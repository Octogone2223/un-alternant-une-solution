from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import json

# Create your tests here.


class AuthenticationTests(TestCase):
    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_signup_page(self):
        response = self.client.get("/auth/sign-up/")
        self.assertEqual(response.status_code, 200)

    def test_signin_page(self):
        response = self.client.get("/auth/sign-in/")
        self.assertEqual(response.status_code, 200)

    def test_student_signup(self):
        python_dict = json.dumps(
            {
                "accountType": 3,
                "first_name": "TestStudent",
                "last_name": "TESTSTUDENT",
                "email": "student@test.com",
                "password": "TestStudent",
                "confirmPassword": "TestStudent",
            }
        )
        response = self.client.post("/auth/sign-up/", python_dict, "application/json")
        self.assertEqual(response.status_code, 200)

    def test_student_login(self):
        python_dict = json.dumps(
            {"email": "student@test.com", "password": "TestStudent"}
        )
        response = self.client.post("/auth/sign-in/", python_dict, "application/json")
        self.assertEqual(response.status_code, 200)


class AuthenticationSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        option = webdriver.ChromeOptions()
        option.add_argument("start-maximized")
        cls.selenium = webdriver.Chrome(ChromeDriverManager().install(), options=option)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_homepage(self):
        self.selenium.get("%s%s" % (self.live_server_url, "/"))
        assert "1alternant1solution" in self.selenium.title
        elem = self.selenium.find_element_by_xpath(
            '//a[contains(text(),"Je suis étudiant")]'
        )
        assert elem is not None

    def test_signup_signin_student(self):
        # Access to Sign up page
        self.selenium.get("%s%s" % (self.live_server_url, "/auth/sign-up"))

        # Select Student button radio
        self.selenium.find_element_by_xpath("//input[@value=3]").click()

        # Fill the form's field
        firstname_input = self.selenium.find_element_by_name("first_name")
        firstname_input.send_keys("TestStudent")
        lastname_input = self.selenium.find_element_by_name("last_name")
        lastname_input.send_keys("TESTSTUDENT")
        mail_input = self.selenium.find_element_by_name("email")
        mail_input.send_keys("student@test.com")
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys("TestStudent")
        confirmpassword_input = self.selenium.find_element_by_name("confirmPassword")
        confirmpassword_input.send_keys("TestStudent")

        # Click on signup button
        self.selenium.find_element_by_id("btn_signup").click()

        # Check if we're on Sign-in page
        elem = self.selenium.find_element_by_id("signin")
        assert elem is not None

        # Fill the form's field
        username_input = self.selenium.find_element_by_name("email")
        username_input.send_keys("student@test.com")
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys("TestStudent")

        # Click on signin button
        self.selenium.find_element_by_id("btn_signin").click()

        # Check if we're on private page
        elem = self.selenium.find_element_by_xpath(
            '//*[contains(text(),"Modifier son profil")]'
        )
        assert elem is not None
