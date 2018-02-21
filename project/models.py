from project import db
from sqlalchemy import desc


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(200), index=True)
    status = db.Column(db.String(20), index=True)
    time = db.Column(db.Float, default=0.0)
    timeperiod = db.Column(db.String(20), index=True)
    category = db.Column(db.Integer)
    release = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)

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


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(20))
    comments = db.Column(db.String(64))
    category_index = db.Column(db.Integer)

    def __repr__(self):
        return '<Category{id: %s, name: %s, comments: %s}>' \
               % (self.id, self.category_name, self.comments)
