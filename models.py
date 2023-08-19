from flask import Flask, render_template, request, jsonify, url_for, redirect
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate

# Initialize Flask-Migrate after initializing SQLAlchemy



app = Flask(__name__)

load_dotenv()

DATABASE_URL_RAW = os.getenv('DATABASE_URL')
DATABASE_URL = DATABASE_URL_RAW.replace("postgres://", "postgresql://") if DATABASE_URL_RAW else None
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL



db = SQLAlchemy(app)

migrate = Migrate(app, db)
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
    role_name = db.Column(db.String)  # Temporarily allow null values
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.skill_id'))
    count = db.Column(db.Integer, default=0)


class CompanySkillAssociation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String)  # This assumes company names are unique. Adjust accordingly if not.
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.skill_id'))
    count = db.Column(db.Integer, default=0)
