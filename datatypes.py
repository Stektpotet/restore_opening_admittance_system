from __future__ import annotations
from dataclasses import dataclass, field
import datetime
from difflib import SequenceMatcher

def _seq_ignore_space(c: str):
    return c in " \t\r\n"

@dataclass(frozen=True, eq=True)
class Person:
    name: str
    email: str

    def similar(self, other: Person, similarity_threshold: float = 0.9) -> bool:
        # TODO: Consider reordering of names, last name before first name etc.
        name_similarity = SequenceMatcher(_seq_ignore_space, self.name.strip().lower(),
                                          other.name.strip().lower()).ratio()
        email_similarity = SequenceMatcher(_seq_ignore_space, self.email.strip().lower(),
                               other.email.strip().lower()).ratio()
        return name_similarity > similarity_threshold or email_similarity > similarity_threshold

@dataclass(frozen=True)
class Registration(Person):
    timestamp: datetime.datetime
    timeslots: [str]
    read_rules: bool

@dataclass(frozen=False)
class RegistrationExtras:
    year_of_studies: str
    nationality: str
    sit_residence: bool
    erasmus: bool = field(compare=False)
    location: str

