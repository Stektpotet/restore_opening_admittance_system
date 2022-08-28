import pytest

from admittance import OpeningAdmittance, LimitedTimeslot
from form_data import Person

def test_cancel():
    admittance = OpeningAdmittance({'test': LimitedTimeslot(10)})
    person = Person("test mc tester", "test@gmail.com")
    similar = Person("test mc tester", "test@gmail.con")
    admittance.timeslots['test'].admit(person)
    admittance.timeslots['test'].admit(similar)
    assert (person in admittance.timeslots['test'].spots)
    admittance.cancel(person)
    assert (person in admittance.cancelled)
    assert (similar in admittance.marked.keys())
