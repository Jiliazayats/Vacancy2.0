# Ваш API-ключ OpenAI
OPENAI_API_KEY = "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"

from openai import OpenAI
import streamlit as st
from parse_hh import get_job_description, get_candidate_info

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Промпт для системы
SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии. Ответь строго на русском языке.

Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?). Эта оценка должна учитываться при выставлении финальной оценки - нам важно нанимать таких кандидатов, которые могут рассказать про свою работу.
Потом представь результат в виде оценки от 1 до 10.
""".strip()

# Функция для работы с OpenAI GPT
def request_gpt(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при запросе к GPT: {e}"

# Интерфейс Streamlit
st.title("CV Scoring App")

# Поля ввода для URL вакансии и резюме
job_description_url = st.text_input("Введите ссылку на описание вакансии")
cv_url = st.text_input("Введите ссылку на резюме кандидата")

# Кнопка для запуска оценки
if st.button("Оценить резюме"):
    if not job_description_url or not cv_url:
        st.error("Пожалуйста, введите ссылки на вакансию и резюме.")
    else:
        with st.spinner("Обработка данных..."):
            # Получение данных о вакансии и резюме
            job_description = get_job_description(job_description_url)
            candidate_info = get_candidate_info(cv_url)

            # Отображение данных
            st.subheader("Описание вакансии")
            st.text(job_description)

            st.subheader("Резюме кандидата")
            st.text(candidate_info)

            # Проверка на ошибки парсинга
            if "Ошибка" in job_description or "Ошибка" in candidate_info:
                st.error("Не удалось получить корректные данные. Проверьте ссылки.")
            else:
                # Формирование запроса для GPT
                user_prompt = f"# ВАКАНСИЯ\n{job_description}\n\n# РЕЗЮМЕ\n{candidate_info}"
                gpt_response = request_gpt(SYSTEM_PROMPT, user_prompt)

                # Отображение результата оценки
                st.subheader("Результат оценки")
                st.markdown(gpt_response)
