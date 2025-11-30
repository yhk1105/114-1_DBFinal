from app.extensions import db

class Report(db.Model):
    __tablename__ = "report"
    re_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200), nullable=False)
    r_conclusion = db.Column(db.String(200), nullable=True)
    create_at = db.Column(db.DateTime, nullable=False)
    conclude_at = db.Column(db.DateTime, nullable=True)
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"), nullable=False)
    i_id = db.Column(db.Integer, db.ForeignKey("item.i_id"), nullable=False)
    s_id = db.Column(db.Integer, db.ForeignKey("staff.s_id"), nullable=False)