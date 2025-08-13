import re
from typing import Dict, Any, List

def extract_job_description_from_vacancy(vacancy_data: Dict[str, Any]) -> str:
    position = vacancy_data.get('name', 'Не указана')
    company = vacancy_data.get('employer', {}).get('name', 'Не указана')
    description = vacancy_data.get('description', '')
    salary_info = ""
    salary = vacancy_data.get('salary')
    if salary:
        f = salary.get('from'); t = salary.get('to'); c = salary.get('currency', 'RUR')
        if f and t: salary_info = f"от {f:,} до {t:,} {c}"
        elif f: salary_info = f"от {f:,} {c}"
        elif t: salary_info = f"до {t:,} {c}"
    experience = vacancy_data.get('experience', {}).get('name', 'Не указан')
    employment = vacancy_data.get('employment', {}).get('name', 'Не указан')
    schedule = vacancy_data.get('schedule', {}).get('name', 'Не указан')
    key_skills: List[str] = [s['name'] for s in vacancy_data.get('key_skills', []) if isinstance(s, dict) and 'name' in s]
    chunks = [f"ВАКАНСИЯ: {position}", f"КОМПАНИЯ: {company}"]
    if salary_info: chunks.append(f"ЗАРПЛАТА: {salary_info}")
    chunks.extend([f"ОПЫТ РАБОТЫ: {experience}", f"ТИП ЗАНЯТОСТИ: {employment}", f"ГРАФИК РАБОТЫ: {schedule}"])
    if key_skills: chunks.append(f"КЛЮЧЕВЫЕ НАВЫКИ: {', '.join(key_skills)}")
    if description:
        clean = re.sub(r'<[^>]+>', '', description); clean = re.sub(r'\s+', ' ', clean).strip()
        chunks.append(f"\nОПИСАНИЕ ВАКАНСИИ:\n{clean}")
    return "\n".join(chunks)
