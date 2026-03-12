import logging
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId, errors as bson_errors

logger = logging.getLogger(__name__)

# Generic type variable for Pydantic models
ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    async def get(self, db: Any, id: str) -> Optional[ModelType]:
        try:
            object_id = ObjectId(id)
        except (bson_errors.InvalidId, ValueError) as e:
            raise ValueError(f"Invalid ID format: {id}") from e
        
        try:
            document = await db[self.collection_name].find_one({"_id": object_id})
            return self.model_class(**document) if document else None
        except PyMongoError as e:
            logger.error(f"Error getting document {id} from {self.collection_name}: {e}")
            raise

    async def get_multi(
        self, db: Any, skip: int = 0, limit: int = 100,
        filter_query: Optional[Dict[str, Any]] = None,
        sort_query: Optional[List[tuple]] = None
    ) -> List[ModelType]:
        if filter_query is None:
            filter_query = {}
        if sort_query is None:
            sort_query = [("created_at", -1)]
        
        try:
            cursor = db[self.collection_name].find(filter_query).sort(sort_query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            return [self.model_class(**doc) for doc in documents]
        except PyMongoError as e:
            logger.error(f"Error getting multiple documents from {self.collection_name}: {e}")
            raise

    async def create(self, db: Any, obj_in: ModelType) -> ModelType:
        try:
            obj_data = obj_in.dict()
            current_time = datetime.utcnow()
            obj_data["created_at"] = current_time
            obj_data["updated_at"] = current_time
            
            result = await db[self.collection_name].insert_one(obj_data)
            created_doc = await db[self.collection_name].find_one({"_id": result.inserted_id})
            if not created_doc:
                raise PyMongoError("Failed to retrieve created document")
            
            return self.model_class(**created_doc)
        except DuplicateKeyError:
            raise
        except PyMongoError as e:
            logger.error(f"Error creating document in {self.collection_name}: {e}")
            raise

    async def update(
        self, db: Any, id: str, obj_in: ModelType
    ) -> Optional[ModelType]:
        try:
            object_id = ObjectId(id)
        except (bson_errors.InvalidId, ValueError) as e:
            raise ValueError(f"Invalid ID format: {id}") from e
        
        try:
            update_data = obj_in.dict(exclude_unset=True)
            
            if not update_data:
                return await self.get(db, id)
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": object_id}, {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_doc = await db[self.collection_name].find_one({"_id": object_id})
                return self.model_class(**updated_doc) if updated_doc else None
            
            return None
        except DuplicateKeyError:
            raise
        except PyMongoError as e:
            logger.error(f"Error updating document {id} in {self.collection_name}: {e}")
            raise

    async def delete(self, db: Any, id: str) -> bool:
        try:
            object_id = ObjectId(id)
        except (bson_errors.InvalidId, ValueError) as e:
            raise ValueError(f"Invalid ID format: {id}") from e
        
        try:
            result = await db[self.collection_name].delete_one({"_id": object_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Error deleting document {id} from {self.collection_name}: {e}")
            raise

    async def count(self, db: Any, filter_query: Optional[Dict[str, Any]] = None) -> int:
        if filter_query is None:
            filter_query = {}
        
        try:
            count = await db[self.collection_name].count_documents(filter_query)
            return int(count)
        except PyMongoError as e:
            logger.error(f"Error counting documents in {self.collection_name}: {e}")
            raise

    async def exists(self, db: Any, filter_query: Dict[str, Any]) -> bool:
        try:
            count = await db[self.collection_name].count_documents(filter_query, limit=1)
            return bool(count > 0)
        except PyMongoError as e:
            logger.error(f"Error checking document existence in {self.collection_name}: {e}")
            raise

    async def get_by_filter(
        self, db: Any, filter_query: Dict[str, Any],
        sort_query: Optional[List[tuple]] = None
    ) -> Optional[ModelType]:
        try:
            if sort_query is None:
                cursor = db[self.collection_name].find(filter_query).limit(1)
            else:
                cursor = db[self.collection_name].find(filter_query).sort(sort_query).limit(1)
            
            document = await cursor.to_list(length=1)
            return self.model_class(**document[0]) if document else None
        except PyMongoError as e:
            logger.error(f"Error getting document by filter in {self.collection_name}: {e}")
            raise

    @property
    def model_class(self) -> Type[ModelType]:
        raise NotImplementedError("Subclasses must implement model_class property")
