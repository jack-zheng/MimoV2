from project import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(400), index=True)
    status = db.Column(db.String(20), index=True)

    def __repr__(self):
        return '<Task %r>' % self.title
