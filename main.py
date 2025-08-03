#!/usr/bin/env python3
"""
Prompt Management Application
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models import db, PromptDef, PromptDefVer, prompt_def_schema, prompt_defs_schema, prompt_def_ver_schema
from database import init_database, get_database_url, create_sample_data
from datetime import datetime
import os
from dotenv import load_dotenv
import json
# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_database(app)

# Web UI Routes
@app.route('/')
def index():
    """Main page showing all prompt definitions"""
    prompt_defs = PromptDef.query.all()
    return render_template('index.html', prompt_defs=prompt_defs)

@app.route('/prompt/<int:prompt_id>')
def prompt_detail(prompt_id):
    """Detail page for a specific prompt definition"""
    prompt_def = PromptDef.query.get_or_404(prompt_id)
    versions = PromptDefVer.query.filter_by(prompt_id=prompt_id).order_by(PromptDefVer.version.desc()).all()
    return render_template('prompt_detail.html', prompt_def=prompt_def, versions=versions)

@app.route('/version/<int:version_id>')
def version_detail(version_id):
    """Detail page for a specific prompt version"""
    version = PromptDefVer.query.get_or_404(version_id)
    return render_template('version_detail.html', version=version)

@app.route('/create_prompt', methods=['GET', 'POST'])
def create_prompt():
    """Create new prompt definition with initial version"""
    if request.method == 'POST':
        prompt_type = request.form.get('prompt_type')
        prompt_value = request.form.get('prompt_value')
        
        if not prompt_type or not prompt_value:
            flash('Both prompt type and prompt value are required!', 'error')
            return render_template('create_prompt.html')
        
        if prompt_type not in ['persona prompt', 'advanced prompt']:
            flash('Invalid prompt type!', 'error')
            return render_template('create_prompt.html')
        
        try:
            # Create prompt definition
            prompt_def = PromptDef(prompt_type=prompt_type)
            db.session.add(prompt_def)
            db.session.flush()
            
            # Create initial version
            version = PromptDefVer(
                prompt_id=prompt_def.id,
                prompt_value=prompt_value,
                status='draft',
                version=1
            )
            db.session.add(version)
            db.session.commit()
            
            flash('Prompt created successfully!', 'success')
            return redirect(url_for('prompt_detail', prompt_id=prompt_def.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating prompt: {str(e)}', 'error')
    
    return render_template('create_prompt.html')

@app.route('/edit_version/<int:version_id>', methods=['GET', 'POST'])
def edit_version(version_id):
    """Edit prompt version (only if status is draft)"""
    version = PromptDefVer.query.get_or_404(version_id)
    
    if version.status != 'draft':
        flash('Only draft versions can be edited!', 'error')
        return redirect(url_for('version_detail', version_id=version_id))
    
    if request.method == 'POST':
        prompt_value = request.form.get('prompt_value')
        
        if not prompt_value:
            flash('Prompt value is required!', 'error')
            return render_template('edit_version.html', version=version)
        
        try:
            version.prompt_value = prompt_value
            db.session.commit()
            flash('Version updated successfully!', 'success')
            return redirect(url_for('version_detail', version_id=version_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating version: {str(e)}', 'error')
    
    return render_template('edit_version.html', version=version)

@app.route('/publish_version/<int:version_id>', methods=['POST'])
def publish_version(version_id):
    """Publish a draft version and deactivate others"""
    version = PromptDefVer.query.get_or_404(version_id)
    
    if version.status != 'draft':
        flash('Only draft versions can be published!', 'error')
        return redirect(url_for('version_detail', version_id=version_id))
    
    published_by = request.form.get('published_by', 'system')
    
    try:
        # Deactivate all other versions of the same prompt
        PromptDefVer.query.filter_by(prompt_id=version.prompt_id).filter(
            PromptDefVer.id != version_id
        ).update({'status': 'Inactive'})
        
        # Activate current version
        version.status = 'Active'
        version.published_date = datetime.utcnow()
        version.published_by = published_by
        
        db.session.commit()
        flash('Version published successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error publishing version: {str(e)}', 'error')
    
    return redirect(url_for('version_detail', version_id=version_id))

@app.route('/create_version/<int:prompt_id>', methods=['POST'])
def create_version(prompt_id):
    """Create a new version for an existing prompt definition"""
    prompt_def = PromptDef.query.get_or_404(prompt_id)
    
    try:
        # Get the highest version number for this prompt
        max_version = db.session.query(db.func.max(PromptDefVer.version)).filter_by(prompt_id=prompt_id).scalar()
        next_version = (max_version or 0) + 1
        
        # Create new version with draft status and blank prompt value
        new_version = PromptDefVer(
            prompt_id=prompt_id,
            prompt_value='',  # Blank prompt value
            status='draft',
            version=next_version
        )
        
        db.session.add(new_version)
        db.session.commit()
        
        flash(f'New version {next_version} created successfully!', 'success')
        return redirect(url_for('edit_version', version_id=new_version.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating new version: {str(e)}', 'error')
        return redirect(url_for('prompt_detail', prompt_id=prompt_id))

# API Routes for external services
@app.route('/api/getPersonaPrompts', methods=['GET'])
def get_persona_prompts():
    """API endpoint to get active persona prompts"""
    try:
        active_versions = db.session.query(PromptDefVer).join(PromptDef).filter(
            PromptDef.prompt_type == 'persona prompt',
            PromptDefVer.status == 'Active'
        ).all()
        
        prompt_values = [version.prompt_value for version in active_versions]
        #modify to return just the json string
        json_string = prompt_values[0]
        #modify to return just the json string
        return json_string
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/getAdvancedPrompts', methods=['GET'])
def get_advanced_prompts():
    """API endpoint to get active advanced prompts"""
    try:
        active_versions = db.session.query(PromptDefVer).join(PromptDef).filter(
            PromptDef.prompt_type == 'advanced prompt',
            PromptDefVer.status == 'Active'
        ).all()
        
        prompt_values = [version.prompt_value for version in active_versions]
        #modify to return just the json string
        json_string = prompt_values[0]
        return json_string
        #return prompt_values
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

def main():
    """Main application function"""
    with app.app_context():
        # Create sample data on first run
        create_sample_data()
    
    print("Starting Prompt Management Application...")
    print(f"Database URL: {get_database_url()}")
    print("Access the application at: http://localhost:5000")
    print("API endpoints:")
    print("  - GET /api/getPersonaPrompts")
    print("  - GET /api/getAdvancedPrompts")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()