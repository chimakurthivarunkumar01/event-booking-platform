from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import TypeVar, Generic, List, Optional, Type
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def create(self, obj_in: dict) -> T:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Created {self.model.__name__} with id {db_obj.id}")
        return db_obj
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by id"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 10) -> tuple[List[T], int]:
        """Get all records with pagination"""
        query = self.db.query(self.model)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def update(self, id: int, obj_in: dict) -> Optional[T]:
        """Update a record"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None
        
        for key, value in obj_in.items():
            if value is not None:
                setattr(db_obj, key, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Updated {self.model.__name__} with id {id}")
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Delete a record"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        logger.info(f"Deleted {self.model.__name__} with id {id}")
        return True
    
    def flush(self):
        """Flush pending changes"""
        self.db.flush()
    
    def commit(self):
        """Commit transaction"""
        self.db.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.db.rollback()
