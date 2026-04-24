from app.db import db
from app.models.client import Client
from app.models.program import Program

def register_client(name: str, age: int):
    client = Client(name=name, age=age)
    db.session.add(client)
    db.session.commit()
    return client

def search_clients(name_query: str):
    return Client.query.filter(Client.name.ilike(f'%{name_query}%')).all()

def get_client(client_id: str):
    return db.session.get(Client, client_id)

def enroll_client(client_id: str, program_ids: list):
    client = db.session.get(Client, client_id)
    if not client:
        return None, 'Client not found'

    enrolled = []
    not_found = []

    for pid in program_ids:
        program = db.session.get(Program, pid)
        if not program:
            not_found.append(pid)
            continue
        if program not in client.programs:
            client.programs.append(program)
            enrolled.append(program.name)

    db.session.commit()
    return client, {'enrolled': enrolled, 'not_found': not_found}
