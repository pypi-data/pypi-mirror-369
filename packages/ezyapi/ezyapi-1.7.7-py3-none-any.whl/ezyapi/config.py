from typing import Type, Optional, Dict, Any

from ezyapi.entity import EzyEntityBase
from ezyapi.repositories.base import EzyRepository

class DatabaseConfig:
    
    def __init__(self, db_type: str = "sqlite", connection_string: str = None, connection_params: dict = None):
        self.db_type = db_type
        self.connection_string = connection_string
        self.connection_params = connection_params or {}
        
        if not connection_string and not connection_params:
            if db_type == "sqlite":
                self.connection_string = ":memory:"
            else:
                raise ValueError(f"Either connection_string or connection_params must be provided for {db_type}")
        
        self._session_factory = None
    
    def get_connection_string(self) -> str:
        if self.connection_string:
            return self.connection_string
            
        if self.db_type == "sqlite":
            return self.connection_params.get("dbname", ":memory:")
        elif self.db_type == "postgresql":
            return f"postgresql://{self.connection_params.get('user', '')}:{self.connection_params.get('password', '')}@{self.connection_params.get('host', 'localhost')}:{self.connection_params.get('port', 5432)}/{self.connection_params.get('dbname', '')}"
        elif self.db_type == "mysql":
            return f"mysql://{self.connection_params.get('user', '')}:{self.connection_params.get('password', '')}@{self.connection_params.get('host', 'localhost')}:{self.connection_params.get('port', 3306)}/{self.connection_params.get('dbname', '')}"
        elif self.db_type == "mongodb":
            auth = f"{self.connection_params.get('user', '')}:{self.connection_params.get('password', '')}@" if self.connection_params.get('user') else ""
            return f"mongodb://{auth}{self.connection_params.get('host', 'localhost')}:{self.connection_params.get('port', 27017)}/{self.connection_params.get('dbname', '')}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def get_repository(self, entity_class: Type[Any]) -> EzyRepository:
        from ezyapi.repositories.sqlite import SQLiteRepository
        from ezyapi.repositories.postgresql import PostgreSQLRepository
        from ezyapi.repositories.mongodb import MongoDBRepository
        from ezyapi.repositories.mysql import MySQLRepository
        
        conn_str = self.get_connection_string()
        
        if self.db_type == "sqlite":
            return SQLiteRepository(conn_str, entity_class)
        elif self.db_type == "postgresql":
            return PostgreSQLRepository(conn_str, entity_class)
        elif self.db_type == "mongodb":
            return MongoDBRepository(conn_str, entity_class)
        elif self.db_type == "mysql":
            return MySQLRepository(conn_str, entity_class)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


def auto_inject_repository(service_class: Any, db_config: DatabaseConfig):
    import sys
    from ezyapi.services.base import EzyService
    
    service_name = service_class.__name__
    entity_class_name = None
    
    if service_name.endswith("Service"):
        entity_name = service_name[:-7]
        entity_class_name = f"{entity_name}Entity"
    
    entity_class = None
    
    for module_name, module in sys.modules.items():
        if hasattr(module, entity_class_name):
            entity_class = getattr(module, entity_class_name)
            break
    
    if entity_class and issubclass(entity_class, EzyEntityBase):
        repository = db_config.get_repository(entity_class)
        return service_class(repository=repository)
    
    return service_class()