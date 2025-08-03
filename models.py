from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

db = SQLAlchemy()

class PromptDef(db.Model):
    __tablename__ = 'prompt_def'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt_type = db.Column(db.String(255), nullable=False)
    createddate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    versions = db.relationship('PromptDefVer', backref='prompt_def', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PromptDef {self.id}: {self.prompt_type}>'

class PromptDefVer(db.Model):
    __tablename__ = 'prompt_def_ver'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt_def.id'), nullable=False)
    prompt_value = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='draft', nullable=False)
    published_date = db.Column(db.DateTime, nullable=True)
    published_by = db.Column(db.String(255), nullable=True)
    createddate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    
    __table_args__ = (
        db.CheckConstraint("status IN ('draft', 'Active', 'Inactive')", name='check_status'),
    )
    
    def __repr__(self):
        return f'<PromptDefVer {self.id}: {self.status} v{self.version}>'

# Marshmallow schemas for serialization
class PromptDefSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PromptDef
        load_instance = True
        include_relationships = True
    
    versions = fields.Nested('PromptDefVerSchema', many=True, exclude=['prompt_def'])

class PromptDefVerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PromptDefVer
        load_instance = True
    
    prompt_def = fields.Nested('PromptDefSchema', exclude=['versions'])

# Schema instances
prompt_def_schema = PromptDefSchema()
prompt_defs_schema = PromptDefSchema(many=True)
prompt_def_ver_schema = PromptDefVerSchema()
prompt_def_vers_schema = PromptDefVerSchema(many=True)