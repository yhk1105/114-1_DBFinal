from app.extensions import db

class Member(db.Model):
    __tablename__ = "member"

    m_id = db.Column(db.Integer, primary_key=True)
    u_mail = db.Column(db.String(120), unique=True, nullable=False)
    u_name = db.Column(db.String(50), nullable=False)
    u_password = db.Column(db.String(255), nullable=False)