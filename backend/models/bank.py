from database import db
from datetime import datetime

class BankDetails(db.Model):
    __tablename__ = "bank_details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False, unique=True)
    account_holder_name = db.Column(db.String(150), nullable=True)
    bank_name = db.Column(db.String(150), nullable=True)
    branch_name = db.Column(db.String(150), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    ifsc_code = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # 1:1 Relationship back to Application
    application = db.relationship("Application", back_populates="bank_details")

    def __repr__(self):
        return f"<BankDetails id={self.id} application_id={self.application_id}>"
