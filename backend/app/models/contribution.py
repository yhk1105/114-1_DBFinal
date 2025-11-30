from app.extensions import db

class Contribution(db.Model):
    __tablename__ = "contribution"
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"), primary_key=True)
    i_id = db.Column(db.Integer, db.ForeignKey("item.i_id"), primary_key=True)
    is_active = db.Column(db.Boolean, default=False)