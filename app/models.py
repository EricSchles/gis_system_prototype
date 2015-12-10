try:
    from app import db
except ImportError:
    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db" #os.environ["DATABASE_URL"]
    db = SQLAlchemy(app)


class AddressLogger(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float(0))
    long = db.Column(db.Float(0))

    def __init__(self,lat=0.0,long=0.0):
        self.lat = lat
        self.long = long
    def __repr__(self):
        return '<lat_long %r>' % str(self.lat)+","+str(self.long)

