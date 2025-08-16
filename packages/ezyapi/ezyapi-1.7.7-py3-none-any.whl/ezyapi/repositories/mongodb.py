import inflect
from typing import Type, List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

from ezyapi.repositories.base import EzyRepository, T
from ezyapi.filters import Not, LessThan, LessThanOrEqual, MoreThan, MoreThanOrEqual
from ezyapi.filters import Equal, Like, ILike, Between, In, IsNull

class MongoDBRepository(EzyRepository[T]):
    
    def __init__(self, connection_string: str, entity_class: Type[T]):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.get_default_database()
        self.entity_class = entity_class
        self.collection_name = self._get_collection_name(entity_class)
    
    def _get_collection_name(self, entity_class: Type[T]) -> str:
        p = inflect.engine()
        name = entity_class.__name__
        if name.endswith("Entity"):
            name = name[:-6]
        return p.plural(name.lower())
    
    def _build_filter(self, conditions: Dict[str, Any]) -> dict:
        f = {}
        for key, value in conditions.items():
            if isinstance(value, Not):
                f[key] = {"$ne": value.value}
            elif isinstance(value, LessThan):
                f[key] = {"$lt": value.value}
            elif isinstance(value, LessThanOrEqual):
                f[key] = {"$lte": value.value}
            elif isinstance(value, MoreThan):
                f[key] = {"$gt": value.value}
            elif isinstance(value, MoreThanOrEqual):
                f[key] = {"$gte": value.value}
            elif isinstance(value, Equal):
                f[key] = value.value
            elif isinstance(value, Like):
                f[key] = {"$regex": value.value}
            elif isinstance(value, ILike):
                f[key] = {"$regex": value.value, "$options": "i"}
            elif isinstance(value, Between):
                f[key] = {"$gte": value.min, "$lte": value.max}
            elif isinstance(value, In):
                f[key] = {"$in": value.values}
            elif isinstance(value, IsNull):
                f[key] = None
            else:
                f[key] = value
        return f
    
    def _doc_to_entity(self, doc: dict) -> T:
        if doc is None:
            return None
            
        entity = self.entity_class()
        
        for key, value in doc.items():
            if key == "_id":
                setattr(entity, "id", value)
            else:
                setattr(entity, key, value)
                
        return entity
    
    async def find(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                  select: Optional[List[str]] = None, 
                  relations: Optional[Dict[str, Any]] = None, 
                  order: Optional[Dict[str, str]] = None, 
                  skip: Optional[int] = None, 
                  take: Optional[int] = None) -> List[T]:
        collection = self.db[self.collection_name]
        f = {}
        
        if where:
            if isinstance(where, list):
                f = {"$or": [self._build_filter(cond) for cond in where]}
            else:
                f = self._build_filter(where)
        
        projection = None
        if select:
            projection = {field: 1 for field in select}
        
        cursor = collection.find(f, projection)
        
        if order:
            sort_list = [(k, 1 if v.lower() == "asc" else -1) for k, v in order.items()]
            cursor = cursor.sort(sort_list)
        
        if skip:
            cursor = cursor.skip(skip)
        
        if take:
            cursor = cursor.limit(take)
        
        docs = await cursor.to_list(length=take or 100)
        
        return [self._doc_to_entity(doc) for doc in docs]
    
    async def find_one(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                      select: Optional[List[str]] = None, 
                      relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
        collection = self.db[self.collection_name]
        f = {}
        
        if where:
            if isinstance(where, list):
                f = {"$or": [self._build_filter(cond) for cond in where]}
            else:
                f = self._build_filter(where)
        
        projection = None
        if select:
            projection = {field: 1 for field in select}
        
        doc = await collection.find_one(f, projection)
        
        return self._doc_to_entity(doc) if doc else None
    
    async def save(self, entity: T) -> T:
        collection = self.db[self.collection_name]
        data = entity.__dict__.copy()
        
        if data.get("id") is None:
            data.pop("id", None)
            result = await collection.insert_one(data)
            entity.id = result.inserted_id
        else:
            id_val = entity.id
            data.pop("id", None)
            await collection.update_one({"_id": id_val}, {"$set": data})
        
        return entity
    
    async def delete(self, id: int) -> bool:
        collection = self.db[self.collection_name]
        result = await collection.delete_one({"_id": id})
        
        return result.deleted_count > 0