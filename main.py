from appointment import Appointment
from eleadtime import *
from appointment_interface import *
from appointment import *
from datetime import datetime, timedelta
import time

def getinputtime(prompt: str) -> Time:
    t = input(prompt).strip()
    tele = t.split(':')
    # keep asking for input if it's entered incorrectly until it's correct
    while ':' not in t or len(tele) != 2 or not tele[0].isdigit() or not tele[1].isdigit():
        print('Error: Invalid input. Format: "H[H]:MM" where H[H] is an hour like 1 or 11 and MM is a minute like 20\n')
        t = input(prompt).strip()

    dp = input('AM or PM? ')
    dp = dp.strip().upper()
    while dp != 'AM' and dp != 'PM':
        print('Error: Invalid input. Enter either AM or PM (upper or lowercase)')
        dp = input('AM or PM? ')
        dp = dp.strip().upper()

    return Time(int(tele[0]), int(tele[1]), True if dp == 'AM' else False)

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
    ai = AppointmentInterface(username, password, lead0_url, lead1_url, dummy_appt_name, today, headless=False,
                              cookie_file=cookie_file, cookie_exp_dir=cookie_exp_dir)
    
    interval = TimeDelta(0, 30)
    print('Note: minute 15 or 45 for time\n')
    st = getinputtime('Enter start time: ')
    while st.minute != 15 or st.minute != 45:
        print('Minute only 15 or 45\n')
        getinputtime('Enter start time: ')
    
    et = getinputtime('Enter end time: ')
    while et.minute != 15 or st.minute != 45:
        print('Minute only 15 or 45\n')
        getinputtime('Enter end time: ')
    
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

