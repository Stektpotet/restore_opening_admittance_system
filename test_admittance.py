import datetime

import pytest

from admittance import OpeningAdmittance, LimitedTimeslot, read_entry
from form_data import Person, Registration

_kate = read_entry("18/08/2022 18:04:40", "katemccoy@gmail.com", "Kate Mccoy", "a, b", "", "yes", "", "yes", "yes")
_barrett = read_entry("18/08/2022 18:04:41", "BarrettIngram@gmail.com", "Barrett Ingram", "a, b", "", "yes", "", "yes", "yes")
_zayden = read_entry("18/08/2022 18:04:42", "ZaydenJenkins@gmail.com", "Zayden Jenkins", "a, b", "", "yes", "", "yes", "yes")
_ruben = read_entry("18/08/2022 18:04:43", "RubenPalmer@gmail.com", "Ruben Palmer", "a, b", "", "yes", "", "yes", "yes")
_jaydon = read_entry("18/08/2022 18:04:44", "JaydonHuff@gmail.com", "Jaydon Huff", "a, b", "", "yes", "", "yes", "yes")
_yamilet = read_entry("18/08/2022 18:04:45", "YamiletWalton@gmail.com", "Yamilet Walton", "a, b", "", "yes", "", "yes", "yes")
_khalil = read_entry("18/08/2022 18:04:46", "KhalilRichards@gmail.com", "Khalil Richards", "a, b", "", "yes", "", "yes", "yes")
_serenety = read_entry("18/08/2022 18:04:47", "SerenityCastaneda@gmail.com", "Serenity Castaneda", "a, b", "", "yes", "", "yes", "yes")
_river = read_entry("18/08/2022 18:04:48", "RiverFry@gmail.com", "River Fry", "a, b", "", "yes", "", "yes", "yes")
_tristen = read_entry("18/08/2022 18:04:49", "TristenLamb@gmail.com", "Tristen Lamb", "a, b", "", "yes", "", "yes", "yes")
_walter = read_entry("18/08/2022 18:04:50", "WalterCarr@gmail.com", "Walter Carr", "a, b", "", "yes", "", "yes", "yes")
_braydon = read_entry("18/08/2022 18:04:51", "BraydonShort@gmail.com", "Braydon Short", "a, b", "", "yes", "", "yes", "yes")

# Arrange
@pytest.fixture
def admittance_filled():
    adm = OpeningAdmittance({'a': LimitedTimeslot(5), 'b': LimitedTimeslot(10)})
    adm.auto_admit([
        _kate, _barrett, _zayden, _ruben, _jaydon, _yamilet, _khalil, _serenety, _river, _tristen, _walter, _braydon
    ])
    return adm

def test_ban(admittance_filled):
    admittance_filled.ban(_kate)
    assert (_kate in admittance_filled.banned)
    assert (_kate not in admittance_filled.timeslots['a'].spots)
    assert (_kate not in admittance_filled.timeslots['b'].spots)
    assert (_kate not in admittance_filled.waiting_list)

def test_cancel(admittance_filled):
    admittance_filled.cancel(_kate)
    assert (_kate in admittance_filled.cancelled)
    assert (_kate not in admittance_filled.timeslots['a'].spots)
    assert (_kate not in admittance_filled.timeslots['b'].spots)
    assert (_kate not in admittance_filled.waiting_list)

def test_waiting_list(admittance_filled):
    waiter = read_entry("18/08/2022 18:04:55", "JordonEmelie@gmail.com", "Jordon Emelie", "a", "", "yes", "", "yes", "yes")
    admittance_filled.auto_admit([waiter])
    assert (waiter in admittance_filled.waiting_list)
    assert (waiter not in admittance_filled.timeslots['a'].spots)
    assert (waiter not in admittance_filled.timeslots['b'].spots)