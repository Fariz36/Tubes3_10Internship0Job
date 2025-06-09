import datetime

class DataService:
    def __init__(self):
        self._candidates = [
            {
                "id": 1,
                "name": "Adha",
                "email": "adha.keren@example.com",
                "phone": "081234567890",
                "address": "Jl. Ganesa No. 10, Bandung",
                "birthdate": datetime.date(2000, 5, 19),
                "matched_keywords": {
                    "React": 4, "C++": 7, "Java": 1, "Node.js": 5, "MongoDB": 2,
                    "Python": 10, "JavaScript": 8, "TypeScript": 3, "Go": 1
                },
                "skills": ["React", "C++", "Java", "Node.js", "MongoDB", "Python", "JavaScript", "TypeScript", "Go"],
                "job_history": [
                    {"position": "Software Engineer", "company": "Google", "period": "2022-Sekarang"},
                    {"position": "Intern", "company": "Tokopedia", "period": "2021-2022"}
                ],
                "education": [
                    {"institution": "Institut Teknologi Bandung", "degree": "S1 Teknik Informatika", "period": "2018-2022"}
                ]
            },
            {
                "id": 2,
                "name": "Budi",
                "email": "budi.santoso@example.com",
                "phone": "081234567891",
                "address": "Jl. Dago Asri No. 15, Bandung",
                "birthdate": datetime.date(1999, 8, 22),
                "matched_keywords": { "Python": 5, "SQL": 2 },
                "skills": ["Python", "SQL", "Django", "PostgreSQL", "Docker"],
                "job_history": [
                    {"position": "Data Scientist", "company": "Traveloka", "period": "2021-Sekarang"}
                ],
                "education": [
                    {"institution": "Universitas Indonesia", "degree": "S1 Ilmu Komputer", "period": "2017-2021"}
                ]
            },
            {
                "id": 3,
                "name": "Caca",
                "email": "caca.cantik@example.com",
                "phone": "081234567892",
                "address": "Jl. Setiabudi No. 20, Bandung",
                "birthdate": datetime.date(2001, 1, 30),
                "matched_keywords": { "HTML": 3, "CSS": 1 },
                "skills": ["HTML", "CSS", "JavaScript", "Figma", "UI/UX Design"],
                "job_history": [
                    {"position": "Frontend Developer", "company": "Shopee", "period": "2023-Sekarang"}
                ],
                "education": [
                    {"institution": "Universitas Gadjah Mada", "degree": "S1 Desain Komunikasi Visual", "period": "2019-2023"}
                ]
            },
            {
                "id": 4,
                "name": "Deni",
                "email": "deni.ganteng@example.com",
                "phone": "081234567893",
                "address": "Jl. Pasteur No. 5, Bandung",
                "birthdate": datetime.date(2002, 11, 11),
                "matched_keywords": { "Flet": 8, "Python": 1 },
                "skills": ["Flet", "Python", "FastAPI", "REST API"],
                "job_history": [
                    {"position": "Backend Developer", "company": "Gojek", "period": "2023-Sekarang"}
                ],
                "education": [
                    {"institution": "Institut Teknologi Sepuluh Nopember", "degree": "S1 Teknik Komputer", "period": "2020-2024"}
                ]
            },
        ]
        
        for candidate in self._candidates:
            total_occurrences = sum(candidate["matched_keywords"].values())
            candidate["matches"] = total_occurrences

    def get_total_cvs(self):
        return len(self._candidates)

    def search_candidates(self, keywords: list, top_n: int, algorithm: str):

        # TODO: Implement search logic based on keywords, top_n, and algorithm
        
        print(f"Searching with keywords: {keywords}, top_n: {top_n}, algorithm: {algorithm}")
        sorted_candidates = sorted(self._candidates, key=lambda c: c['matches'], reverse=True)
        
        return sorted_candidates[:top_n]