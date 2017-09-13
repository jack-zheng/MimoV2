import unittest
from mimov2 import app


class MimoTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    # create a hello test as a start
    def test_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.data.decode('utf-8'), 'Hello World')


if __name__ == '__main__':
    unittest.main()