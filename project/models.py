from project import db
from sqlalchemy import desc
from datetime import datetime


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)
    comment = db.Column(db.String(200))
    release = db.Column(db.Integer)
    category = db.Column(db.Integer)
    minutes = db.Column(db.Integer, default=0)
    start_timestamp = db.Column(db.DateTime)
    end_timestamp = db.Column(db.DateTime)
    update_timestamp = db.Column(db.DateTime, default=datetime.utcnow())

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
