from appointment import Appointment
from eleadtime import *
from appointment_interface import *
from appointment import *
from datetime import datetime, timedelta
import time


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cookie_file = 'cookies/cookies.txt'
    cookie_exp_dir = 'cookies/cookie_exp'
    with open('logins/username.txt', 'r') as f:
        username = f.readline()
    with open('logins/password.txt', 'r') as f:
        password = f.readline()
    with open('logins/leads.txt', 'r') as f:
        lead0_url = f.readline()
        lead1_url = f.readline()

    with open('logins/dummy_apt_name.txt', 'r') as f:
        dummy_appt_name = f.readline()

    today = datetime.today()
    yesterday = today - timedelta(days=1)

    # measure runtime of browser portion in headless mode vs not headless mode
    t0 = time.perf_counter()
    ai = AppointmentInterface(username, password, lead0_url, lead1_url, dummy_appt_name, today, headless=True,
                              cookie_file=cookie_file, cookie_exp_dir=cookie_exp_dir)
    interval = TimeDelta(0, 30)
    st = Time(8, 45, True)
    et = Time(11, 45, False)
    apts = ai.get_appt_list(interval, st, et)

    # print runtime
    t1 = time.perf_counter()
    print(f'Runtime is {t1-t0}seconds')

    permitted_salespeople = []
    with open('exclusion-inclusion-lists/included-salespeople.txt') as f:
        for line in f.readlines():
            permitted_salespeople.append(line.strip('\n'))

    bdc_appts = []
    for apt in apts:
        if apt.salesperson in permitted_salespeople:
            bdc_appts.append(apt)

    for apt in bdc_appts:
        print(f'Start_time: {apt.start_time}\tdelta: {apt.delta}\tNew?: {apt.new}\tVehicle: {apt.vehicle}\tConfirmed?: {apt.confirmed}\tSold?: {apt.sold}\tSalesman: {apt.salesperson}\tPrivate?: {apt.private_cust}')

    apptspath = 'appts/test0.tsv'
    ai.export_to_tsv(bdc_appts, apptspath, format=1, adder=TimeDelta(0, 15))