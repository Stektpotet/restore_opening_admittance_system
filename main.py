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

    # TODO: Are you also in waiting list if you're admitted in the second time slot?

    # file_path = "C:/Users/halvo/Downloads/RESTORE-Second opening (Responses) - Form responses 1.csv"
    registrations_path = open_csv_path_if_not_exist("data/third_opening_registrations.csv", "Registrations")
    ban_list_path = open_csv_path_if_not_exist("data/banlist.csv", "Ban list")
    first_slot_disallowed_list_path = open_csv_path_if_not_exist("data/downprioritized.csv", "First slot disallowed list")
    confirmed_duplicates_path = open_csv_path_if_not_exist("data/confirmed_duplicates.csv", "Manually confirmed duplicates")

    registrations = [r.registration for r in read_registrations(registrations_path)]
    registrations.sort(key=lambda reg: reg.timestamp)

    ban_list = read_people_table(ban_list_path, name_column=2, email_column=1)
    disallowed_set = set(read_people_table(first_slot_disallowed_list_path, name_column=2, email_column=1))

    confirmed_duplicates = read_people_table(confirmed_duplicates_path, name_column=0, email_column=1)


    admittance = OpeningAdmittance({
        "10:00-11:00": LimitedTimeslot(50),
        "11:00-12:00": LimitedTimeslot(60),
    })

    admittance.confirmed_duplicates = set(confirmed_duplicates)

    admittance.timeslots["10:00-11:00"].disallowed = disallowed_set

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
