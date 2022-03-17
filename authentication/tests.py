from django.test import TestCase
from django.test import Client
# Create your tests here.


class AuthenticationTests(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_signup_page(self):
        response = self.client.get('/sign-up/')
        self.assertEqual(response.status_code, 200)

    def test_signin_page(self):
        response = self.client.get('/sign-in/')
        self.assertEqual(response.status_code, 200)

    # def test_homepage(self):
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)

    # Student sign up
    def test_student_signup(self):
        response = self.client.post("/sign-up/", {'account_type': 3, 'first_name': 'TestStudent', 'last_name': 'TESTSTUDENT', 'email': 'student@test.com', 'password': 'TestStudent', 'confirmPassword': 'TestStudent'})
        self.assertEqual(response.status_code, 200)
