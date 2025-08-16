#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import json
import py_compile
import threading
import time
import re
import requests
from tqdm import tqdm

def get_version():
    setup_path = os.path.join(os.path.dirname(__file__), "../ezyapi/__init__.py")
    try:
        with open(setup_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Warning: Could not read version from setup.py: {e}", file=sys.stderr)
    
    return "0.0.7"

CLI_VERSION = get_version()

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_logo():
    logo = f"""{CYAN}
 _______  ________  ____    ____         ___      .______    __  
|   ____||       /  \   \  /   /        /   \     |   _  \  |  | 
|  |__   `---/  /    \   \/   /        /  ^  \    |  |_)  | |  | 
|   __|     /  /      \_    _/        /  /_\  \   |   ___/  |  | 
|  |____   /  /----.    |  |         /  _____  \  |  |      |  | 
|_______| /________|    |__|        /__/     \__\ | _|      |__| 

         {BOLD}EZY CLI v{CLI_VERSION}{RESET}
"""
    print(logo)

def print_create_message(filepath):
    try:
        size = os.path.getsize(filepath)
    except Exception:
        size = "?"
    print(f"{GREEN}CREATE {filepath} ({size} bytes){RESET}")

def update_dependencies_json(modules_path, json_path):
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--path", modules_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"{RED}Failed to get installed packages.{RESET}", file=sys.stderr)
        return
    installed_deps = {}
    for line in result.stdout.splitlines():
        if "==" in line:
            pkg, ver = line.split("==", 1)
            installed_deps[pkg.lower()] = ver.strip()
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"{RED}Error reading {json_path}: {e}{RESET}", file=sys.stderr)
        return
    config["dependencies"] = installed_deps
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"{GREEN}ezy.json dependencies updated with installed package versions.{RESET}")

def spinner_task(stop_event):
    spinner_chars = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        print(f"\r{YELLOW}✔ Installation in progress... {spinner_chars[idx % len(spinner_chars)]}{RESET}", end="", flush=True)
        time.sleep(0.1)
        idx += 1
    print(f"\r{GREEN}✔ Dependencies installed successfully.            {RESET}")

def update_main_for_service(name):
    main_path = os.path.join(os.getcwd(), "main.py")
    if not os.path.exists(main_path):
        return
    service_import = f"from {name.lower()}.{name.lower()}_service import {name.capitalize()}Service"
    service_add = f"    app.add_service({name.capitalize()}Service)"
    try:
        with open(main_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"{RED}Error reading main.py: {e}{RESET}", file=sys.stderr)
        return

    import_exists = any(service_import in line for line in lines)
    if not import_exists:
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from") or line.startswith("import"):
                insert_idx = i + 1
            else:
                break
        lines.insert(insert_idx, service_import + "\n")
    
    add_exists = any(service_add.strip() in line.strip() for line in lines)
    if not add_exists:
        for i, line in enumerate(lines):
            if "app.run(" in line:
                lines.insert(i, service_add + "\n")
                break

    try:
        with open(main_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"{GREEN}Updated main.py with {name.capitalize()}Service.{RESET}")
    except Exception as e:
        print(f"{RED}Error updating main.py: {e}{RESET}", file=sys.stderr)

