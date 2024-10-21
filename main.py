import requests
from bs4 import BeautifulSoup
import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация OpenAI API ключа
openai.api_key = os.getenv("OPENAI_API_KEY")

# Парсинг страницы вакансии
def parse_vacancy(vacancy_url):
    response = requests.get(vacancy_url)
    if response.status_code != 200:
        return {"error": f"Вакансия не найдена, статус ответа: {response.status_code}", "content": response.content}
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', {'data-qa': 'vacancy-title'}).text.strip() if soup.find('h1', {'data-qa': 'vacancy-title'}) else 'Не указано'
    description = soup.find('div', {'data-qa': 'vacancy-description'}).text.strip() if soup.find('div', {'data-qa': 'vacancy-description'}) else 'Не указано'
    
    return {
        "title": title,
        "description": description
    }

# Парсинг страницы резюме
def parse_resume(resume_url):
    response = requests.get(resume_url)
    if response.status_code != 200:
        return {"error": f"Резюме не найдено, статус ответа: {response.status_code}", "content": response.content}

    soup = BeautifulSoup(response.content, 'html.parser')
    full_name = soup.find('span', {'data-qa': 'resume-personal-name'}).text.strip() if soup.find('span', {'data-qa': 'resume-personal-name'}) else 'Не указано'
    skills_section = soup.find('div', {'data-qa': 'skills-block'})
    skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})] if skills_section else []

    return {
        "full_name": full_name,
        "skills": skills
    }

# Генерация ответа от GPT
def request_gpt(system_prompt, user_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        temperature=0,
    )
    return response.choices[0].message["content"]

# Streamlit UI на русском языке
st.title("Оценка резюме")

vacancy_url = st.text_area("Введите ссылку на вакансию")
resume_url = st.text_area("Введите ссылку на резюме")

SYSTEM_PROMPT = "Вы являетесь экспертом по оценке резюме и вакансий. Сравните резюме и вакансию и предоставьте оценку."

if st.button("Оценить резюме"):
    with st.spinner("Оценка резюме..."):
        # Получение данных
        job_description = parse_vacancy(vacancy_url)
        if "error" in job_description:
            st.write(job_description["error"])
            st.write(job_description.get("content", ""))
        else:
            cv = parse_resume(resume_url)
            if "error" in cv:
                st.write(cv["error"])
                st.write(cv.get("content", ""))
            else:
                # Отображение данных
                st.write("Описание вакансии:")
                st.write(job_description)
                st.write("Резюме:")
                st.write(cv)

                # Создание запроса к GPT
                user_prompt = f"# ВАКАНСИЯ\n{job_description}\n\n# РЕЗЮМЕ\n{cv}"
                response = request_gpt(SYSTEM_PROMPT, user_prompt)

                st.write(response)
