from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()
app = Flask(__name__)

DATABASE_URL_RAW = os.getenv('DATABASE_URL')
DATABASE_URL = DATABASE_URL_RAW.replace("postgres://", "postgresql://") if DATABASE_URL_RAW else None
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

db = SQLAlchemy(app)

class Job(db.Model):
    job_id = db.Column(db.String, primary_key=True)
    role_name = db.Column(db.String, nullable=False)
    company_name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Skill(db.Model):
    skill_id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String, nullable=False)
    mention_count = db.Column(db.Integer, default=0)

class JobSkillAssociation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String, nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.skill_id'))
    count = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    roles = db.session.query(Job.role_name).distinct().all()
    skills = Skill.query.all()
    return render_template('index.html', roles=roles, skills=skills)

@app.route('/get_skills_score', methods=['POST'])
def get_skills_score():
    # Get user input
    chosen_role = request.form.get('role')
    chosen_skills = request.form.getlist('skills')

    # Total jobs for the role
    total_jobs_for_role = Job.query.filter_by(role_name=chosen_role).count()

    # For each skill, find out how many times it appears for the chosen role
    skill_scores = {}
    for skill in chosen_skills:
        skill_obj = Skill.query.filter_by(skill_name=skill).first()
        if not skill_obj:
            continue
        
        count_for_skill = Job.query.filter(
            Job.role_name == chosen_role,
            Job.description.ilike(f"%{skill}%")  # Case-insensitive like query
        ).count()

        skill_scores[skill] = count_for_skill / total_jobs_for_role if total_jobs_for_role > 0 else 0

    # Get top 10 skills for the chosen role
    all_skills = Skill.query.all()
    skill_counts = {}
    for skill in all_skills:
        count = Job.query.filter(
            Job.role_name == chosen_role,
            Job.description.ilike(f"%{skill.skill_name}%")
        ).count()
        skill_counts[skill.skill_name] = count
        
    # Sort skills by count and take the top 10
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return render_template('results.html', chosen_skills=skill_scores, top_skills=top_skills)



if __name__ == "__main__":
    app.run(debug=True)
