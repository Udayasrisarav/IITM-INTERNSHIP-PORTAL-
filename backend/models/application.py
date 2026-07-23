from database import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.BigInteger, db.ForeignKey("profiles.id"), nullable=False)
    schedule_id = db.Column(db.BigInteger, db.ForeignKey("internship_schedules.id"), nullable=True)
    application_number = db.Column(db.String(50), nullable=True)
    referred_by = db.Column(db.String(150), nullable=True)
    # Referral source (Planned Enum enhancement: "Within IIT", "Outside IIT")
    referred_from = db.Column(db.String(50), nullable=True)
    
    # Application status (Planned Enum enhancement: "Draft", "Submitted", "Under Review", "Approved", "Rejected")
    status = db.Column(db.String(50), default="Draft", nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # 1:N Relationship back to Profile
    profile = db.relationship("Profile", back_populates="applications")

    # Relationship to InternshipSchedule
    schedule = db.relationship("InternshipSchedule", back_populates="applications")

    # 1:1 Relationship to BankDetails (Application -> Bank Details)
    bank_details = db.relationship("BankDetails", back_populates="application", uselist=False, cascade="all, delete-orphan")

    # 1:N Relationship to Documents (Application -> Documents)
    documents = db.relationship("Document", back_populates="application", cascade="all, delete-orphan")

    # 1:N Relationship to Reviews
    reviews = db.relationship("Review", back_populates="application", cascade="all, delete-orphan")

    # 1:N Relationship to Approvals
    approvals = db.relationship("Approval", back_populates="application", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Application id={self.id} app_number='{self.application_number}' status='{self.status}'>"
