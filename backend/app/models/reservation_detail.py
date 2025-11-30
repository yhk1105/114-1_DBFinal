from app.extensions import db

class ReservationDetail(db.Model):
    __tablename__ = "reservation_detail"
    rd_id = db.Column(db.Integer, primary_key=True)
    est_start_at = db.Column(db.DateTime, nullable=False)
    est_due_at = db.Column(db.DateTime, nullable=False)
    r_id = db.Column(db.Integer, db.ForeignKey("reservation.r_id"), nullable=False)
    i_id = db.Column(db.Integer, db.ForeignKey("item.i_id"), nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey("pick_up_place.p_id"), nullable=False)
