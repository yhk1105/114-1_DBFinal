from app.extensions import db

class Review(db.Model):
    __tablename__ = "review"

    review_id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(200), nullable=False)
    reviewer_id = db.Column(db.Integer, nullable=False)
    reviewee_id = db.Column(db.Integer, nullable=False)
    l_id = db.Column(db.Integer, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)