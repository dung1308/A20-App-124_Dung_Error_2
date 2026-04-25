"""
CRM (Customer Relationship Management) system for student profiles.
Manages student data, application status, and advisor notes.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from models import Student

logger = logging.getLogger(__name__)


class CRM:
    """
    CRM system for managing student profiles and application status.
    Backed by PostgreSQL database.
    """
    
    def __init__(self, db: Session):
        """
        Initialize CRM with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get student profile by user ID.
        
        Args:
            user_id: Student identifier
            
        Returns:
            Student profile dict or None if not found
        """
        try:
            student = self.db.query(Student)\
                .filter(Student.user_id == user_id)\
                .first()
            
            if not student:
                logger.debug(f"Student {user_id} not found in CRM")
                return None
            
            return self._to_dict(student)
        except Exception as e:
            logger.error(f"Error retrieving student {user_id}: {e}")
            return None

    def get_or_create(self, user_id: str, name: str = "") -> Dict[str, Any]:
        """
        Get existing student or create new one.
        
        Args:
            user_id: Student identifier
            name: Student name (if creating new)
            
        Returns:
            Student profile dict
        """
        try:
            student = self.db.query(Student)\
                .filter(Student.user_id == user_id)\
                .first()
            
            if student:
                return self._to_dict(student)
            
            # Create new student
            student = Student(
                user_id=user_id,
                name=name or f"Student_{user_id}",
                status="mới tạo"
            )
            self.db.add(student)
            self.db.commit()
            logger.info(f"Created new student profile for {user_id}")
            
            return self._to_dict(student)
        except Exception as e:
            logger.error(f"Error creating student {user_id}: {e}")
            self.db.rollback()
            return {"user_id": user_id, "error": str(e)}

    def update_status(self, user_id: str, status: str) -> bool:
        """
        Update application status.
        
        Args:
            user_id: Student identifier
            status: New status (e.g. "thiếu học bạ", "hồ sơ đầy đủ", "trúng tuyển")
            
        Returns:
            True if updated successfully
        """
        try:
            student = self.db.query(Student)\
                .filter(Student.user_id == user_id)\
                .first()
            
            if not student:
                logger.warning(f"Student {user_id} not found, cannot update status")
                return False
            
            student.status = status
            self.db.commit()
            logger.info(f"Updated status for {user_id} to: {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating status for {user_id}: {e}")
            self.db.rollback()
            return False

    def update_major(self, user_id: str, major: str) -> bool:
        """
        Update intended major.
        
        Args:
            user_id: Student identifier
            major: Major/program name
            
        Returns:
            True if updated successfully
        """
        try:
            student = self.db.query(Student)\
                .filter(Student.user_id == user_id)\
                .first()
            
            if not student:
                return False
            
            student.major = major
            self.db.commit()
            logger.info(f"Updated major for {user_id} to: {major}")
            return True
        except Exception as e:
            logger.error(f"Error updating major for {user_id}: {e}")
            self.db.rollback()
            return False

    def add_metadata(self, user_id: str, key: str, value: Any) -> bool:
        """
        Add custom metadata to student profile.
        
        Args:
            user_id: Student identifier
            key: Metadata key
            value: Metadata value
            
        Returns:
            True if added successfully
        """
        try:
            student = self.db.query(Student)\
                .filter(Student.user_id == user_id)\
                .first()
            
            if not student:
                return False
            
            if student.metadata_json is None:
                student.metadata_json = {}
            
            student.metadata_json[key] = value
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding metadata for {user_id}: {e}")
            self.db.rollback()
            return False

    def search_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find all students with given status.
        Useful for batch processing or reporting.
        
        Args:
            status: Status filter
            limit: Max results to return
            
        Returns:
            List of student profiles
        """
        try:
            students = self.db.query(Student)\
                .filter(Student.status == status)\
                .limit(limit)\
                .all()
            
            return [self._to_dict(s) for s in students]
        except Exception as e:
            logger.error(f"Error searching students by status {status}: {e}")
            return []

    def delete(self, user_id: str) -> bool:
        """
        Delete student record (GDPR right to be forgotten).
        
        Args:
            user_id: Student identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            student = self.db.query(Student)\
                .filter(Student.user_id == user_id)\
                .first()
            
            if not student:
                return False
            
            self.db.delete(student)
            self.db.commit()
            logger.info(f"Deleted student profile for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting student {user_id}: {e}")
            self.db.rollback()
            return False

    @staticmethod
    def _to_dict(student: Student) -> Dict[str, Any]:
        """Convert Student ORM object to dict"""
        return {
            "user_id": student.user_id,
            "name": student.name,
            "email": student.email,
            "phone": student.phone,
            "status": student.status,
            "major": student.major,
            "metadata": student.metadata_json or {},
            "created_at": student.created_at.isoformat() if student.created_at else None,
            "updated_at": student.updated_at.isoformat() if student.updated_at else None
        }
