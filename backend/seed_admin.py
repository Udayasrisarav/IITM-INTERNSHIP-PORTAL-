from app import app
from database import db
from models import User, Role, Module, RoleMapping, Profile
from utils.password_utils import hash_password

def seed_admin():
    with app.app_context():
        print("Seeding SuperAdmin User...")
        
        # Ensure SuperAdmin role and USERS module mapping exist
        superadmin_role = Role.query.filter_by(role_name="Superadmin").first()
        if not superadmin_role:
            superadmin_role = Role(role_name="Superadmin", description="System administrator role")
            db.session.add(superadmin_role)
            db.session.flush()

        users_module = Module.query.filter(
            (Module.module_name == "USERS") | (Module.module_id == "USERS")
        ).first()
        if not users_module:
            users_module = Module(module_id="USERS", module_name="USERS", description="User Account Management")
            db.session.add(users_module)
            db.session.flush()

        role_mapping = RoleMapping.query.filter_by(
            role_id=superadmin_role.id, module_id=users_module.id
        ).first()
        if not role_mapping:
            role_mapping = RoleMapping(
                role_id=superadmin_role.id,
                module_id=users_module.id,
                can_read=True,
                can_update=True,
                can_delete=True
            )
            db.session.add(role_mapping)
            db.session.flush()

        # Create or update SuperAdmin User
        admin_email = "superadmin@iitm.ac.in"
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                username="admin",
                password_hash=hash_password("SuperAdminPass123!"),
                role_mapping_id=role_mapping.id,
                is_active=True
            )
            db.session.add(admin_user)
            db.session.flush()

            # Create SuperAdmin profile
            profile = Profile(
                user_id=admin_user.id,
                full_name="System SuperAdmin",
                department="Central Administration"
            )
            db.session.add(profile)
            print(f"  + Created SuperAdmin User: {admin_email} (Username: 'admin', Password: 'SuperAdminPass123!')")
        else:
            print(f"  = SuperAdmin user '{admin_email}' already exists.")

        db.session.commit()
        print("SuperAdmin seeding complete!")

if __name__ == "__main__":
    seed_admin()
