from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
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
    
    def create_applicant(self, applicant_data: Dict) -> Optional[ApplicantProfile]:
        try:
            with self.get_session() as session:
                applicant = ApplicantProfile(
                    first_name=applicant_data.get('first_name'),  # Fixed: added quotes
                    last_name=applicant_data.get('last_name'),    # Fixed: added quotes
                    date_of_birth=applicant_data.get('date_of_birth'),  # Fixed: added quotes
                    address=applicant_data.get('address'),        # Fixed: added quotes
                    phone_number=applicant_data.get('phone_number')  # Fixed: .get() instead of ()
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
      
    def delete_applicant(self, applicant_id: int) -> bool:
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
        try:
            with self.get_session() as session:
                count = session.query(ApplicantProfile).count()
                return count
        except SQLAlchemyError as e:
            logger.error(f"Error getting applicants count: {str(e)}")
            return 0

class ApplicationRepository(BaseRepository):
    
    def create_application(self, application_data: Dict) -> Optional[ApplicationDetail]:
        try:
            with self.get_session() as session:
                application = ApplicationDetail(
                    applicant_id=application_data.get('applicant_id'),
                    cv_path=application_data.get('cv_path'),
                    application_role=application_data.get('application_role')
                )
                session.add(application)
                session.flush()
                session.refresh(application)
                logger.info(f"Created application: {application.application_role} (ID: {application.application_id})")  # Fixed: removed references to non-existent attributes
                return application
        except SQLAlchemyError as e:
            logger.error(f"Error creating application: {str(e)}")
            return None
    
    def get_application_by_id(self, application_id: int) -> Optional[ApplicationDetail]:
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
        try:
            with self.get_session() as session:
                applications = session.query(ApplicationDetail).filter(
                    ApplicationDetail.applicant_id == applicant_id
                ).order_by(ApplicationDetail.detail_id.desc()).all()  # Fixed: used existing field
                return applications
        except SQLAlchemyError as e:
            logger.error(f"Error getting applications for applicant {applicant_id}: {str(e)}")
            return []
    
    def get_all_applications(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ApplicationDetail]:
        try:
            with self.get_session() as session:
                query = session.query(ApplicationDetail).order_by(ApplicationDetail.detail_id.desc())  # Fixed: used existing field
                
                if offset:
                    query = query.offset(offset)
                if limit:
                    query = query.limit(limit)
                
                applications = query.all()
                return applications
        except SQLAlchemyError as e:
            logger.error(f"Error getting all applications: {str(e)}")
            return []
   
    def delete_application(self, application_id: int) -> bool:
        try:
            with self.get_session() as session:
                application = session.query(ApplicationDetail).filter(
                    ApplicationDetail.detail_id == application_id  # Fixed: used correct field name
                ).first()
                
                if not application:
                    logger.warning(f"Application with ID {application_id} not found")
                    return False
                
                role = application.application_role
                session.delete(application)
                logger.info(f"Deleted application: {role} (ID: {application_id})")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting application {application_id}: {str(e)}")
            return False

    def get_applications_count(self) -> int:
        try:
            with self.get_session() as session:
                count = session.query(ApplicationDetail).count()
                return count
        except SQLAlchemyError as e:
            logger.error(f"Error getting applications count: {str(e)}")
            return 0  # Fixed: added missing return statement