from app import app
from database import db
from models import Role

ROLES_DATA = [
    {
        "name": "Applicant",
        "description": "Internship applicant role"
    },
    {
        "name": "Supervisor",
        "description": "Faculty supervisor reviewer role"
    },
    {
        "name": "Chairman",
        "description": "Department chairman final approval role"
    },
    {
        "name": "SuperAdmin",
        "description": "System administrator role"
    }
]

def seed_roles():
    with app.app_context():
        print("Seeding Roles...")
        for data in ROLES_DATA:
            role = Role.query.filter_by(role_name=data["name"]).first()
            if not role:
                role = Role(role_name=data["name"], description=data["description"])
                db.session.add(role)
                print(f"  + Added Role: {data['name']}")
            else:
                print(f"  = Role already exists: {data['name']}")
        db.session.commit()
        print("Roles seeding complete!")

if __name__ == "__main__":
    seed_roles()
