from database import db
from datetime import datetime

class InternshipSchedule(db.Model):
    __tablename__ = "internship_schedules"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    applications = db.relationship("Application", back_populates="schedule")
    creator = db.relationship("User", foreign_keys=[created_by], back_populates="schedules_created")

    def __repr__(self):
        return f"<InternshipSchedule id={self.id} title='{self.title}'>"
