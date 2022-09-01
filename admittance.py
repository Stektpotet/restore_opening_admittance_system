import csv
import os
import warnings
from multiprocessing.pool import Pool
from typing import List, Dict, Iterable, Optional, Set, Union

import openpyxl as xl

from form_data import Person, Registration
from datetime import datetime


def _normalise(field: str) -> str:
    return field.lower().strip()


def read_registrations(file_path: str) -> List[Registration]:
    with open(file_path, encoding="utf-8") as registration_file:
        next(reader := csv.reader(registration_file))  # assign reader and skip headers
        return [
            Registration(
                _normalise(name),
                _normalise(mail),
                datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S'),
                [timeslot.replace(' ', '') for timeslot in timeslots.split(',')])
            for timestamp, mail, name, timeslots, *_ in reader
        ]


def read_people_table(file_path: str, name_column: int, email_column: int) -> List[Person]:
    with open(file_path, encoding="utf-8") as person_table_file:
        next(table_reader := csv.reader(person_table_file))  # skip headers and assign to table_reader
        return [Person(_normalise(row[name_column]), _normalise(row[email_column])) for row in table_reader]


class Timeslot:
    spots: List[Person]
    disallowed: Set[Person]  # The people who are not allowed to attend this timeslot

    def __init__(self, disallowed: Optional[Set[Person]] = None):
        self.spots = []
        self.disallowed = disallowed or set()

    @property
    def spots_taken(self):
        return len(self.spots)

    def __str__(self):
        content = ', '.join(f"{k}: {str(v)}" for k, v in self.__dict__.items())
        return f"Timeslot({content})"

    def __repr__(self):
        content = ', '.join(f"{k}: {str(v)}" for k, v in self.__dict__.items())
        return f"Timeslot({content})"

    def admit(self, person: Person) -> bool:
        if person in self.disallowed:
            return False
        self.spots.append(person)
        return True

    def remove(self, person: Person) -> bool:
        try:
            self.spots.remove(person)
            return True
        except ValueError:
            return False


class LimitedTimeslot(Timeslot):
    capacity: int

    def __init__(self, capacity: int):
        super().__init__()
        self.capacity = capacity

    @property
    def spots_available(self):
        return self.capacity - self.spots_taken

    def admit(self, person: Person) -> bool:
        if person in self.disallowed:
            return False
        if self.spots_available > 0:
            self.spots.append(person)
            return True
        return False


