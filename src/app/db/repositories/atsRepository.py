# db/repository.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime
from contextlib import contextmanager

from ..models import ApplicantProfile, ApplicationDetail, DatabaseConfig
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseRepository:
    """Base repository with common database operations"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.SessionLocal = self.config.get_session_maker()
    
    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()

class ApplicantRepository(BaseRepository):
    """Repository for ApplicantProfile operations"""
    
    def create_applicant(self, applicant_data: Dict) -> Optional[ApplicantProfile]:
        """Create a new applicant profile"""
        try:
            with self.get_session() as session:
                applicant = ApplicantProfile(
                    full_name=applicant_data.get('full_name'),
                    email=applicant_data.get('email'),
                    phone=applicant_data.get('phone'),
                    address=applicant_data.get('address'),
                    date_of_birth=applicant_data.get('date_of_birth')
                )
                session.add(applicant)
                session.flush()  # Get the ID without committing
                session.refresh(applicant)
                logger.info(f"Created applicant: {applicant.full_name} (ID: {applicant.applicant_id})")
                return applicant
        except SQLAlchemyError as e:
            logger.error(f"Error creating applicant: {str(e)}")
            return None
    
    def get_applicant_by_id(self, applicant_id: int) -> Optional[ApplicantProfile]:
        """Get applicant by ID"""
        try:
            with self.get_session() as session:
                applicant = session.query(ApplicantProfile).filter(
                    ApplicantProfile.applicant_id == applicant_id
                ).first()
                return applicant
        except SQLAlchemyError as e:
            logger.error(f"Error getting applicant by ID {applicant_id}: {str(e)}")
            return None
    
    def get_applicant_by_email(self, email: str) -> Optional[ApplicantProfile]:
        """Get applicant by email"""
        try:
            with self.get_session() as session:
                applicant = session.query(ApplicantProfile).filter(
                    ApplicantProfile.email == email
                ).first()
                return applicant
        except SQLAlchemyError as e:
            logger.error(f"Error getting applicant by email {email}: {str(e)}")
            return None
    
    def get_all_applicants(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ApplicantProfile]:
        """Get all applicants with optional pagination"""
        try:
            with self.get_session() as session:
                query = session.query(ApplicantProfile).order_by(ApplicantProfile.created_at.desc())
                
                if offset:
                    query = query.offset(offset)
                if limit:
                    query = query.limit(limit)
                
                applicants = query.all()
                return applicants
        except SQLAlchemyError as e:
            logger.error(f"Error getting all applicants: {str(e)}")
            return []
    
    def update_applicant(self, applicant_id: int, update_data: Dict) -> Optional[ApplicantProfile]:
        """Update applicant profile"""
        try:
            with self.get_session() as session:
                applicant = session.query(ApplicantProfile).filter(
                    ApplicantProfile.applicant_id == applicant_id
                ).first()
                
                if not applicant:
                    logger.warning(f"Applicant with ID {applicant_id} not found")
                    return None
                
                # Update fields if provided
                for field, value in update_data.items():
                    if hasattr(applicant, field) and value is not None:
                        setattr(applicant, field, value)
                
                session.flush()
                session.refresh(applicant)
                logger.info(f"Updated applicant: {applicant.full_name} (ID: {applicant.applicant_id})")
                return applicant
        except SQLAlchemyError as e:
            logger.error(f"Error updating applicant {applicant_id}: {str(e)}")
            return None
    
    def delete_applicant(self, applicant_id: int) -> bool:
        """Delete applicant profile (cascade deletes applications)"""
        try:
            with self.get_session() as session:
                applicant = session.query(ApplicantProfile).filter(
                    ApplicantProfile.applicant_id == applicant_id
                ).first()
                
                if not applicant:
                    logger.warning(f"Applicant with ID {applicant_id} not found")
                    return False
                
                applicant_name = applicant.full_name
                session.delete(applicant)
                logger.info(f"Deleted applicant: {applicant_name} (ID: {applicant_id})")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting applicant {applicant_id}: {str(e)}")
            return False
    
    def search_applicants_by_name(self, name_pattern: str) -> List[ApplicantProfile]:
        """Search applicants by name pattern"""
        try:
            with self.get_session() as session:
                applicants = session.query(ApplicantProfile).filter(
                    ApplicantProfile.full_name.like(f"%{name_pattern}%")
                ).order_by(ApplicantProfile.full_name).all()
                return applicants
        except SQLAlchemyError as e:
            logger.error(f"Error searching applicants by name '{name_pattern}': {str(e)}")
            return []
    
    def get_applicants_count(self) -> int:
        """Get total count of applicants"""
        try:
            with self.get_session() as session:
                count = session.query(ApplicantProfile).count()
                return count
        except SQLAlchemyError as e:
            logger.error(f"Error getting applicants count: {str(e)}")
            return 0

class ApplicationRepository(BaseRepository):
    """Repository for ApplicationDetail operations"""
    
    def create_application(self, application_data: Dict) -> Optional[ApplicationDetail]:
        """Create a new application"""
        try:
            with self.get_session() as session:
                application = ApplicationDetail(
                    applicant_id=application_data.get('applicant_id'),
                    position=application_data.get('position'),
                    company=application_data.get('company'),
                    cv_path=application_data.get('cv_path'),
                    application_date=application_data.get('application_date', date.today()),
                    status=application_data.get('status', 'pending')
                )
                session.add(application)
                session.flush()
                session.refresh(application)
                logger.info(f"Created application: {application.position} at {application.company} (ID: {application.application_id})")
                return application
        except SQLAlchemyError as e:
            logger.error(f"Error creating application: {str(e)}")
            return None
    
    def get_application_by_id(self, application_id: int) -> Optional[ApplicationDetail]:
        """Get application by ID"""
        try:
            with self.get_session() as session:
                application = session.query(ApplicationDetail).filter(
                    ApplicationDetail.application_id == application_id
                ).first()
                return application
        except SQLAlchemyError as e:
            logger.error(f"Error getting application by ID {application_id}: {str(e)}")
            return None
    
    def get_applications_by_applicant(self, applicant_id: int) -> List[ApplicationDetail]:
        """Get all applications for a specific applicant"""
        try:
            with self.get_session() as session:
                applications = session.query(ApplicationDetail).filter(
                    ApplicationDetail.applicant_id == applicant_id
                ).order_by(ApplicationDetail.application_date.desc()).all()
                return applications
        except SQLAlchemyError as e:
            logger.error(f"Error getting applications for applicant {applicant_id}: {str(e)}")
            return []
    
    def get_all_applications(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ApplicationDetail]:
        """Get all applications with optional pagination"""
        try:
            with self.get_session() as session:
                query = session.query(ApplicationDetail).order_by(ApplicationDetail.application_date.desc())
                
                if offset:
                    query = query.offset(offset)
                if limit:
                    query = query.limit(limit)
                
                applications = query.all()
                return applications
        except SQLAlchemyError as e:
            logger.error(f"Error getting all applications: {str(e)}")
            return []
    
    def update_application(self, application_id: int, update_data: Dict) -> Optional[ApplicationDetail]:
        """Update application details"""
        try:
            with self.get_session() as session:
                application = session.query(ApplicationDetail).filter(
                    ApplicationDetail.application_id == application_id
                ).first()
                
                if not application:
                    logger.warning(f"Application with ID {application_id} not found")
                    return None
                
                # Update fields if provided
                for field, value in update_data.items():
                    if hasattr(application, field) and value is not None:
                        setattr(application, field, value)
                
                session.flush()
                session.refresh(application)
                logger.info(f"Updated application: {application.position} (ID: {application.application_id})")
                return application
        except SQLAlchemyError as e:
            logger.error(f"Error updating application {application_id}: {str(e)}")
            return None
    
    def delete_application(self, application_id: int) -> bool:
        """Delete application"""
        try:
            with self.get_session() as session:
                application = session.query(ApplicationDetail).filter(
                    ApplicationDetail.application_id == application_id
                ).first()
                
                if not application:
                    logger.warning(f"Application with ID {application_id} not found")
                    return False
                
                position = application.position
                session.delete(application)
                logger.info(f"Deleted application: {position} (ID: {application_id})")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting application {application_id}: {str(e)}")
            return False
    
    def get_applications_by_status(self, status: str) -> List[ApplicationDetail]:
        """Get applications by status"""
        try:
            with self.get_session() as session:
                applications = session.query(ApplicationDetail).filter(
                    ApplicationDetail.status == status
                ).order_by(ApplicationDetail.application_date.desc()).all()
                return applications
        except SQLAlchemyError as e:
            logger.error(f"Error getting applications by status '{status}': {str(e)}")
            return []
    
    def get_applications_by_position(self, position_pattern: str) -> List[ApplicationDetail]:
        """Search applications by position pattern"""
        try:
            with self.get_session() as session:
                applications = session.query(ApplicationDetail).filter(
                    ApplicationDetail.position.like(f"%{position_pattern}%")
                ).order_by(ApplicationDetail.application_date.desc()).all()
                return applications
        except SQLAlchemyError as e:
            logger.error(f"Error searching applications by position '{position_pattern}': {str(e)}")
            return []
    
    def get_applications_by_company(self, company_pattern: str) -> List[ApplicationDetail]:
        """Search applications by company pattern"""
        try:
            with self.get_session() as session:
                applications = session.query(ApplicationDetail).filter(
                    ApplicationDetail.company.like(f"%{company_pattern}%")
                ).order_by(ApplicationDetail.application_date.desc()).all()
                return applications
        except SQLAlchemyError as e:
            logger.error(f"Error searching applications by company '{company_pattern}': {str(e)}")
            return []
    
    def update_application_status(self, application_id: int, status: str) -> Optional[ApplicationDetail]:
        """Update application status"""
        return self.update_application(application_id, {'status': status})
    
    def get_applications_count(self) -> int:
        """Get total count of applications"""
        try:
            with self.get_session() as session:
                count = session.query(ApplicationDetail).count()
                return count
        except SQLAlchemyError as e:
            logger.error(f"Error getting applications count: {str(e)}")
            return 0