import re
import json
from typing import Dict, List, Optional
import fitz

class InfoPentingGacorRealNoHoax:
    def __init__(self):
        # Define regex patterns for each section
        self.summary_patterns = [
            r'(?i)(?:summary|career overview|professional summary|profile)\s*\n(.*?)(?=\n[A-Z][A-Za-z\s]*\n|\n(?:Experience|Education|Skills|Core|Highlights|Professional))',
            r'(?i)(?:summary|career overview|professional summary|profile)\s*(.*?)(?=(?:Experience|Education|Skills|Core|Highlights|Professional))',
        ]
        
        self.education_patterns = [
            r'(?i)(?:education|education and training|academic background)\s*\n(.*?)(?=\n[A-Z][A-Za-z\s]*\n|\n(?:Experience|Skills|Professional|Additional|Interests))',
            r'(?i)(?:education|education and training|academic background)\s*(.*?)(?=(?:Experience|Skills|Professional|Additional|Interests))',
        ]
        
        self.experience_patterns = [
            r'(?i)(?:experience|professional experience|work experience|employment history|career history)\s*\n(.*?)(?=\n(?:Education|Skills|Additional|Interests|Professional Affiliations))',
            r'(?i)(?:experience|professional experience|work experience|employment history|career history)\s*(.*?)(?=(?:Education|Skills|Additional|Interests|Professional Affiliations))',
        ]
        
        self.skills_patterns = [
            r'(?i)(?:skills|core qualifications|technical skills|competencies|skill highlights|core accomplishments)\s*\n(.*?)(?=\n[A-Z][A-Za-z\s]*\n|\n(?:Additional|Interests|Professional|References)|\Z)',
            r'(?i)(?:skills|technical skills|competencies|skill highlights|core accomplishments)\s*(.*?)(?=(?:Additional|Interests|Professional|References)|\Z)',
        ]
    
    def read_pdf(self, cv_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try with PyMuPDF first (better text extraction)
            doc = fitz.open(cv_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except:
            # Fallback to PyPDF2
            try:
                text = ""
                with fitz.open(cv_path) as doc:
                    for page in doc:
                        text += page.get_text()
                return text
            except Exception as e:
                print(f"Error reading PDF: {str(e)}")
                return ""
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text by preserving line breaks but removing formatting and extra spaces"""
        if not text:
            return ""
        
        cleaned_lines = []
        for line in text.splitlines():
            line = line.strip()
            line = re.sub(r'\s+', ' ', line)  # normalize spaces inside the line
            line = re.sub(r'[^\w\s\.,;:()\-/&]', '', line)  # remove weird artifacts
            if line:  # skip empty lines
                cleaned_lines.append(line)
    
        return '\n'.join(cleaned_lines)

    def extract_section(self, cv_text: str, patterns: List[str]) -> str:
        """Extract a specific section from CV text using regex patterns"""
        res = ""
        for pattern in patterns:
            match = re.search(pattern, cv_text, re.DOTALL | re.IGNORECASE)
            if match:
                extracted_text = match.group(1)
                res += self.clean_text(extracted_text.rstrip())
                res += '\n'
        return res if res else None
    
    def get_summaries(self, cv_path: str) -> List[str]:
        """ Extract summary information from CV """
        cv_text = self.read_pdf(cv_path)
        if not cv_text:
            return []
        
        summary_text = self.extract_section(cv_text, self.summary_patterns)
        
        if summary_text:
            return [{"text" : summary_text}]
        else:
            return []
        
    def normalize_dates_to_month_year(self, text: str) -> str:
        # Define month mapping
        month_map = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12"
        }

        # Regex to find formats like "September 2014" or "September-2014"
        pattern = re.compile(r'\b(' + '|'.join(month_map.keys()) + r')[\s\-]+(\d{4})\b', re.IGNORECASE)

        def repl(match):
            month = match.group(1).lower()
            year = match.group(2)
            return f"{month_map[month]}/{year}"

        return pattern.sub(repl, text)
    
    def get_job_histories(self, cv_path: str) -> List[Dict[str, str]]:
        """ Extract experience information from CV """
        cv_text = self.read_pdf(cv_path)
        if not cv_text:
            return []
        
        print(cv_text)
        
        experience_text = self.extract_section(cv_text, self.experience_patterns)
        experience_text = experience_text.lower()
        experience_text = self.normalize_dates_to_month_year(experience_text)

        if not experience_text:
            return []
           
        print(f"Extracted Experience Text: {experience_text}...")  # Debugging line
        
        job_histories = []
        job_patterns = [
            r'(\d{1,2}/\d{4}|\w+\s+\d{4})\s+to\s+(\w+|\d{1,2}/\d{4})\s*\n?([A-Z][A-Za-z\s&-]+?)(?:\s+Company Name|\s+[A-Z][a-z]+\s*,?\s*[A-Z][a-z]*)',
            r'(\d{1,2}/\d{4}|\w+\s+\d{4})\s+to\s+(\w+|\d{1,2}/\d{4})\s*([A-Z][A-Za-z\s&-]+?)\s+([A-Za-z\s,&-]+)',
            r'(\d{4})\s+to\s+(\d{4}|\w+)\s*([A-Z][A-Za-z\s&-]+?)\s+([A-Za-z\s,&-]+)',
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, experience_text, re.MULTILINE)
            
            for match in matches:
                print(match)
                if len(match) >= 3:
                    start_date = match[0].strip()
                    end_date = match[1].strip()
                    position = match[2].strip()
                    company = match[3].strip() if len(match) > 3 else "Company Name"
                    
                    position = re.sub(r'\s+', ' ', position)
                    company = re.sub(r'\s+', ' ', company)
                    
                    if len(position) > 3 and not re.match(r'^[A-Z]{2,}$', position):
                        job_histories.append({
                            "position": position,
                            "company": company,
                            "period": f"{start_date} to {end_date}"
                        })

        next_pattern = r'(\d{2}/\d{4})\s+to\s+(\d{2}/\d{4})\s+([a-zA-Z&.\s,-]+?)\s+([a-zA-Z/&\s\-.()]+)\s+([a-zA-Z/&\s\-.(),]+\n)'
        matches = re.findall(next_pattern, experience_text)

        job_histories = []
        for match in matches:
            start_date = match[0].strip()
            end_date = match[1].strip()
            company = re.sub(r'\s+', ' ', match[2].strip())
            position = re.sub(r'\s+', ' ', match[4].strip())

            if len(position) > 3 and not re.match(r'^[A-Z]{2,}$', position):
                job_histories.append({
                    "position": position,
                    "company": company,
                    "period": f"{start_date} to {end_date}"
                })
        
        # If no structured matches found, try to extract job titles manually
        if not job_histories:
            title_pattern = r'(?:^|\n)([A-Z][A-Za-z\s&-]{10,50}?)(?:\s+Company Name|\s+\d{1,2}/\d{4}|\s+\w+\s+\d{4})'
            titles = re.findall(title_pattern, experience_text, re.MULTILINE)
            
            for title in titles:
                title = title.strip()
                if len(title) > 5:
                    job_histories.append({
                        "position": title,
                        "company": "Company Name",
                        "period": "Not specified"
                    })
        
        return job_histories
    
    def get_educations(self, cv_path: str) -> List[Dict[str, str]]:
        """ Extract education information from CV """
        cv_text = self.read_pdf(cv_path)
        if not cv_text:
            return []
        
        education_text = self.extract_section(cv_text, self.education_patterns)
        if not education_text:
            return []
        
        educations = []
        
        # Pattern to match education entries
        edu_patterns = [
            r'(\w+\s+\d{4}|\d{4})\s*([A-Za-z\s:]+?)(?:\s*:\s*([A-Za-z\s&,]+?))?\s+([A-Za-z\s&,]+?)\s+(?:City|State|\Z)',
            r'(\w+\s+\d{4}|\d{4})\s*\n?([A-Za-z\s:]+?)\s+([A-Za-z\s&,]+)',
            r'([A-Za-z\s]+degree)\s+([A-Za-z\s&,]+?)\s+([A-Za-z\s&,]+)'
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, education_text, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                if len(match) >= 3:
                    # Handle different match structures
                    if re.search(r'\d{4}', match[0]):  # First element contains year
                        period = match[0].strip()
                        degree = match[1].strip()
                        if len(match) > 3:
                            field = match[2].strip() if match[2] else ""
                            institution = match[3].strip()
                        else:
                            field = ""
                            institution = match[2].strip()
                    else:  # Degree type first
                        period = "Not specified"
                        degree = match[0].strip()
                        institution = match[1].strip()
                        field = match[2].strip() if len(match) > 2 else ""
                    
                    # Clean up the fields
                    degree = re.sub(r'\s+', ' ', degree)
                    institution = re.sub(r'\s+', ' ', institution)
                    
                    # Combine degree and field if both exist
                    if field and field.strip():
                        full_degree = f"{degree} : {field}"
                    else:
                        full_degree = degree
                    
                    # Skip if degree is too short
                    if len(full_degree) > 5:
                        educations.append({
                            "degree": full_degree,
                            "institution": institution,
                            "period": period
                        })
        
        # Remove duplicates based on degree and institution
        seen = set()
        unique_educations = []
        for edu in educations:
            key = (edu["degree"].lower(), edu["institution"].lower())
            if key not in seen:
                seen.add(key)
                unique_educations.append(edu)
        
        return unique_educations
    
    def get_skills(self, cv_path: str) -> List[str]:
        """ Extract skills information from CV """
        cv_text = self.read_pdf(cv_path)
        if not cv_text:
            return []
        
        skills_text = self.extract_section(cv_text, self.skills_patterns)
        if not skills_text:
            return []  

        # Split by common delimiters
        skills = re.split(r'[,;·•\n]', skills_text)
        # Clean and filter empty skills
        skills = [skill.strip() for skill in skills if skill.strip() and len(skill.strip()) > 1]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.lower() not in seen and len(skill) > 1:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills