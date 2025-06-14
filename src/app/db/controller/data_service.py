import datetime
from db.controller.atsController import ATSController
from typing import List, Dict

class DataService:
    def __init__(self):
        self.controller = ATSController()
        self.algorithm_toggle = True 

    def get_total_cvs(self):
        result = self.controller.get_dashboard_stats()
        return result['data']['total_applicants'] if result['success'] else 0

    def search_candidates(self, keywords: list, top_n: int, algorithm: str):
        candidates = []
        position = keywords[0] if keywords else ""
        
        app_result = self.controller.search_applications_by_position(position)
        if not app_result['success']:
            return []
        
        for app in app_result['data']:
            applicant_result = self.controller.get_applicant(app['applicant_id'])
            if not applicant_result['success']:
                continue
                
            applicant = applicant_result['data']
            candidate = {
                "id": applicant['applicant_id'],
                "name": applicant['full_name'],
                "email": applicant['email'],
                "phone": applicant['phone'],
                "address": applicant['address'],
                "birthdate": datetime.datetime.strptime(applicant['date_of_birth'], "%Y-%m-%d").date() if applicant['date_of_birth'] else None,
                "position": app['position'],
                "matched_keywords": {kw: 1 for kw in keywords},
                "skills": ["Database", "Integration", "Python"],
                "job_history": [{
                    "position": app['position'],
                    "company": app['company'],
                    "period": "Current"
                }],
                "education": [{
                    "institution": "University",
                    "degree": "Computer Science",
                    "period": "2018-2022"
                }]
            }
            candidate["matches"] = len(keywords)
            candidates.append(candidate)
        
        return candidates[:top_n]