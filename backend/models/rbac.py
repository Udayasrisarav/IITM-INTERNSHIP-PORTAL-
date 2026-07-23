from database import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    mappings = db.relationship("RoleMapping", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role id={self.id} role_name='{self.role_name}'>"


class Module(db.Model):
    __tablename__ = "modules"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    module_id = db.Column(db.String(50), nullable=True)
    module_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    mappings = db.relationship("RoleMapping", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module id={self.id} module_name='{self.module_name}'>"


class RoleMapping(db.Model):
    __tablename__ = "role_mapping"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    role_id = db.Column(db.BigInteger, db.ForeignKey("roles.id"), nullable=False)
    module_id = db.Column(db.BigInteger, db.ForeignKey("modules.id"), nullable=False)
    can_read = db.Column(db.Boolean, default=False, nullable=True)
    can_update = db.Column(db.Boolean, default=False, nullable=True)
    can_delete = db.Column(db.Boolean, default=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    role = db.relationship("Role", back_populates="mappings")
    module = db.relationship("Module", back_populates="mappings")
    users = db.relationship("User", back_populates="role_mapping")

    def __repr__(self):
        return f"<RoleMapping id={self.id} role_id={self.role_id} module_id={self.module_id}>"