class OpeningAdmittance:
    timeslots: Dict[str, Timeslot]
    processed: Dict[Person, Registration]
    cancelled: Set[Person]
    banned: Set[Person]
    marked: Dict[Person, str]

    def __init__(self, timeslots: Optional[Dict[str, Timeslot]] = None):
        self.timeslots = timeslots if timeslots else {}
        self.waiting_list = []
        self.cancelled = set()
        self.banned = set()
        self.marked = {}

    def clear(self):
        for timeslot in self.timeslots.values():
            timeslot.spots.clear()
        self.processed.clear()
        self.cancelled.clear()
        self.banned.clear()
        self.marked.clear()

    def _preprocess_and_mark(self, registrations: Iterable[Registration]):
        """
        Look through all regisstrations beforehand to mark individuals for manual checking if needed
        and overwrite duplicate registrations by the latest entry from said person if the latest entry makes changes
        to their preferences in timeslot
        :param registrations: All entries from the registration form
        :return: registrations without duplicate entries (NOTE: suspected duplicates are only marked for manual check
                 and will remain as separate registrations)
        """
        proccessed_for_admission = {}
        for registration in registrations:
            if registration.person in self.banned:
                self.marked[registration.person] = "Banned from attending, see ban list!"
                continue

            if all(registration.person in timeslot.disallowed for timeslot in self.timeslots.values()):
                self.marked[registration.person] = "Banned from attending the timeslots they signed up for, " \
                                                   "attended previous opening in the early slot(s)!"
                continue

            # Check if already given a spot
            if (person := registration.person) in proccessed_for_admission.keys():
                # TODO: only overwrite entry if change in timeslots
                if set(registration.timeslots) != set(proccessed_for_admission[person].timeslots):
                    # NOTE: changing your timeslots has its drawback - you're now later in the queue
                    reason = f"Duplicate Entry for {person}:\noverwriting {proccessed_for_admission[person]}...\n"\
                             f"timestamp changed from {proccessed_for_admission[person].timestamp} to {registration.timestamp}\n"\
                             f"changed timeslots from {proccessed_for_admission[person].timeslots} to {registration.timeslots}"
                    self.marked[person] = reason
                else:
                    # if no substantial change is made, don't reprocess the person. They did as intended the first
                    # time around and should not be punished for trying to make sure they registered.
                    continue
            else:
                for already_processed_person, already_processed_registration in proccessed_for_admission.items():
                    if registration.person.similar(already_processed_person):
                        self.marked[already_processed_person] = f"Suspected duplicate of {registration}"
                        self.marked[registration.person] = f"Suspected duplicate of {already_processed_registration}"
                        break
            proccessed_for_admission[person] = registration
        return proccessed_for_admission

    def auto_admit(self, registrations: Iterable[Registration]):
        self.processed = self._preprocess_and_mark(registrations)
        for registration in self.processed.values():
            if not any(self.timeslots[wanted_slot].admit(registration) for wanted_slot in registration.timeslots):
                self.waiting_list.append(registration)

    # def cancel(self, cancelled: Union[Iterable[Person], Person]):
    #     if isinstance(cancelled, Person):
    #         cancelled = (cancelled,)  # make iterable
    #     for person in cancelled:
    #         removed = False
    #         for timeslot in self.timeslots.values():
    #             for other in timeslot.spots.copy():
    #                 if person == other:
    #                     removed = timeslot.remove(person)
    #                     self.cancelled.add(person)
    #                 elif person.similar(other):
    #                     self.marked[other] = f"{self.marked.get(other, '')} Might have cancelled! " \
    #                                           f"{person} cancelled, and {other} might be the same person."
    #         if not removed:
    #             warnings.warn(f"Unable to cancel for {person}! They were not found in timeslots!")
    #         # TODO: also look in waiting lists, they should be removed from it too!
    #
    # def ban(self, banned: Union[Iterable[Person], Person]):
    #     if isinstance(banned, Person):
    #         banned = (banned,)  # make iterable
    #     for person in banned:
    #         removed = False
    #         for timeslot in self.timeslots.values():
    #             for other in timeslot.spots.copy():
    #                 if person == other:
    #                     removed = timeslot.remove(person)
    #                     self.banned.add(person)
    #                 else:
    #                     if person.similar(other):
    #                         self.marked[other] = f"{self.marked.get(other, '')} Might have been banned! " \
    #                                               f"{person} is banned, and {other} might be the same person."
    #         if not removed:
    #             warnings.warn(f"Unable to ban {person}! They were not found in timeslots!")
    #         # TODO: also look in waiting lists, they should be banned from it too!

    def write_to_spreadsheets(self, destination: str):
        workbook = xl.Workbook()
        for i, (timeslot_name, timeslot) in enumerate(self.timeslots.items()):
            timeslot_name = timeslot_name.replace(':', '_')
            sheet = workbook.create_sheet(timeslot_name, i)
            sheet.append(["Name", "Email", "Wanted Timeslots", "Remarks"])
            for j, registration in enumerate(self.processed[person] for person in timeslot.spots):
                sheet.append([
                    registration.person.name,
                    registration.person.email,
                    ", ".join(registration.timeslots),
                    self.marked.get(registration.person, "")
                ])

        waiting_list_sheet = workbook.create_sheet("Waiting List", len(self.timeslots))
        waiting_list_sheet.append(["Name", "Email", "Wanted Timeslots", "Remarks"])
        for j, registration in enumerate(self.waiting_list):
            waiting_list_sheet.append([
                registration.person.name,
                registration.person.email,
                ", ".join(registration.timeslots),
                self.marked.get(registration.person, "")
            ])
        cancelled_list_sheet = workbook.create_sheet("Cancelled", len(self.timeslots) + 1)
        cancelled_list_sheet.append(["Name", "Email", "Remarks"])
        for j, person in enumerate(self.cancelled):
            cancelled_list_sheet.append([
                person.name,
                person.email,
                self.marked.get(person, "")
            ])
        banned_list_sheet = workbook.create_sheet("Banned", len(self.timeslots) + 2)
        banned_list_sheet.append(["Name", "Email", "Remarks"])
        for j, person in enumerate(self.banned):
            banned_list_sheet.append([
                person.name,
                person.email,
                self.marked.get(person, "")
            ])
        marked_list_sheet = workbook.create_sheet("All Remarks", len(self.timeslots) + 3)
        marked_list_sheet.append(["Name", "Email", "Remarks"])
        for j, (person, remark) in enumerate(self.marked.items()):
            marked_list_sheet.append([
                person.name,
                person.email,
                remark
            ])
        workbook.save(destination + "/output.xlsx")

    def write_to_csv(self):
        os.makedirs("./output/", exist_ok=True)
        for name, timeslot in self.timeslots.items():
            with open(f"./output/{name.replace(':', '')}.csv", 'w', newline='', encoding="utf-8") as file:
                fields = timeslot.spots[0].__dict__.keys()
                writer = csv.DictWriter(file, fields)
                writer.writeheader()
                for registration in timeslot.spots:
                    writer.writerow({k: v for k, v in registration.__dict__.items() if k in fields})

        with open(f"./output/waiting_list.csv", 'w', newline='', encoding="utf-8") as file:
            fields = self.waiting_list[0].__dict__.keys()
            writer = csv.DictWriter(file, fields)
            writer.writeheader()
            for registration in self.waiting_list:
                writer.writerow({k: v for k, v in registration.__dict__.items() if k in fields})

        with open(f"./output/marked.csv", 'w', newline='', encoding="utf-8") as file:
            marked_list = [(reg.person, reason) for reg, reason in self.marked.items()]
            fields = [*marked_list[0][0].__dict__.keys(), "marked reason"]
            writer = csv.DictWriter(file, fields)
            writer.writeheader()
            for person, reason in marked_list:
                entry = {k: v for k, v in person.__dict__.items() if k in fields}
                entry["marked reason"] = reason
                writer.writerow(entry)
