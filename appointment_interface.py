from elead import Elead
from eleadtime import TimeDelta, Time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from datetime import date
from appointment import Appointment
import time

class AppointmentInterface(Elead):

    def __init__(self, username, password, lead0_url, lead1_url, date=date.today(), headless=False,
                 cookie_file='cookies/cookies.txt', cookie_exp_dir='cookies/cookie_exp'):

        super().__init__(username, password, cookie_file, cookie_exp_dir, headless)
        self._lead0 = lead0_url
        self._lead1 = lead1_url
        self.date = date
        self._appointment_url = 'https://www.eleadcrm.com/evo2/fresh/elead-v45/elead_track/Reports/Desklog/' \
                                     'AppointmentsPage.aspx?FMV=1'
        self._dummy_appt_name = '..................................., ..............................'

    def get_appt_list(self, interval: TimeDelta, st: Time, et: Time) -> list[Appointment]:
        if st >= et:
            raise ValueError("End time must be after start time")

        appts = []
        while st+interval < et:
            self._set_appts(st, interval, self.date)
            ##TODO: function that reads appointments in between
            st += interval

        #set appointments
        self._set_appts(st, interval, self.date)
        #check for appointments in between an add to list and add each one into appointment then appointmen list
        # return the result

    # _get_appts_in_interval: gets appointments in between set appointment and returns list of Appointment dataclasses
    def _get_appts_in_interval(self, t: Time) -> list[Appointment]: # TODO: check list[Appointment] is correct
        # get to appointment page
        self.get_page(self._appointment_url, 'ID', 'AppointmentData')

        apts = []

        # pull all appointments we can in interval
        apt_num = 1
        base = f'//tbody[@id="AppointmentData"]/tr[{apt_num}]'
        # find first dummy appointment
        while self.element_exists(By.XPATH, base) and self.driver.find_element(By.XPATH, base + '/td[3]').text != self._dummy_appt_name:
            apt_num += 1
            base = f'//tbody[@id="AppointmentData"]/tr[{apt_num}]'
        apt_num += 1
        base = f'//tbody[@id="AppointmentData"]/tr[{apt_num}]'

        while self.element_exists(By.XPATH, base):
            customer = self.driver.find_element(By.XPATH, base + '/td[3]').text
            if customer == self._dummy_appt_name:
                break
            if self.driver.find_element(By.XPATH, base + '/td[2]').text == 'N':
                new = True
            else:
                new = False
            vehicle = self.driver.find_element(By.XPATH, base + '/td[2]/span').get_attribute('data-tooltip')
            confirmed = not self.element_exists(By.XPATH, base + '/td[3]/img')
            sold = self.element_exists(By.XPATH, base + '/td[3]/span[@class="imgStockAvailable"]')
            salesperson = self.driver.find_element(By.XPATH, base + '/td[5]').text
            if customer == 'Private Customer':
                private_cust = True
            else:
                private_cust = False

            apts.append(Appointment(t, new, vehicle, confirmed, sold, salesperson, private_cust))
            apt_num += 1
            base = f'//tbody[@id="AppointmentData"]/tr[{apt_num}]'

        return apts

    # _set_appts: set placeholder appointments so that we know time so we can see what is in between
    def _set_appts(self, st: Time, td: TimeDelta, d: date):
        self._set_appt(self._lead0, st, d)
        self._set_appt(self._lead1, st+td, d)

    # _set_appt: set individual appointment
    def _set_appt(self, lead: str, t: Time, d: date):
        am_pm_dict = {True: 'AM', False: 'PM'}

        self.get_page(lead, 'NAME', 'nHrs')

        # set up all parameters
        hour_dropdown = Select(self.driver.find_element(By.NAME, 'nHrs'))
        min_dropdown = Select(self.driver.find_element(By.NAME, 'nMin'))
        am_pm_dropdown = Select(self.driver.find_element(By.NAME, 'szAMPM'))
        # XPATH: div(class="Input__StyledInputFieldWrapper-sc-h2492t-3 iCyBmY")/input
        date_text = self.driver.find_element(By.NAME, 'dtRadialEffective')  # Not sure if this is right
        submit_btn = self.driver.find_element(By.ID, 'Submit1')

        # set dropdowns for hour, minute, and am/pm
        hour_dropdown.select_by_value(str(t.hour))
        min_dropdown.select_by_value(str(t.minute))
        am_pm_dropdown.select_by_value(am_pm_dict[t.am])

        # set date, if it wasn't passed into function, its it's today's date
        m_txt = ''
        d_txt = ''
        y_txt = ''
        if d.month < 10:
            m_txt = '0'
        m_txt += str(d.month)
        if d.day < 10:
            d_txt = '0'
        d_txt += str(d.day)
        y_txt += str(d.year)
        date_text.click()
        date_text.send_keys(Keys.CONTROL, 'a')
        date_text.send_keys(m_txt + d_txt + y_txt)

        # click submit button to set appointment
        submit_btn.click()

    # export_to_tsv: exports to a tab seperated value file for easy printing
    # TODO: finish this later
    def export_to_tsv(self, appointment_list, file):
        pass
