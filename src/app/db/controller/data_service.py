import datetime
from db.controller.atsController import ATSController
from typing import List, Dict
from db.controller.matcher import Matcher, AhoCorasick

class DataService:
    def __init__(self):
        self.controller = ATSController()
        self.algorithm_toggle = True 

    def get_total_cvs(self):
        result = self.controller.get_dashboard_stats()
        return result['data']['total_applicants'] if result['success'] else 0

    def search_candidates(self, keywords: list, top_n: int, algorithm: str):
        candidates = []

        app_result = self.controller.get_all_applications()
        if not app_result['success']:
            return []
        
        app_dict = {app["detail_id"]: app for app in app_result['data']['applications']}
        
        queries = [kw.lower() for kw in keywords]
        texts = [(app['detail_id'], app['cv_path']) for app in app_result['data']['applications']]

        matcher = Matcher(texts, queries)
        result = matcher.match(algorithm)

        sorted_result = sorted(result, key=lambda x: x["result"]["total_matched"], reverse=True)[:top_n]

        print(queries)        

        for item in sorted_result:
            application = app_dict.get(item['id'])
            datum = self.controller.get_applicant(application['applicant_id'])
            if (datum['success'] and not datum['data']) or not datum['success']:
                print(f"Skipping application {item['id']} due to missing data.")
                continue
            datum_data = datum['data']
            candidate = {
                "id": datum_data['applicant_id'],
                "first_name": datum_data['first_name'],
                "last_name": datum_data['last_name'],
                "phone": datum_data['phone_number'],
                "address": datum_data['address'],
                "birthdate": datetime.datetime.strptime(datum_data['date_of_birth'], "%Y-%m-%d").date() if datum_data['date_of_birth'] else None,
            }
            candidate["matched_keywords"] = item['result']
            print(candidate)

            candidates.append(candidate)

        return candidates[:top_n]