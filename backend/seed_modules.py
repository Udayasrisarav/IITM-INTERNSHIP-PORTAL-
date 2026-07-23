from app import app
from database import db
from models import Module, Role, RoleMapping

MODULES_DATA = [
    {"code": "PROFILES", "name": "PROFILES", "description": "Applicant Profile Management"},
    {"code": "APPLICATIONS", "name": "APPLICATIONS", "description": "Internship Applications Management"},
    {"code": "REVIEWS", "name": "REVIEWS", "description": "Supervisor & Chairman Application Reviews"},
    {"code": "DOCUMENTS", "name": "DOCUMENTS", "description": "Application Documents Management"},
    {"code": "USERS", "name": "USERS", "description": "User Account Management"},
    {"code": "SYSTEM_SETTINGS", "name": "SYSTEM_SETTINGS", "description": "System Configuration & Audit Logs"},
]

# Matrix definition: (Role, ModuleCode) -> (can_read, can_update, can_delete)
PERMISSIONS_MATRIX = {
    ("SuperAdmin", "PROFILES"): (True, True, True),
    ("SuperAdmin", "APPLICATIONS"): (True, True, True),
    ("SuperAdmin", "REVIEWS"): (True, True, True),
    ("SuperAdmin", "DOCUMENTS"): (True, True, True),
    ("SuperAdmin", "USERS"): (True, True, True),
    ("SuperAdmin", "SYSTEM_SETTINGS"): (True, True, True),

    ("Chairman", "PROFILES"): (True, False, False),
    ("Chairman", "APPLICATIONS"): (True, True, False),
    ("Chairman", "REVIEWS"): (True, True, False),
    ("Chairman", "DOCUMENTS"): (True, False, False),

    ("Supervisor", "PROFILES"): (True, False, False),
    ("Supervisor", "APPLICATIONS"): (True, True, False),
    ("Supervisor", "REVIEWS"): (True, True, False),
    ("Supervisor", "DOCUMENTS"): (True, False, False),

    ("Applicant", "PROFILES"): (True, True, False),
    ("Applicant", "APPLICATIONS"): (True, True, True),
    ("Applicant", "DOCUMENTS"): (True, True, True),
}

def seed_modules():
    with app.app_context():
        print("Seeding Modules & Role Mappings...")
        module_map = {}
        for m_data in MODULES_DATA:
            module = Module.query.filter(
                (Module.module_name == m_data["name"]) | (Module.module_id == m_data["code"])
            ).first()
            if not module:
                module = Module(module_id=m_data["code"], module_name=m_data["name"], description=m_data["description"])
                db.session.add(module)
                db.session.flush()
                print(f"  + Added Module: {m_data['name']}")
            module_map[m_data["code"]] = module

        db.session.commit()

        # Seed role_mapping entries
        roles = Role.query.all()
        role_dict = {r.role_name: r for r in roles}

        for (role_name, mod_code), (can_r, can_u, can_d) in PERMISSIONS_MATRIX.items():
            role_obj = role_dict.get(role_name)
            mod_obj = module_map.get(mod_code)
            if role_obj and mod_obj:
                mapping = RoleMapping.query.filter_by(role_id=role_obj.id, module_id=mod_obj.id).first()
                if not mapping:
                    mapping = RoleMapping(
                        role_id=role_obj.id,
                        module_id=mod_obj.id,
                        can_read=can_r,
                        can_update=can_u,
                        can_delete=can_d
                    )
                    db.session.add(mapping)
                    print(f"  + Added RoleMapping: Role='{role_name}' -> Module='{mod_code}' (R:{can_r}, U:{can_u}, D:{can_d})")

        db.session.commit()
        print("Modules & Role Mappings seeding complete!")

if __name__ == "__main__":
    seed_modules()
