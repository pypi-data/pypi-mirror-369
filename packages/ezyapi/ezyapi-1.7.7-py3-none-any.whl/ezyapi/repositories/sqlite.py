import sqlite3
import inflect
from typing import Type, List, Optional, Dict, Any, Tuple

from ezyapi.repositories.base import EzyRepository, T
from ezyapi.filters import Not, LessThan, LessThanOrEqual, MoreThan, MoreThanOrEqual
from ezyapi.filters import Equal, Like, ILike, Between, In, IsNull

class SQLiteRepository(EzyRepository[T]):    
    def __init__(self, db_path: str, entity_class: Type[T]):
        self.db_path = db_path
        self.entity_class = entity_class
        self.table_name = self._get_table_name(entity_class)
        self._ensure_table_exists()
        
    def _get_table_name(self, entity_class: Type[T]) -> str:
        p = inflect.engine()
        name = entity_class.__name__
        if name.endswith("Entity"):
            name = name[:-6]
        return p.plural(name.lower())
        
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def _ensure_table_exists(self):
        entity_instance = self.entity_class()
        columns = []
        
        for attr_name, attr_value in entity_instance.__dict__.items():
            if attr_name.startswith('_'):
                continue
                
            attr_type = type(attr_value) if attr_value is not None else str
            sql_type = "TEXT"
            
            if attr_type == int:
                sql_type = "INTEGER"
            elif attr_type == float:
                sql_type = "REAL"
            elif attr_type == bool:
                sql_type = "INTEGER"
                
            if attr_name == 'id':
                columns.append(f"{attr_name} INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                columns.append(f"{attr_name} {sql_type}")
                
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(columns)});"
        
        with self._get_conn() as conn:
            conn.execute(create_table_sql)
    
    async def find(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                  select: Optional[List[str]] = None, 
                  relations: Optional[Dict[str, Any]] = None, 
                  order: Optional[Dict[str, str]] = None, 
                  skip: Optional[int] = None, 
                  take: Optional[int] = None) -> List[T]:
        fields = ', '.join(select) if select else '*'
        query = f"SELECT {fields} FROM {self.table_name}"
        values = []
        
        if where:
            if isinstance(where, list):
                or_conditions = []
                for cond in where:
                    parts, vals = self._build_where_clause(cond)
                    or_conditions.append(f"({' AND '.join(parts)})")
                    values.extend(vals)
                query += f" WHERE {' OR '.join(or_conditions)}"
            else:
                where_parts, vals = self._build_where_clause(where)
                query += f" WHERE {' AND '.join(where_parts)}"
                values.extend(vals)
        
        if order:
            order_clause = ', '.join(f"{k} {v}" for k, v in order.items())
            query += f" ORDER BY {order_clause}"
        
        if skip is not None and take is not None:
            query += f" LIMIT {take} OFFSET {skip}"
        elif take is not None:
            query += f" LIMIT {take}"
        elif skip is not None:
            query += f" OFFSET {skip}"
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    async def find_one(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                      select: Optional[List[str]] = None, 
                      relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
        fields = ', '.join(select) if select else '*'
        query = f"SELECT {fields} FROM {self.table_name}"
        values = []
        
        if where:
            if isinstance(where, list):
                or_conditions = []
                for cond in where:
                    parts, vals = self._build_where_clause(cond)
                    or_conditions.append(f"({' AND '.join(parts)})")
                    values.extend(vals)
                query += f" WHERE {' OR '.join(or_conditions)}"
            else:
                where_parts, vals = self._build_where_clause(where)
                query += f" WHERE {' AND '.join(where_parts)}"
                values.extend(vals)
                
        query += " LIMIT 1"
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None
    
    async def save(self, entity: T) -> T:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            attrs = {k: v for k, v in entity.__dict__.items() if not k.startswith('_')}
            
            if getattr(entity, 'id', None) is None:
                columns = ', '.join(k for k in attrs.keys() if k != 'id')
                placeholders = ', '.join('?' for _ in range(len(attrs) - (1 if 'id' in attrs else 0)))
                values = [v for k, v in attrs.items() if k != 'id']
                
                query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders});"
                cursor.execute(query, values)
                setattr(entity, 'id', cursor.lastrowid)
            else:
                set_clause = ', '.join(f"{k} = ?" for k in attrs.keys() if k != 'id')
                values = [v for k, v in attrs.items() if k != 'id']
                values.append(attrs.get('id'))
                
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?;"
                cursor.execute(query, values)
                
            return entity
    
    async def delete(self, id: int) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            query = f"DELETE FROM {self.table_name} WHERE id = ?;"
            cursor.execute(query, (id,))
            return cursor.rowcount > 0
    
    def _row_to_entity(self, row) -> T:
        if row is None:
            return None
            
        entity = self.entity_class()
        
        for key in row.keys():
            setattr(entity, key, row[key])
            
        return entity
    
    def _build_where_clause(self, conditions: Dict[str, Any]) -> Tuple[List[str], List[Any]]:
        where_parts = []
        values = []
        
        for key, value in conditions.items():
            if isinstance(value, Not):
                where_parts.append(f"{key} != ?")
                values.append(value.value)
            elif isinstance(value, LessThan):
                where_parts.append(f"{key} < ?")
                values.append(value.value)
            elif isinstance(value, LessThanOrEqual):
                where_parts.append(f"{key} <= ?")
                values.append(value.value)
            elif isinstance(value, MoreThan):
                where_parts.append(f"{key} > ?")
                values.append(value.value)
            elif isinstance(value, MoreThanOrEqual):
                where_parts.append(f"{key} >= ?")
                values.append(value.value)
            elif isinstance(value, Equal):
                where_parts.append(f"{key} = ?")
                values.append(value.value)
            elif isinstance(value, Like):
                where_parts.append(f"{key} LIKE ?")
                values.append(value.value)
            elif isinstance(value, ILike):
                where_parts.append(f"{key} LIKE ?")
                values.append(value.value)
            elif isinstance(value, Between):
                where_parts.append(f"{key} BETWEEN ? AND ?")
                values.extend([value.min, value.max])
            elif isinstance(value, In):
                placeholders = ', '.join('?' for _ in value.values)
                where_parts.append(f"{key} IN ({placeholders})")
                values.extend(value.values)
            elif isinstance(value, IsNull):
                where_parts.append(f"{key} IS NULL")
            else:
                where_parts.append(f"{key} = ?")
                values.append(value)
                
        return where_parts, values