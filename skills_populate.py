from app2 import app, db, Job, Skill, JobSkillAssociation 


SKILLS = [
    "python", "r", "sql", "machine learning", "deep learning", "tensorflow",
    "pytorch", "tableau", "excel", "hadoop", "spark", "statistical modeling",
    "nlp", "natural language processing", "computer vision", "algorithms",
    "sas", "scala", "java", "c++", "power bi", "phd", "master's", "spss", "github",
    "time series", "numpy", "matplotlib", "agile", "data engineering", "gcp", "aws",
    "pandas", "multivariate", "data mining"
]

def initialize_skills_table():
    """
    Initialize the Skills table with our predefined list of skills. 
    Only add skills that are not already in the table.
    """
    for skill in SKILLS:
        if not Skill.query.filter_by(skill_name=skill).first():
            new_skill = Skill(skill_name=skill)
            db.session.add(new_skill)
    db.session.commit()


def update_skill_counts():
    """
    Update the mention_count for each skill based on the Jobs table descriptions and 
    populate the counts for each job and company.
    """
    for job in Job.query.all():
        # DEBUG: Print the role_name of each job being processed.
        print(f"Processing job with role_name: {job.role_name}")
        
        job_description = job.description.lower()
        
        for skill in SKILLS:
            skill_entry = Skill.query.filter_by(skill_name=skill).first()

            if skill_entry and skill in job_description:
                # Global Count
                skill_entry.mention_count += 1
                
                # Job-Specific Count
                job_association = JobSkillAssociation.query.filter_by(role_name=job.role_name, skill_id=skill_entry.skill_id).first()
                
                if not job_association:
                    # DEBUG: Print the role and skill for which a new association is being created.
                    print(f"Creating association for role: {job.role_name}, skill: {skill}")
                    
                    job_association = JobSkillAssociation(role_name=job.role_name, skill_id=skill_entry.skill_id, count=0)
                    db.session.add(job_association)
                job_association.count += 1

                # Company-Specific Count
                #company_association = CompanySkillAssociation.query.filter_by(company_name=job.company_name, skill_id=skill_entry.skill_id).first()
                #if not company_association:
                #    company_association = CompanySkillAssociation(company_name=job.company_name, skill_id=skill_entry.skill_id, count=0)
                #    db.session.add(company_association)
                #company_association.count += 1
                
    db.session.commit()



if __name__ == '__main__':
    with app.app_context():
        initialize_skills_table()
        update_skill_counts()
