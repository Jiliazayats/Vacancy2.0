import requests
import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация OpenAI API ключа
openai.api_key = os.getenv("OPENAI_API_KEY")

# Получение данных о вакансии через публичную страницу HH
def get_vacancy(vacancy_id):
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    response = requests.get(url)
    if response.status_code == 404:
        return {"error": "Вакансия не найдена"}
    return response.json()

# Получение данных о резюме через публичную страницу HH
def get_resume(resume_id):
    url = f"https://api.hh.ru/resumes/{resume_id}"
    response = requests.get(url)
    if response.status_code == 404:
        return {"error": "Резюме не найдено"}
    data = response.json()
    # Извлекаем ключевые навыки, если они есть
    skills = [skill['name'] for skill in data.get('skills', [])]
    full_name = f"{data.get('first_name', 'Не указано')} {data.get('last_name', 'Не указано')}".strip()
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

job_id = st.text_area("Введите ID вакансии")
resume_id = st.text_area("Введите ID резюме")

SYSTEM_PROMPT = "Вы являетесь экспертом по оценке резюме и вакансий. Сравните резюме и вакансию и предоставьте оценку."

if st.button("Оценить резюме"):
    with st.spinner("Оценка резюме..."):
        # Получение данных
        job_description = get_vacancy(job_id)
        if "error" in job_description:
            st.write(job_description["error"])
        else:
            cv = get_resume(resume_id)
            if "error" in cv:
                st.write(cv["error"])
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
