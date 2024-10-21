import os

import openai
import streamlit as st

from parse_hh import get_candidate_info, get_job_description

client = openai.Client(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии.

Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?). Эта оценка должна учитываться при выставлении финальной оценки - нам важно нанимать таких кандидатов, которые могут рассказать про свою работу
Потом представь результат в виде оценки от 1 до 10.
""".strip()

def request_gpt(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        temperature=0,
    )
    return response.choices[0].message.content

st.title("Приложение для оценки резюме")

job_description_url = st.text_area("Введите URL описания вакансии")

cv_url = st.text_area("Введите URL резюме")

if st.button("Оценить резюме"):
    with st.spinner("Оценка резюме..."):

        job_description = get_job_description(job_description_url)
        cv = get_candidate_info(cv_url)

        st.write("### Описание вакансии:")
        st.write(job_description)
        
        # Отображение ключевых навыков из описания вакансии
        skills_start = job_description.find("## Ключевые навыки")
        if skills_start != -1:
            skills_section = job_description[skills_start:]
            st.write("### Ключевые навыки вакансии:")
            st.write(skills_section)

        st.write("### Резюме кандидата:")
        st.write(cv)

        user_prompt = f"# ВАКАНСИЯ\n{job_description}\n\n# РЕЗЮМЕ\n{cv}"
        response = request_gpt(SYSTEM_PROMPT, user_prompt)

    st.write("### Результат оценки:")
    st.write(response)
