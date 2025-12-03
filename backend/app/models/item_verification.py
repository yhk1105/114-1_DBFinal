from app.extensions import db

class ItemVerification(db.Model):
    __tablename__ = "item_verification"
    iv_id = db.Column(db.Integer, primary_key=True)
    v_conclusion = db.Column(db.String(10), nullable=True)
    create_at = db.Column(db.DateTime, nullable=False)
    i_id = db.Column(db.Integer, db.ForeignKey("item.i_id"), nullable=False)
    s_id = db.Column(db.Integer, db.ForeignKey("staff.s_id"), nullable=False)