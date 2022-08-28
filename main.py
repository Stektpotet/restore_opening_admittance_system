import copy
import datetime
import tkinter as tk
from tkinter import filedialog
from typing import List

from admittance import read_registrations, OpeningAdmittance, LimitedTimeslot
from form_data import Person, FullRegistration

if __name__ == '__main__':

    root = tk.Tk()
    root.withdraw()

    # file_path = filedialog.askopenfilename(filetypes=[("Comma Separated Values", "*.csv"), ("All types", "*.*")])
    # if file_path == '':
    #     exit()

    file_path = "C:/Users/halvo/Downloads/RESTORE-Second opening (Responses) - Form responses 1.csv"

    registrations = read_registrations(file_path)
    registrations.sort(key=lambda reg: reg.timestamp)

    admittance = OpeningAdmittance({
        "10:00-11:00": LimitedTimeslot(50),
        "11:00-12:00": LimitedTimeslot(60),
        "12:00-13:00": LimitedTimeslot(70),
        "13:00-14:00": LimitedTimeslot(80),
    })

    admittance.auto_admit(registrations)
    # registrations[0].person()
    #
    # admittance.cancel(Person("halvor smedås", "halvor@restore-trd.no"))

    a = Person("halvor smedås", "halvor@restore-trd.no")
    b = FullRegistration("halvor smedås", "halvor@restore-trd.no", datetime.datetime.now(), [], True, "", False, "", "")

    admittance.cancel(a)
    admittance.cancel(b)

    l = copy.deepcopy(admittance.timeslots['10:00-11:00'].spots)

    admittance.cancel(l)
    print(admittance.timeslots['10:00-11:00'])
