from database import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    application_id = db.Column(db.BigInteger, db.ForeignKey("applications.id"), nullable=False)
    supervisor_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    recommendation = db.Column(db.String(50), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    application = db.relationship("Application", back_populates="reviews")
    supervisor = db.relationship("User", foreign_keys=[supervisor_id], back_populates="reviews")

    def __repr__(self):
        return f"<Review id={self.id} app_id={self.application_id} supervisor_id={self.supervisor_id}>"
