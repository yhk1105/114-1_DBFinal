from app.extensions import db


class Contribution(db.Model):
    __tablename__ = "contribution"
    m_id = db.Column(db.Integer, db.ForeignKey("member.m_id"),
                     primary_key=True, autoincrement=False)
    i_id = db.Column(db.Integer, db.ForeignKey("item.i_id"),
                     primary_key=True, autoincrement=False)
    is_active = db.Column(db.Boolean, default=False)