def generate_fields_with_ai(resource_name):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"{RED}Error: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.{RESET}", file=sys.stderr)
        return None

    prompt = f"Generate a JSON object describing the fields for a {resource_name} entity in a web application. The JSON should have field names as keys and their types as values, like {{'field1': 'type1', 'field2': 'type2'}}. Types should be Python types like 'str', 'int', 'float', 'bool', etc. Provide only the JSON object without additional text."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        generated_text = result['candidates'][0]['content']['parts'][0]['text']
        json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            fields = json.loads(json_str)
            return fields
        else:
            print(f"{RED}Error: Could not find JSON in AI response.{RESET}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"{RED}Error generating fields with AI: {e}{RESET}", file=sys.stderr)
        return None


def new_project(project_name):
    project_path = os.path.join(os.getcwd(), project_name)
    if os.path.exists(project_path):
        print(f"{RED}Error: Project '{project_name}' already exists.{RESET}", file=sys.stderr)
        sys.exit(1)
    print(f"{YELLOW}✨  We will scaffold your app in a few seconds...{RESET}\n")
    os.makedirs(project_path)
    os.makedirs(os.path.join(project_path, "test"))
    os.makedirs(os.path.join(project_path, "ezy_modules"))
    gitignore_path = os.path.join(project_path, ".gitignore")
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write("""# Created by https://www.toptal.com/developers/gitignore/api/intellij,visualstudiocode,python,git
# Edit at https://www.toptal.com/developers/gitignore?templates=intellij,visualstudiocode,python,git

### Git ###
# Created by git for backups. To disable backups in Git:
# $ git config --global mergetool.keepBackup false
*.orig

# Created by git when using merge tools for conflicts
*.BACKUP.*
*.BASE.*
*.LOCAL.*
*.REMOTE.*
*_BACKUP_*.txt
*_BASE_*.txt
*_LOCAL_*.txt
*_REMOTE_*.txt

ezy_modules/

### Intellij ###
# Covers JetBrains IDEs: IntelliJ, RubyMine, PhpStorm, AppCode, PyCharm, CLion, Android Studio, WebStorm and Rider
# Reference: https://intellij-support.jetbrains.com/hc/en-us/articles/206544839

# User-specific stuff
.idea/**/workspace.xml
.idea/**/tasks.xml
.idea/**/usage.statistics.xml
.idea/**/dictionaries
.idea/**/shelf

# AWS User-specific
.idea/**/aws.xml

# Generated files
.idea/**/contentModel.xml

# Sensitive or high-churn files
.idea/**/dataSources/
.idea/**/dataSources.ids
.idea/**/dataSources.local.xml
.idea/**/sqlDataSources.xml
.idea/**/dynamic.xml
.idea/**/uiDesigner.xml
.idea/**/dbnavigator.xml

# Gradle
.idea/**/gradle.xml
.idea/**/libraries

# Gradle and Maven with auto-import
# When using Gradle or Maven with auto-import, you should exclude module files,
# since they will be recreated, and may cause churn.  Uncomment if using
# auto-import.
# .idea/artifacts
# .idea/compiler.xml
# .idea/jarRepositories.xml
# .idea/modules.xml
# .idea/*.iml
# .idea/modules
# *.iml

# CMake
cmake-build-*/

# Mongo Explorer plugin
.idea/**/mongoSettings.xml

# File-based project format
*.iws

# IntelliJ
out/

# mpeltonen/sbt-idea plugin
.idea_modules/

# JIRA plugin
atlassian-ide-plugin.xml

# Cursive Clojure plugin
.idea/replstate.xml

# SonarLint plugin
.idea/sonarlint/

# Crashlytics plugin (for Android Studio and IntelliJ)
com_crashlytics_export_strings.xml
crashlytics.properties
crashlytics-build.properties
fabric.properties

# Editor-based Rest Client
.idea/httpRequests

# Android studio 3.1+ serialized cache file
.idea/caches/build_file_checksums.ser

### Intellij Patch ###
# Comment Reason: https://github.com/joeblau/gitignore.io/issues/186#issuecomment-215987721

# *.iml
# modules.xml
# .idea/misc.xml
# *.ipr

# Sonarlint plugin
# https://plugins.jetbrains.com/plugin/7973-sonarlint
.idea/**/sonarlint/

# SonarQube Plugin
# https://plugins.jetbrains.com/plugin/7238-sonarqube-community-plugin
.idea/**/sonarIssues.xml

# Markdown Navigator plugin
# https://plugins.jetbrains.com/plugin/7896-markdown-navigator-enhanced
.idea/**/markdown-navigator.xml
.idea/**/markdown-navigator-enh.xml
.idea/**/markdown-navigator/

# Cache file creation bug
# See https://youtrack.jetbrains.com/issue/JBR-2257
.idea/$CACHE_FILE$

# CodeStream plugin
# https://plugins.jetbrains.com/plugin/12206-codestream
.idea/codestream.xml

# Azure Toolkit for IntelliJ plugin
# https://plugins.jetbrains.com/plugin/8053-azure-toolkit-for-intellij
.idea/**/azureSettings.xml

### Python ###
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
# .python-version

# pipenv
#Pipfile.lock

# poetry
#poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#.idea/

### Python Patch ###
poetry.toml
.ruff_cache/
pyrightconfig.json

### VisualStudioCode ###
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
!.vscode/*.code-snippets

.history/
*.vsix

### VisualStudioCode Patch ###
.history
.ionide
""")
    print_create_message(gitignore_path)
    default_packages = [
        "annotated-types", "anyio", "click", "dnspython", "fastapi", "h11",
        "idna", "inflect", "more-itertools", "motor", "psycopg2", "pydantic",
        "pydantic_core", "pymongo", "PyMySQL", "sniffio", "starlette",
        "typeguard", "typing_extensions", "uvicorn", "pytest"
    ]
    ezy_json_path = os.path.join(project_path, "ezy.json")
    ezy_json_content = {
        "name": project_name,
        "version": "0.1.0",
        "scripts": {
            "start": "python3 main.py",
            "dev": "python3 main.py --dev"
        },
        "dependencies": {pkg: "latest" for pkg in default_packages}
    }
    with open(ezy_json_path, "w", encoding="utf-8") as f:
        json.dump(ezy_json_content, f, indent=2)
    print_create_message(ezy_json_path)
    main_py_path = os.path.join(project_path, "main.py")
    main_py_content = """from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from app_service import AppService

if __name__ == "__main__":
    app = EzyAPI()
    app.add_service(AppService)
    app.run(port=8000)
"""
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(main_py_content)
    print_create_message(main_py_path)
    app_service_path = os.path.join(project_path, "app_service.py")
    app_service_content = """from ezyapi import EzyService

class AppService(EzyService):
    async def get_app(self) -> str:
        return "Hello, World!"
"""
    with open(app_service_path, "w", encoding="utf-8") as f:
        f.write(app_service_content)
    print_create_message(app_service_path)
    print()
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner_task, args=(stop_event,))
    spinner_thread.start()
    modules_path = os.path.join(project_path, "ezy_modules")
    for pkg in default_packages:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--target", modules_path, pkg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode != 0:
            stop_event.set()
            spinner_thread.join()
            print(f"{RED}Failed to install {pkg}.{RESET}", file=sys.stderr)
            sys.exit(1)
    stop_event.set()
    spinner_thread.join()
    update_dependencies_json(modules_path, ezy_json_path)
    print(f"\n{GREEN}🚀  Successfully created project {project_name}{RESET}")
    print(f"{MAGENTA}👉  Get started with the following commands:{RESET}")
    print(f"   {CYAN}$ cd {project_name}{RESET}")
    print(f"   {CYAN}$ ezy run start{RESET}\n")
    print(f"{YELLOW}Thanks for using EZY CLI 🙏{RESET}")
    print(f"{MAGENTA}Consider supporting our project if you like it!{RESET}\n")

