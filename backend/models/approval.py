from database import db
from datetime import datetime

class Approval(db.Model):
    __tablename__ = "approvals"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    application_id = db.Column(db.BigInteger, db.ForeignKey("applications.id"), nullable=False)
    chairman_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    decision = db.Column(db.String(50), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    approved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    application = db.relationship("Application", back_populates="approvals")
    chairman = db.relationship("User", foreign_keys=[chairman_id], back_populates="approvals")

    def __repr__(self):
        return f"<Approval id={self.id} app_id={self.application_id} chairman_id={self.chairman_id}>"
