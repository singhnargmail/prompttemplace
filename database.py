from models import db, PromptDef, PromptDefVer
from flask import Flask
import os

def init_database(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

def get_database_url():
    """Get database URL from environment variable"""
    return os.environ.get('DATABASE_URL', 'postgresql://sootro:dev_password@localhost:5432/sootro_metadata')

def create_sample_data():
    """Create sample data for testing"""
    # Check if data already exists
    if PromptDef.query.first():
        print("Sample data already exists, skipping creation.")
        return
    
    # Create sample prompt definitions
    persona_prompt = PromptDef(prompt_type='persona prompt')
    advanced_prompt = PromptDef(prompt_type='advanced prompt')
    
    db.session.add(persona_prompt)
    db.session.add(advanced_prompt)
    db.session.flush()  # Flush to get IDs
    
    with open("llm_debug_advanced_prompts.json", 'r') as f:
        advanced_prommpt_value= f.read()
    with open("llm_debug_prompts_refined_cot_markdown.json", 'r') as f:
        persona_prompt_value = f.read()

    # Create sample versions
    persona_ver1 = PromptDefVer(
        prompt_id=persona_prompt.id,
        prompt_value= persona_prompt_value,
        status='Active',
        version=1,
        published_by='system'
    )
    
    
    advanced_ver1 = PromptDefVer(
        prompt_id=advanced_prompt.id,
        prompt_value= advanced_prommpt_value,
        status='Active',
        version=1,
        published_by='system'
    )
    
    db.session.add_all([persona_ver1, advanced_ver1])
    db.session.commit()
    
    print("Sample data created successfully!")