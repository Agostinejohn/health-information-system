from app.db import db
from app.models.program import Program


def create_program(name: str, organization_id: str, **fields):
    if Program.query.filter_by(name=name, organization_id=organization_id).first():
        return None, 'Program already exists'
    program = Program(name=name, organization_id=organization_id, **fields)
    db.session.add(program)
    db.session.commit()
    return program, None


def get_program(program_id: str, organization_id: str):
    return Program.query.filter_by(id=program_id, organization_id=organization_id).first()


def update_program(program: Program, changes: dict):
    if 'name' in changes:
        existing = Program.query.filter(
            Program.organization_id == program.organization_id,
            Program.id != program.id,
            Program.name == changes['name']
        ).first()
        if existing:
            return None, 'Program already exists'
    for key, value in changes.items():
        setattr(program, key, value)
    db.session.commit()
    return program, None


def get_all_programs(organization_id: str):
    return Program.query.filter_by(organization_id=organization_id).all()
