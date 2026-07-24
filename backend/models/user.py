from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(255), nullable=True)
    role_mapping_id = db.Column(db.Integer, db.ForeignKey("role_mapping.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # 1:1 Relationship to Profile (User -> Profile)
    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Relationships
    role_mapping = db.relationship("RoleMapping", back_populates="users")
    reviews = db.relationship("Review", foreign_keys="Review.supervisor_id", back_populates="supervisor")
    approvals = db.relationship("Approval", foreign_keys="Approval.chairman_id", back_populates="chairman")
    schedules_created = db.relationship("InternshipSchedule", foreign_keys="InternshipSchedule.created_by", back_populates="creator")

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}'>"
