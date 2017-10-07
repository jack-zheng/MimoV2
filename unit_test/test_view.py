import json
import unittest

from project import app, db, models
from config import basedir
import os, time


class ViewTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

        self.prepare_data()

        self.item01 = '{"title":"first target"}'

        self.item02 = '{"title": "second target", "description": "my 2 target"}'

        self.item_deletion = {'id': 1}

        # prepare a dynamic task for test
        self.get_time_milli = lambda: int(round(time.time() * 1000))
        self.rand_task = '{"title":"%s"}' % str(self.get_time_milli())

    @staticmethod
    def prepare_data():
        # insert some tasks for test
        task1 = models.Task(id=1, title='t1', desc='desc1', status='In Progress')
        task2 = models.Task(id=2, title='t2', desc='desc2', status='In Progress')
        db.session.add(task1)
        db.session.add(task2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # create a hello test as a start
    def test_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.data.decode('utf-8'), 'Hello World')

    # Post
    def test_post_list(self):
        rand_task_json = json.loads(self.rand_task)
        resp = self.app.post('/todo/api/v1/tasks', data=self.rand_task, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)
        self.assertIn(rand_task_json['title'], str(resp.data))

        query_ret = models.Task.query.filter_by(title=rand_task_json['title']).first()
        self.assertTrue(query_ret)

    # Get all
    def test_get_list(self):
        resp = self.app.get('/todo/api/v1/tasks')
        self.assertEqual(resp.status_code, 200)
        ret = json.loads(resp.data)

        # get query count of db and compare
        count = models.Task.query.count()
        self.assertEqual(count, len(json.loads(resp.data)))

    # Get one
    def test_get_list_by_id(self):
        query_id = self.get_task_id()
        resp = self.app.get('/todo/api/v1/tasks/{}'.format(str(query_id)))
        self.assertEqual(resp.status_code, 200)

    # Update
    def test_update_list(self):
        update_id = self.get_task_id()
        time_milli = str(self.get_time_milli())
        update_task = '{"id": %s, "title": "%s"}' % (update_id, time_milli)
        resp = self.app.put('/todo/api/v1/tasks', data=update_task, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)

        # query db and the update one is exiting
        query_ret = models.Task.query.filter_by(id=update_id).first()
        self.assertEqual(query_ret.title, time_milli)

    # Delete
    def test_list_deletion(self):
        find_id = self.get_task_id()
        resp = self.app.delete('/todo/api/v1/tasks/{}'.format(find_id))
        self.assertEqual(resp.status_code, 200)

        # query db and check the task with special id has been deleted
        query_ret = models.Task.query.filter_by(id=find_id).first()
        self.assertFalse(query_ret)

    # get existing task id for test, using when delete, update testing
    @staticmethod
    def get_task_id():
        id_ret = models.Task.query.with_entities(models.Task.id).first()
        return id_ret.id


if __name__ == '__main__':
    unittest.main()