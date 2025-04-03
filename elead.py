import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import eleadtime
import time
from datetime import datetime
import pickle # for storing and unpacking cookies mainly
from pathlib import Path
import os

# Elead: class to give a logged in ready to use interface with elead
class Elead:

    def __init__(self, username, password, cookie_file='cookies/cookies.txt',
                 cookie_exp_dir='cookies/cookie_exp', headless=False):

        # some constants used elsewhere. Not sure if this is the correct way to do things? In c
        # I would use a define statement.
        self._LOGIN_URL = 'https://www.eleadcrm.com/evo2/fresh/login.asp?logout=1&CID=0&USERID=0&SESSIONID='
        self._MAIN_PAGE_URL = 'https://www.eleadcrm.com/evo2/fresh/elead-v45/elead_track/index.aspx'

        self._username = username
        self._password = password
        self._cookie_file = cookie_file
        self._cookie_exp_dir = cookie_exp_dir

        options = webdriver.ChromeOptions()
        if headless:
            # no graphical browser... faster
            options.add_argument('--headless')

        # add some speed and reliability optimizations TODO: check what these actually do
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(options=options)

        # load new cookies if we can't or loaded cookies are expired, get new cookies
        if self._load_stored_cookies() == False:
            self._get_new_cookies()
        elif self._test_logged_in() == False:
            self._get_new_cookies()

        # close popup window that pops up
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[1])
        self.driver.close()
        self.driver.switch_to.window(windows[0])

        # now everything should be ready to go!

    # _get_new_cookies: get new cookies if the old ones have expired
    def _get_new_cookies(self):

        # login main page
        self.get_page('https://www.eleadcrm.com/evo2/fresh/login.asp', By.ID, 'user')
        self.driver.find_element(By.XPATH, '//*[@id="btnSingleSignOnSignUp"]').click()  # click button to get to login page

        # 2 factor login page with email
        # get_page(driver, 'https://www.eleadcrm.com/evo2/fresh/login.asp', By.ID, 'okta-signin-username')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'okta-signin-username')))
        userNameEl = self.driver.find_element(By.ID, 'okta-signin-username')
        userNameEl.send_keys(self._username)
        passEl = self.driver.find_element(By.ID, 'okta-signin-password')
        passEl.send_keys(self._password)
        self.driver.find_element(By.XPATH, '//label[@for="input42"]').click()  # click remember me check box
        passEl.send_keys(Keys.ENTER)

        # wait for text message box
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'input40')))
        self.driver.find_element(By.XPATH, '//*[@id="form33"]/div[1]/div[2]/a').click()  # click button to get text message
        self.driver.find_element(By.XPATH, '//label[@for="input49"]').click()  # click no challenge for 30 days check box
        time.sleep(15)

        # filter out the cookies we need
        # we only need the 'ASP.NET_SessionId' and 'SessCk2' cookies
        # they are identified by the name key in the dictionary of cookies
        # they are session cookies but my understanding is if you hit remember me they are good for 30 days. Not 100%
        # on that
        all_cookies = self.driver.get_cookies()
        t_str = datetime.now().strftime('%d/%m/%y, %H:%M:%S') # get current time

        file_num = len(os.listdir(self._cookie_exp_dir))
        with open(f'{self._cookie_exp_dir}/exp{file_num}.txt', 'w') as f:
            f.write(t_str)

        needed_cookies = []
        for cookie in all_cookies:
            if cookie.get('name') == 'ASP.NET_SessionId' or cookie.get('name') == 'SessCk2':
                needed_cookies.append(cookie)

        self._store_cookies(needed_cookies)

        return needed_cookies

    # _store_cookies: store cookies in file for later
    def _store_cookies(self, cookies: list):
        with open(self._cookie_file, 'wb') as f:
            pickle.dump(cookies, f)

    # _load_stored_cookies: load stored cookies from earlier into browser. Returns true if cookies loaded. False if not
    def _load_stored_cookies(self) -> bool:
        if os.path.isfile(self._cookie_file):
            with open(self._cookie_file, 'rb') as f:
                try:
                    cookies = pickle.load(f)
                except:
                    return False
            self.get_page(self._LOGIN_URL, By.ID, 'user')
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            return True
        else:
            #TODO: learn about logging and add to this
            print('Error: no cookie file. You must run _get_new_cookies')
            return False

    # _test_cookies: test to see if cookies have expired. Returns true if logged in, false if not
    def _test_logged_in(self) -> bool:
        # main page. If this doesn't load then we know it didn't work
        self.driver.get(self._MAIN_PAGE_URL)
        self.driver.implicitly_wait(2)
        if(self.driver.current_url == self._LOGIN_URL):
            return False
        else:
            return True

    # get_page: loads given url and waits until locater of given type is present and ready
    def get_page(self, url: str, locator_function, locator: str):
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 10).until(EC.present_of_element_locate((locator_function, locator)))
            # if type == 'ID':
            #     WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, locator)))
            # elif type == 'NAME':
            #     WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, locator)))
            # elif type == 'CLASS_NAME':
            #     WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, locator)))
            # elif type == 'XPATH':
            #     WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, locator)))
            # elif type == 'TAG_NAME':
            #     WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, locator)))
            # else:
            #     raise Exception('tag type not found!')\
            #print('page loaded successfully')

        except TimeoutException:
            print("Webpage is taking too long to load")

        except:
            print('unknown error occurred')

    def get_element(self, XPATH, default):
        try:
            element = self.driver.find_element(By.XPATH, XPATH).text
            return element
        except NoSuchElementException:
            return default

    # element_exists: if given element exists return true, else return False. Throw exception if improper type given
    #TODO: UPDATE get_page FUNCTION WITH FUNCTION INPUT
    def element_exists(self, tag_func, locator: str):
        try:
            self.driver.find_element(tag_func, locator)
            return True

        except NoSuchElementException:
            return False
