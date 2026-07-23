from database import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    application_id = db.Column(db.BigInteger, db.ForeignKey("applications.id"), nullable=False)
    document_type = db.Column(db.String(100), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # 1:N Relationship back to Application
    application = db.relationship("Application", back_populates="documents")

    def __repr__(self):
        return f"<Document id={self.id} type='{self.document_type}' application_id={self.application_id}>"
