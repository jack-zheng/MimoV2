import json
import unittest

from project import app, db, models
from config import basedir
import os
from datetime import datetime
import sqlalchemy


class ViewTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("invoke setupclass")
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        db.create_all()

    # set up will be invoked every time test method run
    def setUp(self):
        self.app = app.test_client()

        self.full_entity = '{"title": "full entity", "comment": "comment full",\
                            "minutes": 60, "category": 2,\
                            "start": "2018-01-01 12:00",\
                            "end": "2018-01-01 13:00",\
                            "release": 1708, "updatetime":"2017-05-06 12:00"}'

        self.update_entity = '{"id": id_replace, "title": "title update", "comment": "comment full",\
                            "minutes": 60, "category": 2,\
                            "start": "2018-01-01 12:00",\
                            "end": "2018-01-01 13:00",\
                            "release": 1708, "updatetime":"2017-05-06 12:00"}'

        self.api_db_map = {'start': 'start_timestamp', 'end': 'end_timestamp', 'updatetime': 'update_timestamp'}
        self.time_format = "%Y-%m-%d %H:%M"

    @staticmethod
    def insert_one_test_record():
        t = models.Task(title='testing', comment='t comment',\
                        release=1708, category=1,\
                        minutes=60, start_timestamp=datetime.now(), \
                        end_timestamp=datetime.now(), update_timestamp=datetime.now())

        db.session.add(t)
        db.session.commit()

    # tear down will invoked every test method run
    def tearDown(self):
        models.Task.query.delete()
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        print("tear down class invoked");
        db.session.remove()
        db.drop_all()

    # create a hello test as a start
    def test_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.data.decode('utf-8'), 'Hello World')

    def test_default_update_time(self):
        """
        if not set the update time, the update time is utc now by default
        """
        title = 'update_time_testing'
        t = models.Task(title=title)
        db.session.add(t)
        db.session.commit()

        expected_time = datetime.utcnow()
        expected_time_str = expected_time.strftime("%Y-%m-%d %H:%M")
        query_ret = models.Task.query.filter_by(title=title).first().update_timestamp.strftime("%Y-%m-%d %H:%M")
        self.assertEqual(expected_time_str, query_ret)

    def test_title_nullable(self):
        """
        when there is no title attribute in task obj, insert will throw exception
        """
        t = models.Task(comment='c01')
        db.session.add(t)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.commit()

    # Post
    def test_post_list(self):
        full_json = json.loads(self.full_entity)
        resp = self.app.post('/todo/api/v1/tasks', data=self.full_entity, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)

        # iterate dict and assert resp contains value
        for key in full_json:
            self.assertIn(str(full_json[key]), str(resp.data))

        query_ret = models.Task.query.filter_by(id=1).first()

        for key in full_json:
            if key in self.api_db_map.keys():
                timestr = query_ret.__getattribute__(self.api_db_map.get(key))
                timestr = timestr.strftime("%Y-%m-%d %H:%M")
                self.assertEqual(timestr, full_json[key])
            else:
                self.assertEqual(full_json[key], query_ret.__getattribute__(key), "attribute: %s, entity value: %s"\
                             % (query_ret.__getattribute__(key), full_json[key]))

    def test_post_without_update_timestamp(self):
        """
        when no update timestamp set in request, use utc now as default value
        :return:
        """
        self.test_entity = '{"title": "no timestamp"}'
        resp = self.app.post('/todo/api/v1/tasks', data=self.test_entity, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)
        query_ret = models.Task.query.filter_by(id=1).first().update_timestamp.strftime(self.time_format)
        expected_timestr = datetime.utcnow().strftime(self.time_format)
        self.assertEqual(query_ret, expected_timestr)

        # add a test scenario when time is ""
        self.test_entity02 = '{"title": "empty timestamp", "updatetime":""}'
        resp = self.app.post('/todo/api/v1/tasks', data=self.test_entity02, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)
        query_ret = models.Task.query.filter_by(id=2).first().update_timestamp.strftime(self.time_format)
        expected_timestr = datetime.utcnow().strftime(self.time_format)
        self.assertEqual(query_ret, expected_timestr)

    # Get all
    def test_get_list(self):
        resp = self.app.get('/todo/api/v1/tasks')
        self.assertEqual(resp.status_code, 200)

        # get query count of db and compare
        count = models.Task.query.count()
        self.assertEqual(count, len(json.loads(resp.data)))

    # Get one
    def test_get_list_by_id(self):
        self.insert_one_test_record()
        resp = self.app.get('/todo/api/v1/tasks/1')
        self.assertEqual(resp.status_code, 200)
        json_resp = json.loads(resp.data)

        # assert every field in db is contains in response
        query_task = models.Task.query.filter_by(id=1).first();
        for column in query_task.__table__._columns:
            self.assertEqual(query_task.__getattribute__(column.key), json_resp[column.key])

    def test_empty_field_will_not_return(self):
        """
        if task field is empty, it will not present in json response
        """
        title = 'empty field test'
        t = models.Task(title=title)
        db.session.add(t)
        db.session.commit()
        ret_id = models.Task.query.filter_by(title=title).first()
        resp = self.app.get('/todo/api/v1/tasks/{}'.format(str(ret_id)))
        print(resp)
        self.assertTrue("comment" not in json.loads(resp.data))

    # Update
    def test_update_list(self):
        update_id = self.get_task_id()
        update_task = self.update_entity.replace("id_replace", str(update_id))
        json_update = json.loads(update_task)
        resp = self.app.put('/todo/api/v1/tasks', data=update_task, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)

        # query db and the update one is exiting
        query_ret = models.Task.query.filter_by(id=update_id).first()
        for column in query_ret.__table__._columns:
            if column.key == 'timestamp':
                pass
            else:
                self.assertEqual(query_ret.__getattribute__(column.key), json_update[column.key],
                             "key: %s, expected: %s, actual: %s" % (column.key, query_ret.__getattribute__(column.key),\
                                                                    json_update[column.key]))

    # Delete
    def test_list_deletion(self):
        find_id = self.get_task_id()
        resp = self.app.delete('/todo/api/v1/tasks/{}'.format(find_id))
        self.assertEqual(resp.status_code, 200)

        # query db and check the task with special id has been deleted
        query_ret = models.Task.query.filter_by(id=find_id).first()
        self.assertFalse(query_ret)

    # get existing task id for testing, using when delete, update testing
    @staticmethod
    def get_task_id():
        id_ret = models.Task.query.with_entities(models.Task.id).first()
        return id_ret.id


if __name__ == '__main__':
    unittest.main()
