from project import db
from sqlalchemy import desc


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(400), index=True)
    status = db.Column(db.String(20), index=True)

    @staticmethod
    def get_all():
        return Task.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_max_id_record():
        return Task.query.order_by(desc(Task.id)).first()

    def __repr__(self):
        return '<Task %r>' % self.title
