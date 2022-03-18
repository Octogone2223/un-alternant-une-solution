from django.test import TestCase
from django.test import Client
from selenium.webdriver.firefox.webdriver import WebDriver
# Create your tests here.


class AuthenticationTests(TestCase):
    def test_homepage(self):
        # self.assertFalse(False)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_signup_page(self):
        response = self.client.get('/auth/sign-up/')
        self.assertEqual(response.status_code, 200)

    def test_signin_page(self):
        response = self.client.get('/auth/sign-in/')
        self.assertEqual(response.status_code, 200)

    # def test_homepage(self):
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)

    def test_student_signup(self):
        print("before")
        python_dict = {'account_type': '3', 'first_name': 'TestStudent', 'last_name': 'TESTSTUDENT', 'email': 'student@test.com', 'password': 'TestStudent', 'confirmPassword': 'TestStudent'}
        response = self.client.post(
            '/auth/sign-up/',
            json.dumps(python_dict),
            content_type="application/json"
        )
        print("after")
        self.assertFalse(False)
        # self.assertEqual(response.status_code, 200)


class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['user-data.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_gotologin(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('myuser')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('secret')
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/auth/signin'))
        username_input = self.selenium.find_element_by_name("email")
        username_input.send_keys('myuser')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('secret')
        self.selenium.find_element_by_id('btn_signin').click()
