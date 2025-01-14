import requests
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(
    filename="debug.log",  # Логи будут сохраняться в файл debug.log
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Функция для безопасного извлечения текста из элемента
def safe_get_text(tag, default="Не найдено"):
    """Функция для безопасного извлечения текста из элемента."""
    if tag:
        return tag.text.strip()
    return default

# Функция для загрузки HTML страницы с обработкой ошибок
def get_html(url: str):
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            },
        )
        response.raise_for_status()  # Проверка на ошибки HTTP
        if "captcha" in response.text.lower():
            logging.warning("CAPTCHA обнаружена! Попробуйте использовать прокси или замедлить запросы.")
            return None
        logging.info("Успешно загружена страница. Первые 500 символов HTML:\n" + response.text[:500])
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе: {e}")
        return None

# Функция извлечения данных о вакансии
def extract_vacancy_data(html):
    if not html:
        logging.error("HTML пустой или отсутствует.")
        return "Не удалось извлечь данные о вакансии"
    
    soup = BeautifulSoup(html, "html.parser")

    # Извлечение данных
    title = safe_get_text(soup.find("h1", {"data-qa": "vacancy-title"}), "Название вакансии не найдено")
    salary = safe_get_text(soup.find("span", {"data-qa": "vacancy-salary"}), "Зарплата не указана")
    company = safe_get_text(soup.find("a", {"data-qa": "vacancy-company-name"}), "Компания не указана")
    location = safe_get_text(soup.find("p", {"data-qa": "vacancy-view-location"}), "Местоположение не указано")
    description = safe_get_text(soup.find("div", {"data-qa": "vacancy-description"}), "Описание вакансии не указано")

    # Логирование извлеченных данных
    logging.info(f"Извлеченные данные о вакансии:\nНазвание: {title}\nКомпания: {company}\nЗарплата: {salary}\nМестоположение: {location}\nОписание: {description[:100]}...")

    # Извлечение навыков
    skills = [skill.text.strip() for skill in soup.find_all("span", {"data-qa": "bloko-tag__text"})]
    skills = skills if skills else ["Навыки не указаны"]

    markdown = f"""
# {title}

**Компания:** {company}  
**Зарплата:** {salary}  
**Местоположение:** {location}  

## Описание
{description}  

## Ключевые навыки
- {'\n- '.join(skills)}
    """
    return markdown.strip()

# Функция извлечения данных о кандидате
def extract_candidate_data(html):
    if not html:
        logging.error("HTML пустой или отсутствует.")
        return "Не удалось извлечь данные о кандидате"
    
    soup = BeautifulSoup(html, 'html.parser')

    # Извлечение данных
    name = safe_get_text(soup.find('h2', {'data-qa': 'bloko-header-1'}), "Имя не указано")
    location = safe_get_text(soup.find('span', {'data-qa': 'resume-personal-address'}), "Местоположение не указано")
    job_title = safe_get_text(soup.find('span', {'data-qa': 'resume-block-title-position'}), "Должность не указана")
    job_status = safe_get_text(soup.find('span', {'data-qa': 'job-search-status'}), "Статус не указан")

    # Логирование основных данных
    logging.info(f"Извлеченные данные о кандидате:\nИмя: {name}\nМестоположение: {location}\nДолжность: {job_title}\nСтатус: {job_status}")

    # Извлечение опыта работы
    experience_section = soup.find('div', {'data-qa': 'resume-block-experience'})
    experience_items = experience_section.find_all('div', class_='resume-block-item-gap') if experience_section else []
    experiences = []
    for item in experience_items:
        period = safe_get_text(item.find('div', class_='bloko-column_s-2'))
        duration = safe_get_text(item.find('div', class_='bloko-text'))
        period = period.replace(duration, f" ({duration})")

        company = safe_get_text(item.find('div', class_='bloko-text_strong'))
        position = safe_get_text(item.find('div', {'data-qa': 'resume-block-experience-position'}))
        description = safe_get_text(item.find('div', {'data-qa': 'resume-block-experience-description'}))
        experiences.append(f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")

    # Логирование опыта работы
    logging.info(f"Извлечено {len(experiences)} записей об опыте работы.")

    # Извлечение навыков
    skills_section = soup.find('div', {'data-qa': 'skills-table'})
    skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})] if skills_section else ["Навыки не указаны"]

    # Формирование результата
    markdown = f"# {name}\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"
    markdown += "## Опыт работы\n\n"
    for exp in experiences:
        markdown += exp + "\n"
    markdown += "## Ключевые навыки\n\n"
    markdown += ', '.join(skills) + "\n"

    return markdown.strip()

# Получение описания вакансии
def get_job_description(url: str):
    html = get_html(url)
    return extract_vacancy_data(html) if html else "Ошибка при получении данных о вакансии"

# Получение информации о кандидате
def get_candidate_info(url: str):
    html = get_html(url)
    return extract_candidate_data(html) if html else "Ошибка при получении данных о кандидате"
