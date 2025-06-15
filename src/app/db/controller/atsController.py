from typing import Dict, List
from datetime import date, datetime
from ..repositories.atsRepository import ApplicantRepository, ApplicationRepository
from ..models import init_database
import logging

logger = logging.getLogger(__name__)

class ATSController:
    
    def __init__(self):
        self.applicant_repo = ApplicantRepository()
        self.application_repo = ApplicationRepository()
        
        try:
            init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
        
    def create_applicant(self, full_name: str, email: str, phone: str = None, 
                        address: str = None, date_of_birth: date = None) -> Dict:
        try:
            existing_applicant = self.applicant_repo.get_applicant_by_email(email)
            if existing_applicant:
                return {
                    'success': False,
                    'message': f'Applicant with email {email} already exists',
                    'data': None
                }
            
            name_parts = full_name.strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            applicant_data = {
                'first_name': first_name,  # Fixed: use actual model fields
                'last_name': last_name,    # Fixed: use actual model fields
                'phone_number': phone,     # Fixed: match model field name
                'address': address,
                'date_of_birth': date_of_birth
            }
            
            applicant = self.applicant_repo.create_applicant(applicant_data)
            
            if applicant:
                return {
                    'success': True,
                    'message': 'Applicant created successfully',
                    'data': applicant.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create applicant',
                    'data': None
                }
        except Exception as e:
            logger.error(f"Error in create_applicant: {str(e)}")
            return {
                'success': False,
                'message': f'Error creating applicant: {str(e)}',
                'data': None
            }
    
    def get_applicant(self, applicant_id: int) -> Dict:
        try:
            applicant = self.applicant_repo.get_applicant_by_id(applicant_id)
            
            if applicant:
                return {
                    'success': True,
                    'message': 'Applicant found',
                    'data': applicant
                }
            else:
                return {
                    'success': False,
                    'message': f'Applicant with ID {applicant_id} not found',
                    'data': None
                }
        except Exception as e:
            logger.error(f"Error in get_applicant: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting applicant: {str(e)}',
                'data': None
            }
    
    def get_applicant_by_email(self, email: str) -> Dict:
        try:
            applicant = self.applicant_repo.get_applicant_by_email(email)
            
            if applicant:
                return {
                    'success': True,
                    'message': 'Applicant found',
                    'data': applicant.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': f'Applicant with email {email} not found',
                    'data': None
                }
        except Exception as e:
            logger.error(f"Error in get_applicant_by_email: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting applicant: {str(e)}',
                'data': None
            }
    
    def get_all_applicants(self, page: int = 1, page_size: int = 50) -> Dict:
        try:
            offset = (page - 1) * page_size
            applicants = self.applicant_repo.get_all_applicants(limit=page_size, offset=offset)
            total_count = self.applicant_repo.get_applicants_count()
            
            return {
                'success': True,
                'message': f'Found {len(applicants)} applicants',
                'data': {
                    'applicants': [applicant.to_dict() for applicant in applicants],
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error in get_all_applicants: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting applicants: {str(e)}',
                'data': None
            }
    
    def search_applicants(self, name_pattern: str) -> Dict:
        try:
            applicants = self.applicant_repo.search_applicants_by_name(name_pattern)
            
            return {
                'success': True,
                'message': f'Found {len(applicants)} applicants matching "{name_pattern}"',
                'data': [applicant.to_dict() for applicant in applicants]
            }
        except Exception as e:
            logger.error(f"Error in search_applicants: {str(e)}")
            return {
                'success': False,
                'message': f'Error searching applicants: {str(e)}',
                'data': None
            }
        
    def create_application(self, applicant_id: int, position: str, company: str = None, 
                          cv_path: str = None, application_date: date = None, 
                          status: str = 'pending') -> Dict:
        try:
            applicant = self.applicant_repo.get_applicant_by_id(applicant_id)
            if not applicant:
                return {
                    'success': False,
                    'message': f'Applicant with ID {applicant_id} not found',
                    'data': None
                }
            
            application_data = {
                'applicant_id': applicant_id,
                'application_role': position,  # Fixed: match model field name
                'cv_path': cv_path or f'/cvs/{applicant_id}_{position.replace(" ", "_")}.pdf'
            }
            
            application = self.application_repo.create_application(application_data)
            
            if application:
                return {
                    'success': True,
                    'message': 'Application created successfully',
                    'data': application.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create application',
                    'data': None
                }
        except Exception as e:
            logger.error(f"Error in create_application: {str(e)}")
            return {
                'success': False,
                'message': f'Error creating application: {str(e)}',
                'data': None
            }
    
    def get_application(self, application_id: int) -> Dict:
        try:
            application = self.application_repo.get_application_by_id(application_id)
            
            if application:
                return {
                    'success': True,
                    'message': 'Application found',
                    'data': application.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': f'Application with ID {application_id} not found',
                    'data': None
                }
        except Exception as e:
            logger.error(f"Error in get_application: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting application: {str(e)}',
                'data': None
            }
    
    def get_applications_by_applicant(self, applicant_id: int) -> Dict:
        try:
            applications = self.application_repo.get_applications_by_applicant(applicant_id)
            
            return {
                'success': True,
                'message': f'Found {len(applications)} applications for applicant {applicant_id}',
                'data': [application.to_dict() for application in applications]
            }
        except Exception as e:
            logger.error(f"Error in get_applications_by_applicant: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting applications: {str(e)}',
                'data': None
            }
    
    def get_all_applications(self, page: int = 1, page_size: int = 50) -> Dict:
        try:
            offset = (page - 1) * page_size
            applications = self.application_repo.get_all_applications(limit=page_size, offset=offset)
            total_count = self.application_repo.get_applications_count()

            return {
                'success': True,
                'message': f'Found {len(applications)} applications',
                'data': {
                    'applications': applications,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error in get_all_applications: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting applications: {str(e)}',
                'data': None
            }
    
    def get_application_count(self) -> Dict:
        try:
            count = self.application_repo.get_applications_count()
            return {
                'success': True,
                'message': f'Total applications count retrieved',
                'data': {'count': count}
            }
        except Exception as e:
            logger.error(f"Error in get_application_count: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting application count: {str(e)}',
                'data': None
            }
    
    def get_applicant_count(self) -> Dict:
        try:
            count = self.applicant_repo.get_applicants_count()
            return {
                'success': True,
                'message': f'Total applicants count retrieved',
                'data': {'count': count}
            }
        except Exception as e:
            logger.error(f"Error in get_applicant_count: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting applicant count: {str(e)}',
                'data': None
            }
        
    def get_applicant_with_applications(self, applicant_id: int) -> Dict:
        try:
            applicant = self.applicant_repo.get_applicant_by_id(applicant_id)
            if not applicant:
                return {
                    'success': False,
                    'message': f'Applicant with ID {applicant_id} not found',
                    'data': None
                }
            
            applications = self.application_repo.get_applications_by_applicant(applicant_id)
            
            applicant_data = applicant.to_dict()
            applicant_data['applications'] = [app.to_dict() for app in applications]
            
            return {
                'success': True,
                'message': f'Found applicant with {len(applications)} applications',
                'data': applicant_data
            }
        except Exception as e:
            logger.error(f"Error in get_applicant_with_applications: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting applicant with applications: {str(e)}',
                'data': None
            }
    
    def get_application_with_applicant(self, application_id: int) -> Dict:
        try:
            application = self.application_repo.get_application_by_id(application_id)
            if not application:
                return {
                    'success': False,
                    'message': f'Application with ID {application_id} not found',
                    'data': None
                }
            
            applicant = self.applicant_repo.get_applicant_by_id(application.applicant_id)
            
            application_data = application.to_dict()
            application_data['applicant'] = applicant.to_dict() if applicant else None
            
            return {
                'success': True,
                'message': 'Application with applicant details found',
                'data': application_data
            }
        except Exception as e:
            logger.error(f"Error in get_application_with_applicant: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting application with applicant: {str(e)}',
                'data': None
            }
        
    def get_dashboard_stats(self) -> Dict:
        try:
            total_applicants = self.applicant_repo.get_applicants_count()
            total_applications = self.application_repo.get_applications_count()
            
            return {
                'success': True,
                'message': 'Dashboard statistics retrieved successfully',
                'data': {
                    'total_applicants': total_applicants,
                    'total_applications': total_applications,
                    'note': 'Status breakdown requires additional repository methods'
                }
            }
        except Exception as e:
            logger.error(f"Error in get_dashboard_stats: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting dashboard statistics: {str(e)}',
                'data': None
            }
    
    def get_monthly_application_stats(self, year: int = None, month: int = None) -> Dict:
        try:
            if not year:
                year = datetime.now().year
            if not month:
                month = datetime.now().month
            
            return {
                'success': True,
                'message': f'Monthly statistics for {month}/{year}',
                'data': {
                    'year': year,
                    'month': month,
                    'note': 'Implementation pending - requires additional repository methods'
                }
            }
        except Exception as e:
            logger.error(f"Error in get_monthly_application_stats: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting monthly statistics: {str(e)}',
                'data': None
            }
    
    def test_connection(self) -> Dict:
        try:
            count = self.applicant_repo.get_applicants_count()
            return {
                'success': True,
                'message': f'Database connection successful. Found {count} applicants.',
                'data': {'applicant_count': count}
            }
        except Exception as e:
            logger.error(f"Error in test_connection: {str(e)}")
            return {
                'success': False,
                'message': f'Database connection failed: {str(e)}',
                'data': None
            }
    
    def health_check(self) -> Dict:
        try:
            # Test database connection
            db_test = self.test_connection()
            
            # Get basic counts
            applicant_count = self.applicant_repo.get_applicants_count()
            application_count = self.application_repo.get_applications_count()
            
            return {
                'success': True,
                'message': 'ATS system health check completed',
                'data': {
                    'database_connection': db_test['success'],
                    'total_applicants': applicant_count,
                    'total_applications': application_count,
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error in health_check: {str(e)}")
            return {
                'success': False,
                'message': f'Health check failed: {str(e)}',
                'data': None
            }
