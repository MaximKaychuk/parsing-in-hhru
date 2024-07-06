import requests
from sqlalchemy import create_engine, Column, Integer, String, Text, func
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    job_title = Column(String)
    skills = Column(Text)
    work_format = Column(String)
    location = Column(String)
    source = Column(String)
    url = Column(String)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def parse_hh_vacancies(pages=10):
    url = 'https://api.hh.ru/vacancies'
    for page in range(pages):
        params = {
            'text': 'Python',
            'area': 1,  # Moscow
            'page': page,
            'per_page': 20
        }

        response = requests.get(url, params=params)
        response.encoding = 'utf-8'  # Устанавливаем правильную кодировку
        data = response.json()

        if 'items' not in data:
            print(f"Error: {data}")
            return

        for item in data['items']:
            job_title = item['name']
            skills = ', '.join([skill['name'] for skill in item.get('key_skills', [])])
            work_format = item.get('employment', {}).get('name', '')
            location = item.get('area', {}).get('name', '')
            source = 'hh.ru'
            vacancy_url = item['alternate_url']

            # Добавляем вывод данных в консоль для отладки
            print(f"Job Title: {job_title}")
            print(f"Skills: {skills}")
            print(f"Work Format: {work_format}")
            print(f"Location: {location}")
            print(f"Source: {source}")
            print(f"URL: {vacancy_url}")

            vacancy = Vacancy(
                job_title=job_title,
                skills=skills,
                work_format=work_format,
                location=location,
                source=source,
                url=vacancy_url
            )

            session.add(vacancy)
            print(f"Added vacancy: {job_title} - {location} - {vacancy_url}")

    session.commit()
    print("Vacancies committed to the database.")


def generate_analytics():
    vacancies_count = session.query(Vacancy).count()
    print(f"Total vacancies: {vacancies_count}")

    job_titles = session.query(Vacancy.job_title, func.count(Vacancy.id)).group_by(Vacancy.job_title).all()
    print("Vacancies by job title:")
    for title, count in job_titles:
        print(f"{title}: {count}")


if __name__ == '__main__':
    parse_hh_vacancies(pages=10)  # Увеличиваем количество страниц для парсинга
    generate_analytics()
