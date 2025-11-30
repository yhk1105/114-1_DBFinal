from app.extensions import db

class Item(db.Model):
    __tablename__ = "item"
    i_id = db.Column(db.Integer, primary_key=True)
    i_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    out_duration = db.Column(db.Integer, nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey("member.m_id"), nullable=False)
    c_id = db.Column(db.Integer, db.ForeignKey("category.c_id"), nullable=False)