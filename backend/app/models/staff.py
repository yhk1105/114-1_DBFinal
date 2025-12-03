from app.extensions import db

class Staff(db.Model):
    __tablename__ = "staff"

    s_id = db.Column(db.Integer, primary_key=True)
    s_mail = db.Column(db.String(120), unique=True, nullable=False)
    s_name = db.Column(db.String(50), nullable=False)
    s_password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)


