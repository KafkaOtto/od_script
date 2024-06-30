# -*- coding: UTF-8 -*-
"""
__Author__ = "Otto Guo"
__Version__ = "1.0.0"
__Description__ = ""
__Created__ = 2024/05/30
"""

import os.path
import pickle
import time
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import datetime
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse, parse_qs
import http.client, urllib
import random

class OurDomain:
    def __init__(self, config):
        self.config = config
        self.status = 0  # 状态,表示如今进行到何种程度
        self.login_method = 1  # {0:模拟登录,1:Cookie登录}自行选择登录方式
        chrome_options = Options()
        # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=chrome_options)  # 默认Chrome浏览器
        # self.driver.delete_all_cookies()

    def set_cookie(self):
        """
        :return: write cookie
        https://southeast-thisisourdomain.securerc.co.uk/onlineleasing/ourdomain-amsterdam-south-east/guestlogin.aspx
        """

        self.driver.get(self.config.login_url)

        # wait for login to complete
        # time.sleep(5)
        login_par = "Login"

        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "Username")))
            print("Username field is present")

            # Find elements by id for Username and Password, and fill in the values
            self.driver.find_element(By.ID, "Username").send_keys(self.config.user)
            self.driver.find_element(By.ID, "Password").send_keys(self.config.password)
            print("Filled in username and password")

            # Find and trigger the SubmitLogin button
            self.driver.find_element(By.ID, "SubmitLogin").click()
            print("Clicked the SubmitLogin button")

            time.sleep(5)

            current_url = self.driver.current_url
            print(f"Current URL after login attempt: {current_url}")

            if login_par in current_url:
                print("Login Fail.")
            else:
                print("Login Successful.")
                # Write cookies to a file
                with open("od_cookies.pkl", "wb") as cookie_file:
                    pickle.dump(self.driver.get_cookies(), cookie_file)

        except:
            current_url = self.driver.current_url
            print(f"Login failed. Current URL: {current_url}")

    def get_cookie(self):
        """
        :return: 读取cookie
        """
        # try:
        #     cookies = pickle.load(open("od_cookies.pkl", "rb"))
        #     for cookie in cookies:
        #         cookie_dict = {
        #             # valid domain
        #             'domain': 'southeast-thisisourdomain.securerc.co.uk',
        #             'name': cookie.get('name'),
        #             'value': cookie.get('value'),
        #         }
        #         self.driver.add_cookie(cookie_dict)
        #     print('***finish cookie loading***\n')
        # except Exception as e:
        #     print(e)

    def login(self):
        """
        :return: Login
        """
        # if self.login_method == 0:
        #     self.driver.get(self.config.login_url)
        #     print('***start login***\n')
        # elif self.login_method == 1:
        #     if not os.path.exists('od_cookies.pkl'):
        #         # 没有cookie就获取
        #         self.set_cookie()
        #     else:
        #         self.driver.get(self.config.target_url)
        #         self.get_cookie()
        self.driver.get(self.config.login_url)
        self.set_cookie()
        self.get_cookie()

    def get_stepname(self):
        cur = self.driver.current_url
        parsed_url = urlparse(cur)
        query_params = parse_qs(parsed_url.query)
        # Normalize keys to lowercase
        query_params_normalized = {k.lower(): v for k, v in query_params.items()}

        # Get the value of the 'stepname' parameter (in any case)
        stepname = query_params_normalized.get('stepname', [None])[0]

        return stepname

    def index(self):
        if self.floor_plan(is_first=False):
            prev_step = 'floorplan'
            while (True):
                while (True):
                    stepname = self.get_stepname()
                    if stepname != prev_step:
                        prev_step = stepname
                        break
                if not self.step(stepname):
                    return False
        else:
            return False

    def send_note(self):
        return
        # try:
        #     conn = http.client.HTTPSConnection("api.pushover.net:443")
        #     conn.request("POST", "/1/messages.json",
        #                  urllib.parse.urlencode({
        #                      "token": "axqckkgyrqa93b5d1d8ct5rdg567ix",
        #                      "user": "uvq93ehr14f9o5ro7y6ht6az6pskh1",
        #                      "message": "Ourdomain has new house alert",
        #                  }), {"Content-type": "application/x-www-form-urlencoded"})
        #     res = conn.getresponse()
        #     print(res.status, res.msg)
        #
        # except Exception as e:
        #     print("An error occurred:", e)


    def step(self, stepname):
        print("current step: ", stepname)
        # https://southeast-thisisourdomain.securerc.co.uk/onlineleasing/ourdomain-amsterdam-south-east/oleapplication.aspx?propleadsource_182801=portal&stepname=Apartments&myOlePropertyId=182801&floorPlans=1101760&MoveInDate=undefined
        if stepname == 'Apartments':
            self.send_note()
            return self.apartment()
        # https://southeast-thisisourdomain.securerc.co.uk/onlineleasing/ourdomain-amsterdam-south-east/oleapplication.aspx?Stepname=RentalOptions
        if stepname == 'RentalOptions':
            return self.retal()
        # https://southeast-thisisourdomain.securerc.co.uk/onlineleasing/ourdomain-amsterdam-south-east/oleapplication.aspx?stepname=IntApplicantInfo&myOlePropertyId=182801&ShowPreAppForm=1&UnitID=224148&FloorPlanID=1101760
        if stepname == "IntApplicantInfo":
            return self.applicationInfo()
        # https://southeast-thisisourdomain.securerc.co.uk/onlineleasing/ourdomain-amsterdam-south-east/oleapplication.aspx?stepname=IntAdditionalApplicants&myOlePropertyId=182799&myMainProspectId=1054321&ShowAfterAppinfoDocs=1
        if stepname == "IntAdditionalApplicants":
            return self.additionalApplication()
        # https://southeast-thisisourdomain.securerc.co.uk/onlineleasing/ourdomain-amsterdam-south-east/oleapplication.aspx?stepname=ApplicationCharges&myOlePropertyId=182799
        if stepname == "ApplicationCharges":
            return self.applicationCharger()
        else:
            return True


    def floor_plan(self, is_first=True):
        try:
            print("start choose plan")
            self.driver.get(self.config.floor_plan_url)

            if (is_first):
                self.driver.refresh()
                return True

            # print(self.driver.page_source)
            # Wait for the apply button to be present

            plan_span = "//span[@title='%s']" % (self.config.plan)
            superior_studio = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, plan_span))
            )

            if superior_studio:
                # Find the parent <tr> element
                row_element = superior_studio.find_element(By.XPATH, "./ancestor::tr")

                # Find the button within the row
                button = WebDriverWait(row_element, 10).until(
                    EC.element_to_be_clickable((By.XPATH, ".//button"))
                )

                if button:
                    if 'contactButton' not in button.get_attribute('class'):
                        # Click the button if it's not a contact button
                        button.click()
                        print("Continue Button clicked!")

                        return True
                    else:
                        print("It's a contact button. Plan Not available")
                else:
                    print("Button not found.")
            else:
                print("Superior Studio not found.")
        except Exception as e:
            print(f'***Continue Button not found or other error: {e}***')
            return False
        return False

    def apartment(self):
        try:
            # Wait for the table rows to be present
            print("start choose an apartment")
            rows = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//tr[contains(@class, 'AvailUnitRow')]"))
            )

            if not rows:
                print("No available units found.")
                return False

            min_rent = float('inf')
            min_rent_button = None

            for row in rows:
                rent_text = row.find_element(By.XPATH, ".//td[contains(@data-label, 'Rent')]").text
                rent_value = float(rent_text.replace('€', '').replace(',', '').strip())

                if rent_value < min_rent:
                    min_rent = rent_value
                    min_rent_button = row.find_element(By.XPATH, ".//button[contains(@name, 'Select')]")

            if min_rent_button:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(min_rent_button))
                min_rent_button.click()
                print(f"Apartment with the lowest rent of €{min_rent} selected!")
                return True
            else:
                print("No 'Select' buttons found.")
                return False

        except Exception as e:
            print("An error occurred:", e)
            return False

    # def apartment(self):
    #     try:
    #         # Wait for the buttons to be clickable
    #
    #         print("start choose an apartment")
    #         select_buttons = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_all_elements_located((By.XPATH, "//button[contains(@name, 'Select')]"))
    #         )
    #
    #         if select_buttons:
    #             # Click the last button
    #
    #             last_button = random.choice(select_buttons)
    #             WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(last_button))
    #             last_button.click()
    #             print("Last button with 'Select' in the name clicked!")
    #             return True
    #         else:
    #             print("No buttons with 'Select' in the name found.")
    #
    #     except Exception as e:
    #         print("An error occurred:", e)
    #     return False

    def retal(self):

        print(f"current url ${self.driver.current_url}")
        retry_attempts = 3  # Number of retry attempts for handling stale element reference
        try:
            for attempt in range(retry_attempts):
                try:
                    # Wait for the datepicker to be clickable
                    datepicker = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'sMoveInDate'))
                    )

                    # Execute the script to get the maxDate
                    max_date_script = "$('#sMoveInDate').datepicker('option', 'maxDate');"
                    max_date = self.driver.execute_script("return " + max_date_script)
                    formatted_max_date = datetime.datetime.strptime(max_date, '%d-%m-%Y').strftime('%d-%m-%Y')

                    # Set the date to the maxDate using the datepicker
                    # datepicker.clear()  # Clear the datepicker field if needed
                    datepicker.send_keys(formatted_max_date)
                    datepicker.send_keys(Keys.RETURN)

                    # Wait for the continue button to be clickable and click it
                    continue_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'btnContinue'))
                    )
                    continue_button.click()

                    return True

                except Exception as e:
                    print(f"Retrying... ({attempt + 1}/{retry_attempts})")

        except Exception as e:
            print("An error occurred:", e)

        return False

    def applicationInfo(self):

        try:
            # print(f"current url ${self.driver.current_url}")
            btnNext = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.ID, "btnNext"))
            )

            btnNext.click()

            return 1
        except Exception as e:
            print("An error occurred:", e)
        return False


    def additionalApplication(self):

        try:
            # print(f"current url ${self.driver.current_url}")
            btnNext = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.ID, "continueBtn"))
            )

            btnNext.click()

            return True
        except Exception as e:
            print("An error occurred:", e)
        return False

    def applicationCharger(self):
        # send notification
        try:
            # print(f"current url ${self.driver.current_url}")
            idealBtn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.ID, "btnAddIdeal"))
            )

            idealBtn.click()

            sleep(1000)
            return True
        except Exception as e:
            print("An error occurred:", e)
        return False


    def finish(self):
        self.driver.quit()