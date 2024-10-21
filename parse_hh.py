import requests
from bs4 import BeautifulSoup

def get_html(url: str):
    return requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        },
    )

def extract_vacancy_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Извлечение заголовка вакансии
    title_tag = soup.find("h1", {"data-qa": "vacancy-title"})
    title = title_tag.text.strip() if title_tag else "Не указано"

    # Извлечение зарплаты
    salary_tag = soup.find("span", {"data-qa": "vacancy-salary-compensation-type-net"})
    salary = salary_tag.text.strip() if salary_tag else "Не указано"

    # Извлечение опыта работы
    experience_tag = soup.find("span", {"data-qa": "vacancy-experience"})
    experience = experience_tag.text.strip() if experience_tag else "Не указано"

    # Извлечение типа занятости и режима работы
    employment_mode_tag = soup.find("p", {"data-qa": "vacancy-view-employment-mode"})
    employment_mode = employment_mode_tag.text.strip() if employment_mode_tag else "Не указано"

    # Извлечение компании
    company_tag = soup.find("a", {"data-qa": "vacancy-company-name"})
    company = company_tag.text.strip() if company_tag else "Не указано"

    # Извлечение местоположения
    location_tag = soup.find("p", {"data-qa": "vacancy-view-location"})
    location = location_tag.text.strip() if location_tag else "Не указано"

    # Извлечение описания вакансии
    description_tag = soup.find("div", {"data-qa": "vacancy-description"})
    description = description_tag.text.strip() if description_tag else "Не указано"

    # Извлечение ключевых навыков
    skills = [
        skill.text.strip()
        for skill in soup.find_all("div", class_="magritte-tag__label___YHV-o_3-0-13")
    ]

    # Формирование строки в формате Markdown
    markdown = f"""
# {title}

**Компания:** {company}
**Зарплата:** {salary}
**Опыт работы:** {experience}
**Тип занятости и режим работы:** {employment_mode}
**Местоположение:** {location}

## Описание вакансии
{description}

## Ключевые навыки
- {'\n- '.join(skills) if skills else 'Не указаны'}
"""

    return markdown.strip()

def extract_candidate_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Извлечение основных данных кандидата
    name_tag = soup.find('h2', {'data-qa': 'bloko-header-1'})
    name = name_tag.text.strip() if name_tag else "Не указано"

    gender_age_tag = soup.find('p')
    gender_age = gender_age_tag.text.strip() if gender_age_tag else "Не указано"

    location_tag = soup.find('span', {'data-qa': 'resume-personal-address'})
    location = location_tag.text.strip() if location_tag else "Не указано"

    job_title_tag = soup.find('span', {'data-qa': 'resume-block-title-position'})
    job_title = job_title_tag.text.strip() if job_title_tag else "Не указано"

    job_status_tag = soup.find('span', {'data-qa': 'job-search-status'})
    job_status = job_status_tag.text.strip() if job_status_tag else "Не указано"

    # Извлечение опыта работы
    experience_section = soup.find('div', {'data-qa': 'resume-block-experience'})
    experience_items = experience_section.find_all('div', class_='resume-block-item-gap') if experience_section else []
    experiences = []
    for item in experience_items:
        period_tag = item.find('div', class_='bloko-column_s-2')
        period = period_tag.text.strip() if period_tag else "Не указано"

        duration_tag = item.find('div', class_='bloko-text')
        duration = duration_tag.text.strip() if duration_tag else ""
        if duration:
            period = period.replace(duration, f" ({duration})")

        company_tag = item.find('div', class_='bloko-text_strong')
        company = company_tag.text.strip() if company_tag else "Не указано"

        position_tag = item.find('div', {'data-qa': 'resume-block-experience-position'})
        position = position_tag.text.strip() if position_tag else "Не указано"

        description_tag = item.find('div', {'data-qa': 'resume-block-experience-description'})
        description = description_tag.text.strip() if description_tag else "Не указано"

        experiences.append(f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")

    # Извлечение ключевых навыков
    skills_section = soup.find('div', {'data-qa': 'skills-table'})
    skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})] if skills_section else []

    # Формирование строки в формате Markdown
    markdown = f"# {name}\n\n"
    markdown += f"**{gender_age}**\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"
    markdown += "## Опыт работы\n\n"
    for exp in experiences:
        markdown += exp + "\n"
    markdown += "## Ключевые навыки\n\n"
    markdown += ', '.join(skills) if skills else "Не указаны"

    return markdown

def get_candidate_info(url: str):
    response = get_html(url)
    return extract_candidate_data(response.text)

def get_job_description(url: str):
    response = get_html(url)
    return extract_vacancy_data(response.text)
