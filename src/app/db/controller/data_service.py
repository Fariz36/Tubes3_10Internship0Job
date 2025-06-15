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

        print(f"Searching candidates for position: {position} with keywords: {keywords}")
        
        app_result = self.controller.get_all_applications()
        if not app_result['success']:
            return []
        
        
        for app in app_result['data']['applications']:
            print(app)
            datum = self.controller.get_applicant(app['applicant_id'])
            if (datum['success'] and not datum['data']) or not datum['success']:
                print(f"Skipping application {app['applicant_id']} due to missing data.")
                continue
            datum_data = datum['data']
            print(datum_data)

            candidate = {
                "id": datum_data['applicant_id'],
                "first_name": datum_data['first_name'],
                "last_name": datum_data['last_name'],
                "phone": datum_data['phone_number'],
                "address": datum_data['address'],
                "birthdate": datetime.datetime.strptime(datum_data['date_of_birth'], "%Y-%m-%d").date() if datum_data['date_of_birth'] else None,
                "position": app['application_role'],
                "matched_keywords": {kw: 1 for kw in keywords},
                # "skills": ["Database", "Integration", "Python"],
                # "job_history": [{
                #     "position": app['position'],
                #     "company": app['company'],
                #     "period": "Current"
                # }],
                # "education": [{
                #     "institution": "University",
                #     "degree": "Computer Science",
                #     "period": "2018-2022"
                # }]
            }
            candidate["matches"] = len(keywords)
            candidates.append(candidate)
        
        return candidates[:top_n]