from app.extensions import db

class PickUpPlace(db.Model):
    __tablename__ = "pick_up_place"
    p_id = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(200))
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
