import csv
import os
import warnings
from multiprocessing.pool import Pool
from typing import List, Dict, Iterable, Optional, Set, Union

from form_data import Person, FullRegistration, Cancellation
from datetime import datetime


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
        reader = csv.reader(registration_file)
        next(reader)

        next(reader := csv.reader(registration_file))  # assign reader and skip headers
        return [read_entry(*row) for row in reader]


class Timeslot:
    spots: List[Person]

    def __init__(self):
        self.spots = []

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
        if self.spots_available > 0:
            self.spots.append(person)
            return True
        return False


class OpeningAdmittance:
    timeslots: Dict[str, Timeslot]
    processed: Dict[Person, FullRegistration]
    cancelled: Set[Person]
    banned: Set[Person]
    marked: Dict[Person, str]

    def __init__(self, timeslots: Optional[Dict[str, Timeslot]] = None):
        self.timeslots = timeslots if timeslots else {}
        self.waiting_list = []
        self.cancelled = set()
        self.marked = {}

    def _preprocess_and_mark(self, registrations: Iterable[FullRegistration]):
        """
        Look through all regisstrations beforehand to mark individuals for manual checking if needed
        and overwrite duplicate registrations by the latest entry from said person if the latest entry makes changes
        to their preferences in timeslot
        :param registrations: All entries from the registration form
        :return: registrations without duplicate entries (NOTE: suspected duplicates are only marked for manual check
                 and will remain as separate registrations)
        """
        processed = {}
        for registration in registrations:
            # Check if already given a spot
            if (person := registration.person) in processed.keys():
                # TODO: only overwrite entry if change in timeslots
                if set(registration.timeslots) != set(processed[person].timeslots):
                    # NOTE: changing your timeslots has its drawback - you're now later in the queue
                    reason = f"Duplicate Entry for {person}: overwriting {processed[person]}...\n"\
                             f"timestamp changed from {processed[person].timestamp} to {registration.timestamp}\n"\
                             f"changed timeslots from {processed[person].timeslots} to {registration.timeslots}"
                    self.marked[person] = reason
                else:
                    # if no substantial change is made, don't reprocess the person. They did as intended the first
                    # time around and should not be punished for trying to make sure they registered.
                    continue
            else:
                for already_processed_person in processed.keys():
                    if registration.person.similar(already_processed_person):
                        self.marked[already_processed_person] = f"Suspected duplicate of {registration.person}"
                        self.marked[registration.person] = f"Suspected duplicate of {already_processed_person}"
                        break
            processed[person] = registration
        return processed

    def auto_admit(self, registrations: Iterable[FullRegistration]):
        for registration in self._preprocess_and_mark(registrations).values():
            if not any(self.timeslots[wanted_slot].admit(registration) for wanted_slot in registration.timeslots):
                self.waiting_list.append(registration)

    def cancel(self, cancelled: Union[Iterable[Person], Person]):
        if isinstance(cancelled, Person):
            cancelled = (cancelled,)  # make iterable
        for person in cancelled:
            removed = False
            for timeslot in self.timeslots.values():
                for other in timeslot.spots.copy():
                    if person == other:
                        removed = timeslot.remove(person)
                        self.cancelled.add(person)
                    elif person.similar(other):
                        self.marked[other] = f"{self.marked.get(other, '')} Might have cancelled! " \
                                              f"{person} cancelled, and {other} might be the same person."
            if not removed:
                warnings.warn(f"Unable to cancel for {person}! They were not found in timeslots!")
            # TODO: also look in waiting lists, they should be removed from it too!

    def ban(self, banned: Union[Iterable[Person], Person]):
        if isinstance(banned, Person):
            banned = (banned,)  # make iterable
        for person in banned:
            removed = False
            for timeslot in self.timeslots.values():
                for other in timeslot.spots.copy():
                    if person == other:
                        removed = timeslot.remove(person)
                    else:
                        if person.similar(other):
                            self.marked[other] = f"{self.marked.get(other, '')} Might have been banned! " \
                                                  f"{person} is banned, and {other} might be the same person."
            if not removed:
                warnings.warn(f"Unable to ban {person}! They were not found in timeslots!")
            # TODO: also look in waiting lists, they should be banned from it too!

    def write_to_spreadsheets(self):
        pass

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
