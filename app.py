from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import os
from main import Base, Vacancy, parse_hh_vacancies  # Импортируем модели и функции из main.py

app = Flask(__name__)

# Используем переменную окружения DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def index():
    vacancies = session.query(Vacancy).all()
    return render_template('index.html', vacancies=vacancies)


@app.route('/parse', methods=['POST'])
def parse():
    pages = request.form.get('pages', 1, type=int)
    parse_hh_vacancies(pages)
    return redirect(url_for('index'))


@app.route('/vacancy/<int:id>')
def vacancy_detail(id):
    vacancy = session.query(Vacancy).get(id)
    return render_template('vacancy_detail.html', vacancy=vacancy)


@app.route('/analytics')
def analytics():
    total_vacancies = session.query(Vacancy).count()
    job_titles = session.query(Vacancy.job_title, func.count(Vacancy.id)).group_by(Vacancy.job_title).all()

    return render_template('analytics.html', total_vacancies=total_vacancies, job_titles=job_titles)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

