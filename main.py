import csv
import itertools
from os import times
from typing import List, Tuple

from datatypes import Person, Registration, RegistrationExtras, Timeslot, AdmittanceStatus
from datetime import datetime
import tkinter as tk
from tkinter import filedialog


def _normalise(field: str) -> str:
    return field.lower().strip()


def read_entry(
        timestamp: str,
        email: str,
        name: str,
        timeslots: str,
        student_type: str,
        erasmus: str,
        nationality: str,
        sit_residency: str,
        read_rules: str
) -> Tuple[Registration, RegistrationExtras]:
    registration = Registration(
        _normalise(name),
        _normalise(email),
        datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S'),
        [timeslot.replace(' ', '') for timeslot in timeslots.split(',')],
        _normalise(read_rules) == "yes"
    )
    extras = RegistrationExtras(
        _normalise(student_type),
        _normalise(erasmus) == "yes",
        _normalise(nationality),
        _normalise(sit_residency)
    )

    return registration, extras


def read_registrations(file_path: str) -> Tuple[List[Registration], List[RegistrationExtras]]:
    with open(file_path, encoding="utf-8") as registration_file:
        next(reader := csv.reader(registration_file))  # assign reader and skip headers
        return tuple(zip(*[read_entry(*row) for row in reader]))

timeslots = {
    "10:00-11:00": Timeslot(50),
    "11:00-12:00": Timeslot(60),
    "12:00-13:00": Timeslot(70),
    "13:00-14:00": Timeslot(80),
}

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(filetypes=[("Comma Separated Values", "*.csv"), ("All types", "*.*")])
    if file_path == '':
        exit()

    registrations, _ = read_registrations(file_path)
    registrations = list(registrations)
    registrations.sort(key=lambda reg: reg.timestamp)

    for registration in registrations:
        person = Person(registration.name, registration.email)
        for wanted_slot in registration.timeslots:
            status, spot = timeslots[wanted_slot].admit(person)
            if AdmittanceStatus.Admitted in status:
                if AdmittanceStatus.Marked in status:
                    print("Marked!", registration, f"admitted to spot #{spot}")
                break

    print(timeslots)





