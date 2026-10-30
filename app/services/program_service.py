from app.db import db
from app.models.program import Program


def create_program(name: str, organization_id: str):
    if Program.query.filter_by(name=name, organization_id=organization_id).first():
        return None, 'Program already exists'
    program = Program(name=name, organization_id=organization_id)
    db.session.add(program)
    db.session.commit()
    return program, None


def get_all_programs(organization_id: str):
    return Program.query.filter_by(organization_id=organization_id).all()
