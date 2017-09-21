# project/server/tests/test_main.py


import unittest

from base import BaseTestCase


class TestMainBlueprint(BaseTestCase):

    def test_index(self):
        # Ensure Flask is setup.
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome!', response.data)
        self.assertIn(b'Register/Login', response.data)

    def test_about(self):
        # Ensure about route behaves correctly.
        response = self.client.get('/about', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    def test_404(self):
        # Ensure 404 error is handled.
        response = self.client.get('/404')
        self.assert404(response)
        self.assertTemplateUsed('errors/404.html')

    def test_search_add_view(self):
        response = self.client.get('/')
        self.assertIn(b'-- search --', response.data)
        response = self.client.post('/search', data=dict(
            search_text = 'Dark Souls',
        ), follow_redirects=True)
        self.assertIn(b'/game/find?asin=B00Z9LUFHS',response.data)
        response = self.client.get(
            'http://localhost:5000/game/find?asin=B00Z9LUFHS',
            follow_redirects=True
        )
        self.assertIn(b'Dark Souls',response.data)


if __name__ == '__main__':
    unittest.main()
