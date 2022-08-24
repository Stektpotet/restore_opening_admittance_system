from __future__ import annotations
from dataclasses import dataclass, field
import datetime
from difflib import SequenceMatcher
from itertools import permutations
from typing import List, Tuple, Set
from enum import Enum, Flag, IntFlag


def _seq_ignore_space(c: str):
    return c in " \t\r\n"


@dataclass(frozen=True, eq=True)
class Person:
    name: str
    email: str

    def similar(self, other: Person, similarity_threshold: float = 0.9) -> bool:
        # Consider permutations of name order, last name before first name etc.
        name_similarity = 0
        sub_names = other.name.split(' ')
        for n in range(len(sub_names), 1, -1):
            for name in (' '.join(names) for names in (permutations(sub_names, n))):
                if (ratio := SequenceMatcher(_seq_ignore_space, self.name, name).ratio()) > name_similarity:
                    name_similarity = ratio
                    if name_similarity > similarity_threshold:
                        return True

        email_similarity = SequenceMatcher(_seq_ignore_space, self.email, other.email).ratio()
        return name_similarity > similarity_threshold or email_similarity > similarity_threshold


@dataclass(frozen=True)
class Registration(Person):
    timestamp: datetime.datetime
    timeslots: [str]
    read_rules: bool

    @property
    def person(self):
        return Person(self.name, self.email)


@dataclass(frozen=True)
class RegistrationExtras:
    student_type: str
    erasmus: bool
    nationality: str
    sit_residency: str

@dataclass(frozen=True)
class FullRegistration(RegistrationExtras, Registration):

    @property
    def person(self):
        return Person(self.name, self.email)

    @property
    def registration(self):
        return Registration(self.name, self.email, self.timestamp, self.timeslots, self.read_rules)

    @property
    def extras(self):
        return RegistrationExtras(self.student_type, self.erasmus, self.nationality, self.sit_residency)



class AdmittanceStatus(IntFlag):
    Waiting_List = 0,
    Admitted = 1,
    Marked = 2



class Timeslot:
    capacity: int
    spots: List[Person]
    waiting_list: List[Person]
    marked: Set[Person]

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.spots = []
        self.waiting_list = []
        self.marked = set()

    def __str__(self):
        content = ', '.join(f"{k}: {str(v)}" for k, v in self.__dict__.items())
        return f"Timeslot({content})"

    def __repr__(self):
        content = ', '.join(f"{k}: {str(v)}" for k, v in self.__dict__.items())
        return f"Timeslot({content})"

    def add(self, person: Person) -> bool:
        if (index := len(self.spots)) < self.capacity:
            for already_admitted in self.spots:
                if person.similar(already_admitted):
                    print("THIS SHOULD NEVER HAPPEN WHEN WE PREPROCESS REGISTRATIONS!")
                    # TODO: Handle marked individuals
            self.spots.append(person)
            return True
        return False


    def admit(self, person: Person) -> Tuple[AdmittanceStatus, int]:
        if (index := len(self.spots)) < self.capacity:
            marked = False
            for already_admitted in self.spots:
                if person.similar(already_admitted):
                    self.marked.add(person)
                    # self.marked.add(already_admitted)
                    marked = True
                    break
                    # TODO: Handle marked individuals

            self.spots.append(person)
            if marked:
                return AdmittanceStatus.Admitted | AdmittanceStatus.Marked, index+1
            return AdmittanceStatus.Admitted, index+1

        self.waiting_list.append(person)
        return AdmittanceStatus.Waiting_List, len(self.waiting_list)


if __name__ == '__main__':
    a = Person("Halvor Bakken Smedås", "halvor@restore-trd.no")
    others = [
        Person("Halvor Bakken Smedås", "halvor@restore-trd.no"),
        Person("Klara Schlüter", "halvor@restore-trd.no"),
        Person("Bakken Smedås", "halvor@restore-trd.no"),
        Person("Halvor Smedås", "halvor@restore-trd.no"),
        Person("Halvor Smedås", "halvor@restore-trd.n"),
    ]

    for b in others:
        if not a == b:
            print("Not the same:", a, b)
        if not a.similar(b):
            print("Not similar:", a, b)