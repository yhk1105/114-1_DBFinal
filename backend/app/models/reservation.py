from app.extensions import db

class Reservation(db.Model):
    __tablename__ = "reservation"
    r_id = db.Column(db.Integer, primary_key=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    create_at = db.Column(db.DateTime, nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey("member.m_id"), nullable=False)
