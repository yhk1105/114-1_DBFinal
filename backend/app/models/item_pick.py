from app.extensions import db

class ItemPick(db.Model):
    __tablename__ = "item_pick"
    i_id = db.Column(db.Integer, db.ForeignKey("item.i_id"), primary_key=True)
    p_id = db.Column(db.Integer, db.ForeignKey("pick_up_place.p_id"), primary_key=True)
    is_deleted = db.Column(db.Boolean, default=False)
    