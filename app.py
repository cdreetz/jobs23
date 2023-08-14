from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)


DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://your_username:your_password@localhost/your_database_name'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)

# Database models
class Job(db.Model):
    job_id = db.Column(db.String, primary_key=True)
    role_name = db.Column(db.String, nullable=False)
    company_name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Skill(db.Model):
    skill_id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String, nullable=False)
    mention_count = db.Column(db.Integer, default=0)


# List of potential skills - this can be expanded upon
SKILLS = [
    "python", "r", "sql", "machine learning", "deep learning", "tensorflow", 
    "pytorch", "tableau", "excel", "big data", "hadoop", "spark", "statistics", 
    "nlp", "natural language processing", "computer vision"
]

def extract_skills_from_description(description):
    for skill in SKILLS:
        if skill in description.lower():
            # Check if skill already exists in the database
            skill_entry = Skill.query.filter_by(skill_name=skill).first()
            if skill_entry:
                skill_entry.mention_count += 1
            else:
                new_skill = Skill(skill_name=skill, mention_count=1)
                db.session.add(new_skill)
            db.session.commit()










@app.route('/skills', methods=['GET'])
def get_skills():
    skills = Skill.query.order_by(Skill.mention_count.desc()).all()
    result = [{'skill_name': s.skill_name, 'mention_count': s.mention_count} for s in skills]
    return jsonify(result)


@app.route('/compare-skills', methods=['POST'])
def compare_skills():
    user_skills = request.form.getlist('skills')  # Get list from form checkboxes
    
    matched_skills = Skill.query.filter(Skill.skill_name.in_(user_skills)).all()
    
    top_skills = Skill.query.order_by(Skill.mention_count.desc()).limit(10).all()
    user_top_skills = [s for s in top_skills if s.skill_name in user_skills]
    
    return render_template('results.html', 
                           total_top_skills=len(top_skills), 
                           user_top_skills_count=len(user_top_skills), 
                           user_top_skills=[s.skill_name for s in user_top_skills])


@app.route('/input-skills', methods=['GET'])
def input_skills():
    skills = Skill.query.all()
    return render_template('input_skills.html', skills=skills)


@app.route('/')
def index():
    return "Hello, World!"





with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
