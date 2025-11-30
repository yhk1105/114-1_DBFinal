from app.extensions import db

class Category(db.Model):
    __tablename__ = "category"
    c_id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String(20), nullable=False)
    parent_c_id = db.Column(db.Integer, db.ForeignKey("category.c_id"))

