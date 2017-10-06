import json
import unittest

from project import app


class ViewTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.item01 = '{"title":"first target"}'

        self.item02 = '{"title": "second target", "description": "my 2 target"}'

        self.update = '{"id": id_replace, "title": "title update"}'

        self.item_deletion = {'id': 1}

    # create a hello test as a start
    def test_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.data.decode('utf-8'), 'Hello World')

    # Post
    def test_post_list(self):
        resp = self.app.post('/todo/api/v1/tasks', data=self.item01, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)
        self.assertIn('first target', str(resp.data))

    # Get all
    def test_get_list(self):
        # post a new target first as data prepare.
        resp= self.app.post('/todo/api/v1/tasks', data=self.item02, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)
        resp = self.app.get('/todo/api/v1/tasks')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(2, len(json.loads(resp.data)['tasks']))

    # Get one
    def test_get_list_by_id(self):
        resp = self.app.get('/todo/api/v1/tasks/{}'.format('1'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('t1', str(resp.data))

    # Update
    def test_update_list(self):
        update_id = self.get_task_id()
        self.update = self.update.replace('id_replace', str(update_id))
        resp = self.app.put('/todo/api/v1/tasks', data=self.update, headers={"Content-type": "application/json"})
        self.assertEqual(resp.status_code, 201)
        resp = self.app.get('/todo/api/v1/tasks')
        self.assertIn('update', str(resp.data))

    # Delete
    def test_list_deletion(self):
        find_id = self.get_task_id()

        resp = self.app.delete('/todo/api/v1/tasks/{}'.format(find_id))
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(str(find_id), str(resp.data))

    # get existing task id for test, use when delete, update testing
    def get_task_id(self):
        resp = self.app.get('/todo/api/v1/tasks')
        json_tasks = json.loads(resp.data)['tasks']
        find_id = json_tasks[0]['id']
        return find_id


if __name__ == '__main__':
    unittest.main()