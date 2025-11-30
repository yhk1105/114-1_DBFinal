from app.extensions import db

class Member(db.Model):
    __tablename__ = "member"

    m_id = db.Column(db.Integer, primary_key=True)
    m_mail = db.Column(db.String(120), unique=True, nullable=False)
    m_name = db.Column(db.String(50), nullable=False)
    m_password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)