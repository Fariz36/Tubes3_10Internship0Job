import datetime
from db.controller.atsController import ATSController
from typing import List, Dict
from db.controller.matcher import Matcher, AhoCorasick

class DataService:
    def __init__(self):
        self.controller = ATSController()
        self.algorithm_toggle = True 

        self.app_dict = {}
        self.matcher = Matcher(self.get_all_text(), [])

    def get_all_text(self) -> str:
        app_result = self.controller.get_all_applications()
        if not app_result['success']:
            return []
        
        self.app_dict = {app["detail_id"]: app for app in app_result['data']['applications']}
        
        queries = []
        texts = [(app['detail_id'], app['cv_path']) for app in app_result['data']['applications']]

        return texts


    def get_total_cvs(self):
        result = self.controller.get_dashboard_stats()
        return result['data']['total_applications'] if result['success'] else 0

    def search_candidates(self, keywords: list, top_n: int, algorithm: str):
        candidates = []

        self.matcher.set_keywords(keywords)
        result, exact_match_calculation_time, fuzzy_match_calculation_time = self.matcher.match(algorithm)

        sorted_result = sorted(result, key=lambda x: x["result"]["total_matched"], reverse=True)[:top_n]   

        # prune further if total matched is zero
        sorted_result = [item for item in sorted_result if item['result']['total_matched'] > 0]   

        for item in sorted_result:
            application = self.app_dict.get(item['id'])
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
            candidates.append(candidate)

        return candidates[:top_n], exact_match_calculation_time, fuzzy_match_calculation_time