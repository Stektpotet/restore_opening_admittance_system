import csv
import dataclasses
import itertools
from os import times
from typing import List, Tuple, Dict, Optional, Iterable, Set

from datatypes import Person, Registration, RegistrationExtras, Timeslot, AdmittanceStatus, FullRegistration
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
) -> FullRegistration:
    return FullRegistration(
        _normalise(name),
        _normalise(email),
        datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S'),
        [timeslot.replace(' ', '') for timeslot in timeslots.split(',')],
        _normalise(read_rules) == "yes",
        _normalise(student_type),
        _normalise(erasmus) == "yes",
        _normalise(nationality),
        _normalise(sit_residency)
    )


def read_registrations(file_path: str) -> List[FullRegistration]:
    with open(file_path, encoding="utf-8") as registration_file:
        next(reader := csv.reader(registration_file))  # assign reader and skip headers
        return [read_entry(*row) for row in reader]


class OpeningAdmittance:
    timeslots: Dict[str, Timeslot]
    processed: Dict[Person, FullRegistration]
    marked: Set[Person]
    # comment_list
    # TODO Make Dict[Any, Set[Marked]] of marked. that way we can categorise markings (duplicate, suspected duplicate, etc.)

    def __init__(self, timeslots: Dict[str, Timeslot]):
        self.timeslots = timeslots
        self.processed = {}
        self.marked = set()

    def auto_admit(self, registrations: Registration):
        for registration in registrations:
            # Check if already given a spot
            if (person := registration.person) in self.processed.keys():
                # TODO: add checks for changed preferences.
                if set(registration.timeslots) != set(self.processed[person].timeslots):
                    self.processed[person] = registration
                self.marked.add(person)
                break
            else:
                for already_processed_person in self.processed.keys():
                    if registration.person.similar(already_processed_person):
                        self.marked.add(already_processed_person)
                        self.marked.add(registration.person)
                        break
            self.processed[person] = registration

        for registration in self.processed.values():
            for wanted_slot in registration.timeslots:
                if self.timeslots[wanted_slot].admit(registration):
                    break

    def remove_cancelled(self, cancelled: Iterable[Person]):
        pass

    def remove_banned(self, banned: Iterable[Person]):
        pass

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(filetypes=[("Comma Separated Values", "*.csv"), ("All types", "*.*")])
    if file_path == '':
        exit()

    registrations = read_registrations(file_path)
    registrations = list(registrations)
    registrations.sort(key=lambda reg: reg.timestamp)

    admittance = OpeningAdmittance({
        "10:00-11:00": Timeslot(50),
        "11:00-12:00": Timeslot(60),
        "12:00-13:00": Timeslot(70),
        "13:00-14:00": Timeslot(80),
    })

    admittance.auto_admit(registrations)
    print(admittance.timeslots)