def init_project(project_name=None):
    if project_name is None:
        project_name = os.path.basename(os.getcwd())
    ezy_json_path = os.path.join(os.getcwd(), "ezy.json")
    
    if os.path.exists(ezy_json_path):
        print(f"{RED}Error: ezy.json already exists in this directory.{RESET}", file=sys.stderr)
        sys.exit(1)
    
    ezy_json_content = {
        "name": project_name,
        "version": "0.1.0",
        "scripts": {
            "start": "python3 main.py",
            "dev": "python3 main.py --dev"
        },
        "dependencies": {}
    }
    
    with open(ezy_json_path, "w", encoding="utf-8") as f:
        json.dump(ezy_json_content, f, indent=2)
    
    print_create_message(ezy_json_path)
    print(f"\n{GREEN}🚀  Successfully initialized project {project_name}{RESET}")
    print(f"{MAGENTA}👉  You can now create your main.py and other files.{RESET}")

def generate_resource(name):
    try:
        with open("ezy.json", "r", encoding="utf-8") as f:
            _ = json.load(f)
    except Exception:
        pass
    base_dir = os.getcwd()
    
    root_init = os.path.join(base_dir, "__init__.py")
    if not os.path.exists(root_init):
        with open(root_init, "w", encoding="utf-8") as f:
            f.write("")
        print_create_message(root_init)
    
    resource_dir = os.path.join(base_dir, name.lower())
    if os.path.exists(resource_dir):
        print(f"{RED}Error: Resource folder already exists: {resource_dir}{RESET}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(resource_dir)
    transport = input(f"{YELLOW}What transport layer do you use? [REST API]: {RESET}") or "REST API"
    crud_answer = input(f"{YELLOW}Would you like to generate CRUD entry points? [Yes/No]: {RESET}").strip().lower() or "yes"
    crud = crud_answer in ["yes", "y"]
    
    if crud:
        ai_answer = input(f"{YELLOW}Would you like to use AI to infer the fields for this resource? [Yes/No]: {RESET}").strip().lower() or "no"
        use_ai = ai_answer in ["yes", "y"]
        fields = None
        if use_ai:
            fields = generate_fields_with_ai(name)
        
        with open(os.path.join(resource_dir, "__init__.py"), "w", encoding="utf-8") as f:
            f.write("")
        dto_dir = os.path.join(resource_dir, "dto")
        os.makedirs(dto_dir)
        with open(os.path.join(dto_dir, "__init__.py"), "w", encoding="utf-8") as f:
            f.write("")
        entity_dir = os.path.join(resource_dir, "entity")
        os.makedirs(entity_dir)
        with open(os.path.join(entity_dir, "__init__.py"), "w", encoding="utf-8") as f:
            f.write("")

        entity_path = os.path.join(entity_dir, f"{name.lower()}_entity.py")
        if fields:
            entity_content = f"""from ezyapi.database import EzyEntityBase

class {name.capitalize()}Entity(EzyEntityBase):
"""
            for field, field_type in fields.items():
                entity_content += f"    {field}: {field_type}\n"
            entity_content += "\n"
        else:
            entity_content = f"""from ezyapi.database import EzyEntityBase

class {name.capitalize()}Entity(EzyEntityBase):
    pass
"""
        with open(entity_path, "w", encoding="utf-8") as f:
            f.write(entity_content)
        print_create_message(entity_path)
        create_dto_path = os.path.join(dto_dir, f"{name.lower()}_create_dto.py")
        if fields:
            create_dto_content = f"""from ezyapi import EzyBaseDTO

class {name.capitalize()}CreateDTO(EzyBaseDTO):
"""
            for field, field_type in fields.items():
                if field != "id":
                    create_dto_content += f"    {field}: {field_type}\n"
            create_dto_content += "\n"
        else:
            create_dto_content = f"""from ezyapi import EzyBaseDTO

class {name.capitalize()}CreateDTO(EzyBaseDTO):
    pass
"""
        with open(create_dto_path, "w", encoding="utf-8") as f:
            f.write(create_dto_content)
        print_create_message(create_dto_path)

        update_dto_path = os.path.join(dto_dir, f"{name.lower()}_update_dto.py")
        if fields:
            update_dto_content = f"""from ezyapi import EzyBaseDTO

class {name.capitalize()}UpdateDTO(EzyBaseDTO):
"""
            for field, field_type in fields.items():
                update_dto_content += f"    {field}: {field_type}\n"
            update_dto_content += "\n"
        else:
            update_dto_content = f"""from ezyapi import EzyBaseDTO

class {name.capitalize()}UpdateDTO(EzyBaseDTO):
    pass
"""
        with open(update_dto_path, "w", encoding="utf-8") as f:
            f.write(update_dto_content)
        print_create_message(update_dto_path)

        singular = name.lower()
        plural = name.lower() + 's'
        service_path = os.path.join(resource_dir, f"{singular}_service.py")
        service_content = f"""# Transport layer: {transport}
from ezyapi import EzyService
from {singular}.dto.{singular}_create_dto import {name.capitalize()}CreateDTO
from {singular}.dto.{singular}_update_dto import {name.capitalize()}UpdateDTO
from {singular}.entity.{singular}_entity import {name.capitalize()}Entity

class {name.capitalize()}Service(EzyService):
    async def create_{singular}(self, data: {name.capitalize()}CreateDTO):
        return 'This action adds a new {singular}'

    async def list_{plural}(self):
        return 'This action returns all {plural}'

    async def get_{singular}_by_id(self, id: int):
        return f'This action returns a #{{id}} {singular}'

    async def update_{singular}_by_id(self, id: int, data: {name.capitalize()}UpdateDTO):
        return f'This action updates a #{{id}} {singular}'

    async def delete_{singular}_by_id(self, id: int):
        return f'This action removes a #{{id}} {singular}'
"""
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(service_content)
        print_create_message(service_path)

        test_dir = os.path.join(base_dir, "test")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        test_file_path = os.path.join(test_dir, f"test_{singular}_service.py")
        test_content = f"""import pytest
from {singular}.{singular}_service import {name.capitalize()}Service

class Test{name.capitalize()}Service:
    @pytest.fixture
    def service(self):
        return {name.capitalize()}Service()

    def test_create_{singular}(self, service):
        pass

    def test_list_{plural}(self, service):
        pass

    def test_get_{singular}_by_id(self, service):
        pass

    def test_update_{singular}_by_id(self, service):
        pass

    def test_delete_{singular}_by_id(self, service):
        pass
"""
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        print_create_message(test_file_path)
    else:
        service_path = os.path.join(resource_dir, f"{name.lower()}_service.py")
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(f"""# Transport layer: {transport}
from ezyapi import EzyService

class {name.capitalize()}Service(EzyService):
    pass
""")
        print_create_message(service_path)

    print(f"{GREEN}Resource '{name}' created at: {resource_dir}{RESET}")
    update_main_for_service(name)

def generate_component(component_type, name):
    if component_type == "res":
        generate_resource(name)
    else:
        print(f"{RED}Error: Unsupported type '{component_type}' (currently only 'res' is supported){RESET}", file=sys.stderr)
        sys.exit(1)

def generate_all_or_single(args):
    if not args.args or len(args.args) == 0:
        print(f"{YELLOW}Component Generation Guide:{RESET}")
        print(f"  {CYAN}Example: ezy g res user{RESET}")
        print(f"    - 'res' indicates resource generation and 'user' is the component name.")
        print(f"  Supported types: res")
        sys.exit(0)
    elif len(args.args) == 2:
        component_type = args.args[0]
        name = args.args[1]
        generate_component(component_type, name)
    else:
        print(f"{RED}Error: Incorrect number of arguments. Example: ezy g res user{RESET}", file=sys.stderr)
        sys.exit(1)

def build_project():
    base_dir = os.getcwd()
    errors = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    py_compile.compile(path, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append(f"Syntax error: {path}\n  {e.msg}")
    if errors:
        print(f"{RED}Build failed:{RESET}")
        for err in errors:
            print(err)
        sys.exit(1)
    print(f"{GREEN}Build completed successfully.{RESET}")

def serve_project():
    main_py = os.path.join(os.getcwd(), "main.py")
    if not os.path.exists(main_py):
        print(f"{RED}Error: main.py does not exist.{RESET}", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run([sys.executable, main_py])
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Server stopped.{RESET}")

def test_project():
    test_dir = os.path.join(os.getcwd(), "test")
    if not os.path.exists(test_dir):
        print(f"{RED}Error: 'test' folder does not exist.{RESET}", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run(["pytest", test_dir], check=True)
    except FileNotFoundError:
        print(f"{RED}Error: pytest is not installed. Install it via 'pip install pytest'.{RESET}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"{RED}Error: Issues encountered during testing.{RESET}", file=sys.stderr)
        sys.exit(1)

def lint_project():
    try:
        subprocess.run(["flake8", "."], check=True)
        print(f"{GREEN}Linting completed successfully.{RESET}")
    except FileNotFoundError:
        print(f"{RED}Error: flake8 is not installed. Install it via 'pip install flake8'.{RESET}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"{RED}Error: Linting issues detected.{RESET}", file=sys.stderr)
        sys.exit(1)

def info_project():
    print(f"{CYAN}Ezy CLI Version: {CLI_VERSION}{RESET}")
    print(f"{CYAN}Python Version: {sys.version}{RESET}")
    print(f"{CYAN}Platform: {sys.platform}{RESET}")
    print(f"{CYAN}Current Directory: {os.getcwd()}{RESET}")

def update_cli():
    print(f"{GREEN}Ezy CLI ({CLI_VERSION}) is up-to-date.{RESET}")

def install_dependencies(args):
    config_path = os.path.join(os.getcwd(), "ezy.json")
    if not os.path.exists(config_path):
        print(f"{RED}Error: ezy.json not found. Are you in a project directory?{RESET}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    dependencies = config.get("dependencies", {})
    
    if args.requirements:
        try:
            packages_to_install = {}
            with open(args.requirements, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "==" in line:
                            pkg_name, version = line.split("==", 1)
                            packages_to_install[pkg_name.strip()] = version.strip()
                        else:
                            packages_to_install[line.strip()] = "latest"
            
            config["dependencies"] = packages_to_install
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"{RED}Error reading requirements.txt: {str(e)}{RESET}", file=sys.stderr)
            sys.exit(1)
    elif args.packages:
        packages_to_install = {}
        for pkg in args.packages:
            if "==" in pkg:
                pkg_name, _ = pkg.split("==", 1)
                packages_to_install[pkg_name] = "latest"
            else:
                packages_to_install[pkg] = "latest"
        config["dependencies"] = packages_to_install
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    else:
        packages_to_install = dependencies
    
    if not packages_to_install:
        print(f"{YELLOW}No dependencies to install.{RESET}")
        return
    
    modules_path = os.path.join(os.getcwd(), "ezy_modules")
    if not os.path.exists(modules_path):
        os.makedirs(modules_path)
    
    print(f"{YELLOW}Installing dependencies into ezy_modules...{RESET}")
    
    for pkg, ver in packages_to_install.items():
        print(f"\n{CYAN}Installing {pkg}...{RESET}")
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "--target", modules_path, pkg],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            pbar = tqdm(
                total=100,
                desc=f"{GREEN}Progress{RESET}",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                ncols=80,
                leave=False
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if "Collecting" in output:
                        pbar.update(20)
                    elif "Installing collected packages" in output:
                        pbar.update(30)
                    elif "Successfully installed" in output:
                        pbar.update(50)
            
            pbar.close()
            
            if process.returncode != 0:
                error = process.stderr.read()
                print(f"{RED}Failed to install {pkg}.{RESET}")
                print(f"{RED}Error details:{RESET}")
                print(error)
                sys.exit(1)
            
            print(f"{GREEN}✓ {pkg} installed successfully{RESET}")
            
        except Exception as e:
            print(f"{RED}Error installing {pkg}: {str(e)}{RESET}")
            sys.exit(1)
    
    update_dependencies_json(modules_path, config_path)
    print(f"\n{GREEN}All dependencies installed successfully!{RESET}")

def run_script(args):
    config_path = os.path.join(os.getcwd(), "ezy.json")
    if not os.path.exists(config_path):
        print(f"{RED}Error: ezy.json not found. Are you in a project directory?{RESET}", file=sys.stderr)
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    scripts = config.get("scripts", {})
    if not args.script:
        print(f"{RED}Error: No script name provided. Usage: ezy run <script>{RESET}", file=sys.stderr)
        sys.exit(1)
    script_cmd = scripts.get(args.script)
    if not script_cmd:
        print(f"{RED}Error: Script '{args.script}' not found in ezy.json.{RESET}", file=sys.stderr)
        sys.exit(1)
    
    if hasattr(args, 'extra_args') and args.extra_args:
        script_cmd = script_cmd + " " + " ".join(args.extra_args)
    
    print(f"{GREEN}Running script '{args.script}': {YELLOW}{script_cmd}{RESET}")
    modules_path = os.path.join(os.getcwd(), "ezy_modules")
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    new_pythonpath = modules_path + os.pathsep + current_pythonpath if current_pythonpath else modules_path
    env = os.environ.copy()
    env["PYTHONPATH"] = new_pythonpath
    try:
        subprocess.run(script_cmd, shell=True, env=env)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Script execution interrupted.{RESET}")

def main():
    print_logo()
    parser = argparse.ArgumentParser(prog="ezy", description=f"{BOLD}Ezy CLI - Ezy API project management tool{RESET}")
    subparsers = parser.add_subparsers(dest="command")
    new_parser = subparsers.add_parser("new", help="Create a new Ezy API project")
    new_parser.add_argument("project_name", help="Name of the project")
    new_parser.set_defaults(func=lambda args: new_project(args.project_name))
    generate_parser = subparsers.add_parser("generate", aliases=["g"], help="Generate a component (e.g., 'ezy g res user')")
    generate_parser.add_argument("args", nargs="*", help="Component type and name (e.g., 'res user')")
    generate_parser.set_defaults(func=lambda args: generate_all_or_single(args))
    install_parser = subparsers.add_parser("install", help="Install dependencies into ezy_modules or add new packages")
    install_parser.add_argument("packages", nargs="*", help="Optional: package names to install (e.g., opencv or opencv==4.5.3)")
    install_parser.add_argument("-r", "--requirements", metavar="FILE", help="Path to requirements.txt file")
    install_parser.set_defaults(func=lambda args: install_dependencies(args))
    run_parser = subparsers.add_parser("run", help="Run a script defined in ezy.json (e.g., 'ezy run dev' or 'ezy run start')")
    run_parser.add_argument("script", nargs="?", help="Name of the script to run")
    run_parser.add_argument("extra_args", nargs="*", help="Additional arguments to pass to the script")
    run_parser.set_defaults(func=lambda args: run_script(args))
    build_parser = subparsers.add_parser("build", help="Build the project (syntax check)")
    build_parser.set_defaults(func=lambda args: build_project())
    serve_parser = subparsers.add_parser("serve", help="Start the development server")
    serve_parser.set_defaults(func=lambda args: serve_project())
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.set_defaults(func=lambda args: test_project())
    lint_parser = subparsers.add_parser("lint", help="Run code linting")
    lint_parser.set_defaults(func=lambda args: lint_project())
    info_parser = subparsers.add_parser("info", help="Show CLI and system information")
    info_parser.set_defaults(func=lambda args: info_project())
    update_parser = subparsers.add_parser("update", help="Update the CLI (simulation)")
    update_parser.set_defaults(func=lambda args: update_cli())
    init_parser = subparsers.add_parser("init", help="Initialize a new Ezy project in the current directory")
    init_parser.add_argument("project_name", nargs='?', default=None, help="Name of the project (default: current directory name)")
    init_parser.set_defaults(func=lambda args: init_project(args.project_name))
    
    args, unknown = parser.parse_known_args()
    
    if hasattr(args, 'command') and args.command == 'run' and unknown:
        if not hasattr(args, 'extra_args'):
            args.extra_args = []
        args.extra_args.extend(unknown)
    
    if not args.command: 
        parser.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()




