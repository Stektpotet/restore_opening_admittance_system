import copy
import datetime
import os.path
import tkinter as tk
from tkinter import filedialog
from typing import List

from admittance import read_registrations, OpeningAdmittance, LimitedTimeslot, read_people_table
from form_data import Person, FullRegistration

def open_csv_path_if_not_exist(path: str, title: str) -> str:
    if os.path.exists(path):
        return path
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(title=title, filetypes=[("Comma Separated Values", "*.csv"), ("All types", "*.*")])
    root.destroy()
    return path


if __name__ == '__main__':

    # file_path = "C:/Users/halvo/Downloads/RESTORE-Second opening (Responses) - Form responses 1.csv"
    registrations_path = open_csv_path_if_not_exist("data/third_opening_test.csv", "Registrations")
    ban_list_path = open_csv_path_if_not_exist("data/Redlist - Sheet1.csv", "Ban list")
    first_slot_disallowed_list_path = open_csv_path_if_not_exist("data/timeslot1.csv", "First slot disallowed list")

    registrations = [r.registration for r in read_registrations(registrations_path)]
    registrations.sort(key=lambda reg: reg.timestamp)

    ban_list = read_people_table(ban_list_path, name_column=2, email_column=1)
    disallowed_list = read_people_table(first_slot_disallowed_list_path, name_column=2, email_column=1)

    admittance = OpeningAdmittance({
        "10:00-11:00": LimitedTimeslot(50),
        "11:00-12:00": LimitedTimeslot(60),
        "12:00-13:00": LimitedTimeslot(70),
        "13:00-14:00": LimitedTimeslot(80),
    })

    admittance.timeslots["10:00-11:00"].disallowed = disallowed_list

    admittance.banned.update(ban_list)

    admittance.auto_admit(registrations)
    admittance.write_to_spreadsheets("data/")
    # registrations[0].person()
    #
    # admittance.cancel(Person("halvor smedås", "halvor@restore-trd.no"))

    # a = Person("halvor smedås", "halvor@restore-trd.no")
    # b = FullRegistration("halvor smedås", "halvor@restore-trd.no", datetime.datetime.now(), [], True, "", False, "", "")
    #
    # admittance.cancel(a)
    # admittance.cancel(b)

    # l = copy.deepcopy(admittance.timeslots['10:00-11:00'].spots)
    #
    # admittance.cancel(l)
    # print(admittance.timeslots['10:00-11:00'])
