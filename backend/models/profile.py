from database import db
from datetime import datetime

class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    full_name = db.Column(db.String(150), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.Text, nullable=True)
    college_name = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(150), nullable=True)
    register_number = db.Column(db.String(100), nullable=True)
    year_of_study = db.Column(db.String(50), nullable=True)
    skills = db.Column(db.Text, nullable=True)
    area_of_interest = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # 1:1 Relationship back to User
    user = db.relationship("User", back_populates="profile")

    # 1:N Relationship to Applications (Profile -> Applications)
    applications = db.relationship("Application", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Profile id={self.id} user_id={self.user_id} full_name='{self.full_name}'>"
