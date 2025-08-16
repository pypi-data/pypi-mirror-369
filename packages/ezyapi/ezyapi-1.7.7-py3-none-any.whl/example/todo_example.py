"""
Todo 예시 - Annotated 컬럼 정의 방식 테스트

이 예시는 Annotated 타입을 사용한 컬럼 정의 방식을 보여줍니다.
"""

from typing import Annotated, List
from ezyapi.database import (
    EzyEntityBase, 
    Column, 
    PrimaryColumn, 
    PrimaryGeneratedColumn,
    OneToMany,
    ManyToOne
)

# 기본 Todo 엔티티 (기본 id가 PrimaryGeneratedColumn으로 자동 설정됨)
class TodoEntity(EzyEntityBase):
    def __init__(self, id: int = 0, content: str = "", completed: bool = False):
        self.id = id
        self.content = content
        self.completed = completed

# Annotated를 사용한 PrimaryColumn 예시
class TodoWithCustomPrimaryEntity(EzyEntityBase):
    def __init__(self, id: int = 0, content: str = "", completed: bool = False):
        self.id = id
        self.content = content
        self.completed = completed

    id: Annotated[int, PrimaryColumn()]

# Annotated를 사용한 PrimaryGeneratedColumn 예시  
class TodoWithGeneratedPrimaryEntity(EzyEntityBase):
    def __init__(self, todo_id: int = 0, content: str = "", completed: bool = False):
        self.todo_id = todo_id
        self.content = content
        self.completed = completed

    todo_id: Annotated[int, PrimaryGeneratedColumn(column_type="BIGINT")]

# 다양한 컬럼 타입 예시
class AdvancedTodoEntity(EzyEntityBase):
    def __init__(self, id: int = 0, title: str = "", content: str = "", 
                 priority: int = 1, completed: bool = False, 
                 category_id: int = None):
        self.id = id
        self.title = title
        self.content = content
        self.priority = priority
        self.completed = completed
        self.category_id = category_id

    # 자동 증가 Primary Key
    id: Annotated[int, PrimaryGeneratedColumn()]
    
    # 필수 컬럼 (NOT NULL)
    title: Annotated[str, Column(nullable=False, column_type="VARCHAR(200)")]
    
    # 기본값이 있는 컬럼
    priority: Annotated[int, Column(default=1, column_type="INTEGER")]
    
    # 유니크 컬럼
    slug: Annotated[str, Column(unique=True, column_type="VARCHAR(100)")] = ""

# 관계 설정 예시
class CategoryEntity(EzyEntityBase):
    def __init__(self, id: int = 0, name: str = ""):
        self.id = id
        self.name = name
    
    id: Annotated[int, PrimaryGeneratedColumn()]
    name: Annotated[str, Column(nullable=False, column_type="VARCHAR(100)")]
    
    # 일대다 관계: 하나의 카테고리가 여러 Todo를 가질 수 있음
    todos: Annotated[List['TodoWithCategoryEntity'], OneToMany('TodoWithCategoryEntity', mapped_by='category_id')] = None

class TodoWithCategoryEntity(EzyEntityBase):
    def __init__(self, id: int = 0, content: str = "", completed: bool = False, category_id: int = None):
        self.id = id
        self.content = content
        self.completed = completed
        self.category_id = category_id
    
    id: Annotated[int, PrimaryGeneratedColumn()]
    content: Annotated[str, Column(nullable=False, column_type="TEXT")]
    completed: Annotated[bool, Column(default=False)]
    
    # 외래키
    category_id: Annotated[int, Column(nullable=False)]
    
    # 다대일 관계: 여러 Todo가 하나의 카테고리에 속할 수 있음
    category: Annotated['CategoryEntity', ManyToOne('CategoryEntity', foreign_key='category_id')] = None

def test_entity_metadata():
    """엔티티 메타데이터 테스트"""
    
    print("=== 기본 TodoEntity ===")
    todo = TodoEntity()
    print("Primary Key Info:", todo.get_primary_key_info())
    print("Column Info:", todo.get_column_info())
    print("Relationship Info:", todo.get_relationship_info())
    
    print("\n=== TodoWithCustomPrimaryEntity ===")
    todo_custom = TodoWithCustomPrimaryEntity()
    print("Primary Key Info:", todo_custom.get_primary_key_info())
    print("Column Info:", todo_custom.get_column_info())
    
    print("\n=== TodoWithGeneratedPrimaryEntity ===")
    todo_generated = TodoWithGeneratedPrimaryEntity()
    print("Primary Key Info:", todo_generated.get_primary_key_info())
    print("Column Info:", todo_generated.get_column_info())
    
    print("\n=== AdvancedTodoEntity ===")
    advanced_todo = AdvancedTodoEntity()
    print("Primary Key Info:", advanced_todo.get_primary_key_info())
    print("Column Info:", advanced_todo.get_column_info())
    
    print("\n=== CategoryEntity ===")
    category = CategoryEntity()
    print("Primary Key Info:", category.get_primary_key_info())
    print("Column Info:", category.get_column_info())
    print("Relationship Info:", category.get_relationship_info())
    
    print("\n=== TodoWithCategoryEntity ===")
    todo_with_category = TodoWithCategoryEntity()
    print("Primary Key Info:", todo_with_category.get_primary_key_info())
    print("Column Info:", todo_with_category.get_column_info())
    print("Relationship Info:", todo_with_category.get_relationship_info())

if __name__ == "__main__":
    test_entity_metadata()
