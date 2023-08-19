from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify, url_for, redirect
from sqlalchemy.exc import SQLAlchemyError
from models import Job, Skill, db
from models import app
import os


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
    try:
        skills = Skill.query.all()
        if not skills: 
            print("No skills found in the database")
        return render_template('input_skills.html', skills=skills)
    except SQLAlchemyError as e:
        print(f"Error querying the database: {e}")
        return "Error fetching skills from the database", 500     


@app.route('/')
def index():
    return redirect(url_for('input_skills'))


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
