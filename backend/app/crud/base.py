import logging
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId, errors as bson_errors

logger = logging.getLogger(__name__)

# Generic type variables for CRUD operations
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD base class for MongoDB operations.
    
    Provides common database operations for any Pydantic model.
    All operations are async and include proper error handling.
    """
    
    def __init__(self, collection_name: str):
        """
        Initialize CRUD base class.
        
        Args:
            collection_name: Name of the MongoDB collection
        """
        self.collection_name = collection_name

    async def get(self, db: AsyncIOMotorDatabase, id: str) -> Optional[ModelType]:
        """
        Get a single document by ID.
        
        Args:
            db: MongoDB database instance
            id: Document ID string
            
        Returns:
            Model instance if found, None otherwise
            
        Raises:
            ValueError: If ID format is invalid
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(id)
        except (bson_errors.InvalidId, ValueError) as e:
            logger.warning(f"Invalid ObjectId format: {id}")
            raise ValueError(f"Invalid ID format: {id}") from e
        
        try:
            document = await db[self.collection_name].find_one({"_id": object_id})
            if document:
                logger.debug(f"Document found in {self.collection_name}: {id}")
                return self.model_class(**document)
            logger.debug(f"Document not found in {self.collection_name}: {id}")
            return None
        except PyMongoError as e:
            logger.error(f"Error getting document {id} from {self.collection_name}: {e}")
            raise

    async def get_multi(
        self,
        db: AsyncIOMotorDatabase,
        skip: int = 0,
        limit: int = 100,
        filter_query: Optional[Dict[str, Any]] = None,
        sort_query: Optional[List[tuple]] = None
    ) -> List[ModelType]:
        """
        Get multiple documents with pagination and filtering.
        
        Args:
            db: MongoDB database instance
            skip: Number of documents to skip (pagination)
            limit: Maximum number of documents to return
            filter_query: MongoDB filter query
            sort_query: Sort specification (e.g., [("created_at", -1)])
            
        Returns:
            List of model instances
        """
        if filter_query is None:
            filter_query = {}
        
        if sort_query is None:
            sort_query = [("created_at", -1)]  # Default sort by created_at descending
        
        try:
            cursor = db[self.collection_name].find(filter_query).sort(sort_query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            logger.debug(f"Retrieved {len(documents)} documents from {self.collection_name}")
            return [self.model_class(**doc) for doc in documents]
        except PyMongoError as e:
            logger.error(f"Error getting multiple documents from {self.collection_name}: {e}")
            raise

    async def create(self, db: AsyncIOMotorDatabase, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new document.
        
        Args:
            db: MongoDB database instance
            obj_in: Pydantic model with creation data
            
        Returns:
            Created model instance
            
        Raises:
            DuplicateKeyError: If document with unique key already exists
        """
        try:
            # Convert Pydantic model to dict
            obj_data = obj_in.dict()
            
            # Add timestamps
            current_time = datetime.utcnow()
            obj_data["created_at"] = current_time
            obj_data["updated_at"] = current_time
            
            # Insert document
            result = await db[self.collection_name].insert_one(obj_data)
            
            # Retrieve and return created document
            created_doc = await db[self.collection_name].find_one({"_id": result.inserted_id})
            if not created_doc:
                raise PyMongoError("Failed to retrieve created document")
            
            logger.info(f"Created document in {self.collection_name}: {result.inserted_id}")
            return self.model_class(**created_doc)
            
        except DuplicateKeyError as e:
            logger.warning(f"Duplicate key error in {self.collection_name}: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Error creating document in {self.collection_name}: {e}")
            raise

    async def update(
        self,
        db: AsyncIOMotorDatabase,
        id: str,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Update a document by ID.
        
        Args:
            db: MongoDB database instance
            id: Document ID string
            obj_in: Update data (Pydantic model or dict)
            
        Returns:
            Updated model instance if found, None otherwise
            
        Raises:
            ValueError: If ID format is invalid
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(id)
        except (bson_errors.InvalidId, ValueError) as e:
            logger.warning(f"Invalid ObjectId format: {id}")
            raise ValueError(f"Invalid ID format: {id}") from e
        
        try:
            # Prepare update data
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                # Convert Pydantic model to dict, excluding unset fields
                update_data = obj_in.dict(exclude_unset=True)
            
            if not update_data:
                logger.warning(f"No update data provided for document {id}")
                return await self.get(db, id)
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update document
            result = await db[self.collection_name].update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Retrieve and return updated document
                updated_doc = await db[self.collection_name].find_one({"_id": object_id})
                if updated_doc:
                    logger.info(f"Updated document in {self.collection_name}: {id}")
                    return self.model_class(**updated_doc)
            
            logger.debug(f"No document updated in {self.collection_name}: {id}")
            return None
            
        except DuplicateKeyError as e:
            logger.warning(f"Duplicate key error during update in {self.collection_name}: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Error updating document {id} in {self.collection_name}: {e}")
            raise

    async def delete(self, db: AsyncIOMotorDatabase, id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            db: MongoDB database instance
            id: Document ID string
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If ID format is invalid
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(id)
        except (bson_errors.InvalidId, ValueError) as e:
            logger.warning(f"Invalid ObjectId format: {id}")
            raise ValueError(f"Invalid ID format: {id}") from e
        
        try:
            result = await db[self.collection_name].delete_one({"_id": object_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted document from {self.collection_name}: {id}")
                return True
            else:
                logger.debug(f"Document not found for deletion in {self.collection_name}: {id}")
                return False
                
        except PyMongoError as e:
            logger.error(f"Error deleting document {id} from {self.collection_name}: {e}")
            raise

    async def count(self, db: AsyncIOMotorDatabase, filter_query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents matching filter.
        
        Args:
            db: MongoDB database instance
            filter_query: MongoDB filter query
            
        Returns:
            Number of matching documents
        """
        if filter_query is None:
            filter_query = {}
        
        try:
            count = await db[self.collection_name].count_documents(filter_query)
            logger.debug(f"Count in {self.collection_name}: {count} documents")
            return count
        except PyMongoError as e:
            logger.error(f"Error counting documents in {self.collection_name}: {e}")
            raise

    async def exists(self, db: AsyncIOMotorDatabase, filter_query: Dict[str, Any]) -> bool:
        """
        Check if document exists matching filter.
        
        Args:
            db: MongoDB database instance
            filter_query: MongoDB filter query
            
        Returns:
            True if document exists, False otherwise
        """
        try:
            # Use count_documents with limit=1 for efficiency
            count = await db[self.collection_name].count_documents(filter_query, limit=1)
            exists = count > 0
            logger.debug(f"Document exists in {self.collection_name}: {exists}")
            return exists
        except PyMongoError as e:
            logger.error(f"Error checking document existence in {self.collection_name}: {e}")
            raise

    async def get_by_filter(
        self,
        db: AsyncIOMotorDatabase,
        filter_query: Dict[str, Any],
        sort_query: Optional[List[tuple]] = None
    ) -> Optional[ModelType]:
        """
        Get a single document matching filter.
        
        Args:
            db: MongoDB database instance
            filter_query: MongoDB filter query
            sort_query: Sort specification
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            if sort_query is None:
                cursor = db[self.collection_name].find(filter_query).limit(1)
            else:
                cursor = db[self.collection_name].find(filter_query).sort(sort_query).limit(1)
            
            document = await cursor.to_list(length=1)
            if document:
                logger.debug(f"Document found in {self.collection_name} with filter: {filter_query}")
                return self.model_class(**document[0])
            return None
        except PyMongoError as e:
            logger.error(f"Error getting document by filter in {self.collection_name}: {e}")
            raise

    @property
    def model_class(self) -> Type[ModelType]:
        """
        Get the model class. This should be overridden by subclasses.
        
        Returns:
            Model class type
        """
        raise NotImplementedError("Subclasses must implement model_class property")
