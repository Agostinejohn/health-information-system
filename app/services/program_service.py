from app.db import db
from app.models.program import Program

def create_program(name: str):
    if Program.query.filter_by(name=name).first():
        return None, 'Program already exists'
    program = Program(name=name)
    db.session.add(program)
    db.session.commit()
    return program, None

def get_all_programs():
    return Program.query.all()
