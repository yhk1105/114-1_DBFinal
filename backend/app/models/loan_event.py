from app.extensions import db

class LoanEvent(db.Model):
    __tablename__ = "loan_event"
    timestamp = db.Column(db.BigInteger, primary_key=True, nullable=False)
    event_type = db.Column(db.String(10), primary_key=True)
    l_id = db.Column(db.BigInteger, primary_key=True)