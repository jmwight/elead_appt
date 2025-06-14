from elead import Elead
from eleadtime import TimeDelta, Time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from datetime import date
from appointment import Appointment
from datetime import datetime
import time
import re

class AppointmentInterface(Elead):

    def __init__(self, username, password, lead0_url, lead1_url, dummy_appt_name, date=date.today(), headless=False,
                 cookie_file='cookies/cookies.txt', cookie_exp_dir='cookies/cookie_exp'):

        super().__init__(username, password, cookie_file, cookie_exp_dir, headless)
        self._lead0 = lead0_url
        self._lead1 = lead1_url
        self.date = date
        self._appointment_url = 'https://www.eleadcrm.com/evo2/fresh/elead-v45/elead_track/Reports/Desklog/' \
                                     'AppointmentsPage.aspx?FMV=1'
        self._dummy_appt_name = dummy_appt_name

    def get_appt_list(self, interval: TimeDelta, st: Time, et: Time) -> list[Appointment]:
        if st >= et:
            raise ValueError("End time must be after start time")

        apts = []
        # go through each interval and add appointment times in for each one
        while st < et:
            self._set_appts(st, interval, self.date) # set appointments on interval
            new_apts = self._get_appts_in_interval(st+TimeDelta(0, 0), interval) # get appointments in between
            for apt in new_apts:
                apts.append(apt) # add appointments into list of all appointments
            st += interval

        self._revert_appointments()

        return apts

    # _get_appts_in_interval: gets appointments in between set appointment and returns list of Appointment dataclasses
    def _get_appts_in_interval(self, start_time: Time, delta: TimeDelta) -> list[Appointment]: # TODO: check list[Appointment] is correct
        # get to appointment page
        self.get_page(self._appointment_url, By.ID, 'AppointmentData')

        apts = []

        # pull all appointments we can in interval

        # get appointment one past first anchor
        apt_num = 1
        base = f'//tbody[@id="AppointmentData"]/tr[{apt_num}]'
        # find first dummy appointment
        while self.element_exists(By.XPATH, base) and self.driver.find_element(By.XPATH, base + '/td[3]').text != self._dummy_appt_name:
            apt_num += 1
            base = f'//tbody[@id="AppointmentData"]/tr[{apt_num}]'
        apt_num += 1
        base = f'//tbody[@id="AppointmentData"]/tr[{apt_num}]'

        # grab every appointment and collect data until we reach other anchor appointment
        while self.element_exists(By.XPATH, base) and self.driver.find_element(By.XPATH, base + '/td[3]').text != self._dummy_appt_name:
            customer = self.driver.find_element(By.XPATH, base + '/td[3]').text
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

            apts.append(Appointment(start_time, delta, new, vehicle, confirmed, sold, salesperson, private_cust))
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

        self.get_page(lead, By.NAME, 'nHrs')

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

    # _revert_appointments: sets both appointments to date one year from today at 12pm and 1pm so they don't appear on
    # the appointment log after we are done
    def _revert_appointments(self):
        d_now = datetime.now()
        d = datetime(d_now.year + 1, d_now.month, d_now.day, d_now.hour, d_now.minute, d_now.second, d_now.microsecond)
        self._set_appts(Time(12, 0, False), TimeDelta(1, 0), d)

    # export_to_tsv: exports to a tab seperated value file for easy printing
    # TODO: finish this later
    def export_to_tsv(self, appointment_list: list[Appointment], out_file: str, format=0, adder=TimeDelta(0, 0)):
        with open(out_file, 'w') as f:
            # column headers
            if format == 0:
                f.write('Start Time\tDelta\tNew?\tVehicle\tConfirmed?\tSold?\tSalesperson\tPriv Cust?\n')
            elif format == 1:
                f.write('Time\tNew?\tVehicle\tConfirmed?\tSold?\tSalesperson\tPriv Cust?\n')
            # print a line for each appointment
            last_start_time = appointment_list[0].start_time - TimeDelta(0, 15) # just to make the first one not equal
            for apt in appointment_list:
                # only print the time and delta if it's not the same as the last one
                if apt.start_time != last_start_time:
                    # print format of start time and end time (interval)
                    if format == 0:
                        f.write(str(apt.start_time) + '\t')
                        f.write(str(apt.delta) + '\t')
                    # print the time we think it is for the appointments. I.e. we set interval 30 minutes and do on the
                    # 15 and 45s then it prints the even hour. Kind of a hack around assumption no one books appointments
                    # at 15 or 45 only 00 and 30. Just makes it prettier to look at
                    elif format == 1:
                        f.write(str(apt.start_time + adder) + '\t')
                # fill with tabs to align properly and so we don't have to see the same appointment times printed
                # repetitively
                else:
                    if format == 0:
                        f.write('\t\t')
                    elif format == 1:
                        f.write('\t')
                f.write(str(apt.new) + '\t')
                f.write(str(apt.vehicle) + '\t')
                f.write(str(apt.confirmed) + '\t')
                f.write(str(apt.sold) + '\t')
                f.write(str(apt.salesperson) + '\t')
                f.write(str(apt.private_cust) + '\n')

                last_start_time = apt.start_time
