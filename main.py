from appointment import Appointment
from eleadtime import *
from appointment_interface import *
from appointment import *
from datetime import datetime


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

    ai = AppointmentInterface(username, password, lead0_url, lead1_url, datetime.today(), False, cookie_file,
                              cookie_exp_dir)
    interval = TimeDelta(0, 30)
    st = Time(9, 15, True)
    et = Time(6, 00, False)
    apts = ai.get_appt_list(interval, st, et)
    for apt in apts:
        print(f'Start_time: {apt.start_time}\tdelta: {apt.delta}\tNew?: {apt.new}\tVehicle: {apt.vehicle}\tConfirmed?: {apt.confirmed}\tSold?: {apt.sold}\tSalesman: {apt.salesperson}\tPrivate?: {apt.private_cust}')

