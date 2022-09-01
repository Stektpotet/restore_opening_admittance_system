from __future__ import annotations
from dataclasses import dataclass, field
import datetime
from difflib import SequenceMatcher
from itertools import permutations

def _seq_ignore_space(c: str):
    return c in " \t\r\n"


@dataclass(frozen=True, eq=True)
class Person:
    name: str
    email: str

    @property
    def person(self):
        return Person(self.name, self.email)

    def similar(self, other: Person, similarity_threshold: float = 0.9) -> bool:
        # Consider permutations of name order, last name before first name etc.

        email_similarity = SequenceMatcher(_seq_ignore_space, self.email, other.email).ratio()
        if email_similarity > similarity_threshold:
            return True


        # Evaluate all permutations of other's name consisting of same number of sub-names as self
        #   Example:    self:   Ola Nordmann
        #               other:  Per Nordmann Ola
        #       This will make permutations of other of length: len("Ola Nordmann".split(' ')) = 2
        #       Permutations made: (Per Nordmann, Per Ola, Nordmann Per, Nordmann Ola, Ola Per, Ola Nordmann)

        name_similarity = 0
        num_sub_names = len(self.name.split(' '))
        seqm = SequenceMatcher(_seq_ignore_space, self.name)
        for name in (' '.join(name_part) for name_part in permutations(other.name.split(' '), num_sub_names)):
            seqm.set_seq2(name)
            if seqm.quick_ratio() < similarity_threshold:  # skip if sets of character doesn't match enough
                continue
            if (ratio := seqm.ratio()) > name_similarity:
                name_similarity = ratio
                if name_similarity > similarity_threshold:
                    return True
        return False


@dataclass(frozen=True)
class Registration(Person):
    timestamp: datetime.datetime = field(compare=False)
    timeslots: [str] = field(compare=False)
    # read_rules: bool = field(compare=False)

    def __eq__(self, other: Registration):
        return self.person.__eq__(other.person)

    @property
    def registration(self):
        return Registration(self.name, self.email, self.timestamp, self.timeslots)


@dataclass(frozen=True, eq=True)
class RegistrationExtras:
    student_type: str = field(compare=False)
    erasmus: bool = field(compare=False)
    nationality: str = field(compare=False)
    sit_residency: str = field(compare=False)

    @property
    def extras(self):
        return RegistrationExtras(self.student_type, self.erasmus, self.nationality, self.sit_residency)


@dataclass(frozen=True)
class FullRegistration(RegistrationExtras, Registration):

    def __eq__(self, other: FullRegistration):
        return self.person.__eq__(other.person)


if __name__ == '__main__':
    a = Person("Halvor Bakken Smedås", "halvor@restore-trd.no")
    b = Person("Halvor Bakken Smedås", "halvor@restore-trd.no")
    # others = [
    #     Person("Halvor Bakken Smedås", "halvor@restore-trd.no"),
    #     Person("Klara Schlüter", "halvor@restore-trd.no"),
    #     Person("Bakken Smedås", "halvor@restore-trd.no"),
    #     Person("Halvor Smedås", "halvor@restore-trd.no"),
    #     Person("Halvor Smedås", "halvor@restore-trd.n"),
    # ]
    #
    # for b in others:
    #     if not a == b:
    #         print("Not the same:", a, b)
    #     if not a.similar(b):
    #         print("Not similar:", a, b)