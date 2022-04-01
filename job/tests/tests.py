from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from job.views import job_detail
from job.models import Job, JobDating, JobStatus, JobCode
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import json
from selenium.webdriver.chrome.options import Options

# Create your tests here.


class JobTests(TestCase):

    fixtures = ["all.json"]

    def setUp(self):
        signup_dict = json.dumps(
            {
                "accountType": 3,
                "first_name": "TestStudent",
                "last_name": "TESTSTUDENT",
                "email": "student@test.com",
                "password": "TestStudent",
                "confirmPassword": "TestStudent",
            }
        )
        login_dict = json.dumps(
            {"email": "student@test.com", "password": "TestStudent"}
        )
        self.client.post("/auth/sign-up/", signup_dict, "application/json")
        self.client.post("/auth/sign-in/", login_dict, "application/json")

    def test_job_page(self):
        job = Job.objects.all()
        print(job)
        response = self.client.get("/jobs/")
        self.assertEqual(response.status_code, 200)

    def test_jobs_datings_notlogged_page(self):
        response = self.client.get("/jobs/datings/")
        self.assertEqual(response.status_code, 302)

    def test_jobs_datings_logged_page(self):
        
        response = self.client.get("/jobs/datings/")
        self.assertEqual(response.status_code, 200)

    def test_job_detail_page(self):
        response = self.client.get(reverse('job_detail'))
        # self.assertEqual(resolve(reverse('job_detail')).func.__name__,job_detail.as_view().__name__)
        self.assertTemplateUsed(response.status_code,'job/jobs_datings_student.html')



class JobSeleniumTests(StaticLiveServerTestCase):

    fixtures = ["all.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        option = webdriver.ChromeOptions()
        option.add_argument("start-maximized")
        cls.selenium = webdriver.Chrome(ChromeDriverManager().install(), options=option)
        cls.selenium.maximize_window()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_job_page(self):
        self.selenium.get("%s%s" % (self.live_server_url, "/jobs"))
        elem = self.selenium.find_element_by_xpath('//*[contains(text(),"Rechercher")]')
        assert elem is not None
        # Fill the search form's field
        search_profession = self.selenium.find_element_by_name("search_profession")
        search_profession.send_keys("appre")
        search_contracttype = self.selenium.find_element_by_name("search_contracttype")
        search_contracttype.send_keys("CDD")

        # Click on search button
        self.selenium.find_element_by_xpath(
            '//button[contains(text(),"Rechercher")]'
        ).click()

        # Check if we got an answer
        elem = self.selenium.find_element_by_xpath(
            '//h2[contains(text(),"Apprentissage")]'
        )
        # assert(elem is not None)

        # Click to show job detail
        self.selenium.find_element_by_xpath(
            '//h2[contains(text(),"Apprenti(e)")]/parent::div'
        ).click()
        elem = self.selenium.find_element_by_xpath(
            '//p[contains(text(),"LES DOUCEURS DU CHENE")]'
        )
        self.selenium.implicitly_wait(30)

    def test_job_detail_page(self):
        # Go to job detail page
        self.selenium.find_element_by_id("btn_apply").click()

        # Check if we're on Sign-in page
        elem = self.selenium.find_element_by_id("signin")
        if elem is not None:

            # Fill the form's field
            username_input = self.selenium.find_element_by_name("email")
            username_input.send_keys("student@test.com")
            password_input = self.selenium.find_element_by_name("password")
            password_input.send_keys("TestStudent")

            # Click on signin button
            self.selenium.find_element_by_id("btn_signin").click()

        # Check if we're on job detail page
        elem = self.selenium.find_element_by_xpath(
            '//p[contains(text(),"LES DOUCEURS DU CHENE")]'
        )

        assert elem is not None
        