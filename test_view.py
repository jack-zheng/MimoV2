import json
import unittest

from project import app, db, models
from config import basedir
import os, time


class ViewTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("invoke setupclass")
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        db.create_all()
        cls.prepare_data()

    # set up will be invoked every time test method run
    def setUp(self):
        self.app = app.test_client()

        self.item01 = '{"title":"first target"}'
        self.item02 = '{"title": "second target", "desc": "my 2 target"}'
        self.full_entity = '{"title": "full entity", "desc": "desc full", "status": "Done", "time": 2.0,\
                       "category": 2}'
        self.full_entity_update = '{"id": id_replace, "title": "full entity", "desc": "desc update",\
         "status": "Block", "time": 100.0, "category": 100}'

        # prepare a dynamic task for test
        self.get_time_milli = lambda: int(round(time.time() * 1000))

    @staticmethod
    def prepare_data():
        print("prepare data method invoked");
        # insert some tasks for test
        task1 = models.Task(title='t1', desc='desc1', status='In Progress')
        task2 = models.Task(title='t2', desc='desc2', status='In Progress')
        db.session.add(task1)
        db.session.add(task2)
        db.session.commit()

    # tear down will invoked every test method run
    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        print("tear down class invoked");
        db.session.remove()
        db.drop_all()

    # create a hello test as a start
    def test_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.data.decode('utf-8'), 'Hello World')

    # Post
    def test_post_list(self):
        rand_full_entity = self.full_entity.replace('full entity', str(self.get_time_milli()))
        rand_full_json = json.loads(rand_full_entity)
        resp = self.app.post('/todo/api/v1/tasks', data=rand_full_entity, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)

        # iterate dict and assert resp contains value
        for key in rand_full_json:
            self.assertIn(str(rand_full_json[key]), str(resp.data))

        query_ret = models.Task.query.filter_by(title=rand_full_json['title']).first()
        for key in rand_full_json:
            self.assertEqual(query_ret.__getattribute__(key), rand_full_json[key], "attribute: %s, entity value: %s"\
                             % (query_ret.__getattribute__(key), rand_full_json[key]))

    # Get all
    def test_get_list(self):
        resp = self.app.get('/todo/api/v1/tasks')
        self.assertEqual(resp.status_code, 200)

        # get query count of db and compare
        count = models.Task.query.count()
        self.assertEqual(count, len(json.loads(resp.data)))

    # Get one
    def test_get_list_by_id(self):
        query_id = self.get_task_id()
        resp = self.app.get('/todo/api/v1/tasks/{}'.format(str(query_id)))
        self.assertEqual(resp.status_code, 200)
        json_resp = json.loads(resp.data)

        # assert every field in db is contains in response
        query_task = models.Task.query.filter_by(id=query_id).first();
        for column in query_task.__table__._columns:
            self.assertEqual(query_task.__getattribute__(column.key), json_resp[column.key])

    # Update
    def test_update_list(self):
        update_id = self.get_task_id()
        update_task = self.full_entity_update.replace("id_replace", str(update_id))
        json_update = json.loads(update_task)
        resp = self.app.put('/todo/api/v1/tasks', data=update_task, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)

        # query db and the update one is exiting
        query_ret = models.Task.query.filter_by(id=update_id).first()
        for column in query_ret.__table__._columns:
            self.assertEqual(query_ret.__getattribute__(column.key), json_update[column.key])

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
