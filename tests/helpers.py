#
# Contains helper functions for testing
#

from random import randint, choice
from datetime import datetime, date, timedelta
from copy import copy
from scripts.helpers import RACE_MAP
import string


UNKNOWN_ID = 'UN'

#
# The following distribution are based on analysis of inmates collected from
# Cook County Jail from January 1st, 013 to November 1st, 2013
#
# The distribution was scaled to 1000, a slight skew was introduced to handle
# A and U race inmates by scaling them up to 1.
#
FEMALE_DISTRIBUTION = [
    [1, 1, 'A'],
    [2, 6, 'AS'],
    [7, 8, 'B'],
    [9, 708, 'BK'],
    [709, 710, 'IN'],
    [711, 715, 'LB'],
    [716, 745, 'LT'],
    [746, 806, 'LW'],
    [807, 807, UNKNOWN_ID],
    [808, 809, 'W'],
    [810, 1000, 'WH']
]

MALE_DISTRIBUTION = [
    [1, 1, 'A'],
    [2, 7, 'AS'],
    [8, 8, 'B'],
    [9, 714, 'BK'],
    [715, 715, 'IN'],
    [716, 718, 'LB'],
    [719, 819, 'LT'],
    [820, 885, 'LW'],
    [886, 886, UNKNOWN_ID],
    [887, 888, 'W'],
    [889, 1000, 'WH']
]


BOOKED = 'booked'
BOOKING_DATE = 'booking_date'
DATE = 'date'
DISCHARGE_DATE_EARLIEST = 'discharge_date_earliest'
GENDER = 'gender'
IN_JAIL = 'in_jail'
LEFT = 'left'
POPULATION = 'population'
RACE = 'race'

ACTIONS = [BOOKED, LEFT]

EXCLUDE_SET = {DATE}

GENDER_NAME_MAP = {'F': 'females', 'M': 'males'}
GENDERS = ['F', 'M']
DAY_BEFORE = '2013-07-21'
STARTING_DATE = '2013-07-22'
NEXT_DAY = '2013-07-23'
NAME_FORMATTER = '%s_%s'

RACE_COUNTS = {'AS': 0, 'BK': 0, 'IN': 0, 'LT': 0, UNKNOWN_ID: 0, 'WH': 0}

JAIL_ID = 'jail_id'

RACE_IDS_MAP = {
    'A': 'AS',
    'AS': 'AS',
    'B': 'BK',
    'BK': 'BK',
    'IN': 'IN',
    'LB': 'LT',
    'LT': 'LT',
    'LW': 'LT',
    'W': 'WH',
    'WH': 'WH'
}


def add_jail_id(inmates):
    for inmate in inmates:
        inmate[JAIL_ID] = str(id(inmate))
    return inmates


def change_counts(inmates):
    starting_datetime = STARTING_DATE + 'T00:00:00'
    counts = initialize_change_counts()
    for inmate in inmates:
        action = BOOKED if inmate[BOOKING_DATE] == starting_datetime else LEFT
        race = inmate[RACE]
        race = RACE_MAP[race] if race in RACE_MAP else UNKNOWN_ID
        # noinspection PyTypeChecker
        counts[inmate[GENDER]][action][race] += 1
    return counts


def convert_hash_values_to_integers(hash_to_convert, excluding):
    for key, value in hash_to_convert.iteritems():
        if key not in excluding:
            hash_to_convert[key] = int(value)


def count_gender_in_jail(gender, race, inmates):
    count = 0
    for inmate in inmates:
        if inmate[IN_JAIL] and inmate[GENDER] == gender and inmate[RACE] == race:
            count += 1
    return count


def count_gender_race(gender, race, inmates):
    count = 0
    for inmate in inmates:
        if inmate[GENDER] == gender and inmate[RACE] == race:
            count += 1
    return count


def count_population(inmates, population_date=None, calculate_totals=True):
    counts = {}
    if population_date:
        counts[DATE] = population_date
    for gender in GENDERS:
        counts[gender] = {POPULATION: copy(RACE_COUNTS), IN_JAIL: copy(RACE_COUNTS)}
    for gender in GENDERS:
        g_p = counts[gender][POPULATION]
        g_p['AS'] = count_gender_race(gender, 'A', inmates) + count_gender_race(gender, 'AS', inmates)
        g_p['BK'] = count_gender_race(gender, 'B', inmates) + count_gender_race(gender, 'BK', inmates)
        g_p['IN'] = count_gender_race(gender, 'IN', inmates)
        g_p['LT'] = count_gender_race(gender, 'LB', inmates) + count_gender_race(gender, 'LT', inmates) + \
            count_gender_race(gender, 'LW', inmates)
        g_p[UNKNOWN_ID] = count_gender_race(gender, UNKNOWN_ID, inmates)
        g_p['WH'] = count_gender_race(gender, 'W', inmates) + count_gender_race(gender, 'WH', inmates)
    for gender in GENDERS:
        g_ij = counts[gender][IN_JAIL]
        g_ij['AS'] = count_gender_in_jail(gender, 'A', inmates) + count_gender_in_jail(gender, 'AS', inmates)
        g_ij['BK'] = count_gender_in_jail(gender, 'B', inmates) + count_gender_in_jail(gender, 'BK', inmates)
        g_ij['IN'] = count_gender_in_jail(gender, 'IN', inmates)
        g_ij['LT'] = count_gender_in_jail(gender, 'LB', inmates) + count_gender_in_jail(gender, 'LT', inmates) + \
            count_gender_in_jail(gender, 'LW', inmates)
        g_ij[UNKNOWN_ID] = count_gender_in_jail(gender, UNKNOWN_ID, inmates)
        g_ij['WH'] = count_gender_in_jail(gender, 'W', inmates) + count_gender_in_jail(gender, 'WH', inmates)
    if calculate_totals:
        for gender in GENDERS:
            total = 0
            for count in counts[gender][POPULATION].itervalues():
                total += count
            field_name = population_field_name(gender)
            counts[field_name] = total
        counts[POPULATION] = counts[population_field_name('F')] + counts[population_field_name('M')]
        for gender in GENDERS:
            counts[in_jail_field_name(gender)] = 0
        for inmate in inmates:
            if inmate[IN_JAIL]:
                gender = inmate[GENDER]
                field_name = in_jail_field_name(gender)
                counts[field_name] += 1
                counts[gender][IN_JAIL][RACE_IDS_MAP[inmate[RACE]]] += 1
        counts[IN_JAIL] = counts[in_jail_field_name('F')] + counts[in_jail_field_name('M')]
    return counts


def discharged_null_inmate_records(number_to_make):
    starting_datetime = STARTING_DATE + 'T00:00:00'
    how_many_to_make = {'F': number_to_make / 2, 'M': number_to_make}
    return add_jail_id([{GENDER: gender, RACE: pick_race(gender), BOOKING_DATE: starting_datetime,
                         DISCHARGE_DATE_EARLIEST: None, IN_JAIL: random_in_jail()}
                        for gender, count in how_many_to_make.iteritems() for i in range(0, count)])


def discharged_on_or_after_start_date_inmate_records(number_to_make, discharged_date='Random'):
    how_many_to_make = {'F': number_to_make / 2, 'M': number_to_make}
    discharge_date = RandomDates(discharged_date)
    return add_jail_id([{GENDER: gender, RACE: pick_race(gender), BOOKING_DATE: DAY_BEFORE,
                         DISCHARGE_DATE_EARLIEST: discharge_date.next(), IN_JAIL: random_in_jail()}
                        for gender, count in how_many_to_make.iteritems() for i in range(0, count)])


def expected_starting_population(population_counts):
    expected = {
        DATE: DAY_BEFORE,
        POPULATION: population_counts[POPULATION]
    }
    for gender in GENDERS:
        for action in ACTIONS:
            expected[action] = 0
            base_field_name = NAME_FORMATTER % (GENDER_NAME_MAP[gender], action)
            expected[base_field_name] = 0
            for race in RACE_COUNTS.iterkeys():
                expected[NAME_FORMATTER % (base_field_name, race.lower())] = 0
    for gender in GENDERS:
        base_field_name = population_field_name(gender)
        expected[base_field_name] = population_counts[base_field_name]
        action_base_field_name = NAME_FORMATTER % (GENDER_NAME_MAP[gender], BOOKED)
        for race, count in population_counts[gender].iteritems():
            field_name = NAME_FORMATTER % (base_field_name, race.lower())
            expected[field_name] = count
            expected[NAME_FORMATTER % (action_base_field_name, race.lower())] = 0
    return expected


def initialize_change_counts(cur_date=STARTING_DATE):
    counts = {DATE: cur_date}
    for gender in GENDERS:
        counts[gender] = {
            BOOKED: copy(RACE_COUNTS),
            LEFT: copy(RACE_COUNTS)
        }
    return counts


def inmate_population():
    low, high = 34, 51
    return discharged_null_inmate_records(randint(low, high)) +\
        discharged_on_or_after_start_date_inmate_records(randint(low, high))


def in_jail_field_name(gender):
    return 'females_in_jail' if gender == 'F' else 'males_in_jail'


def map_race_id(source_race_id):
    if source_race_id in RACE_IDS_MAP:
        return RACE_IDS_MAP[source_race_id]
    return UNKNOWN_ID


def pick_race(gender):
    distribution = FEMALE_DISTRIBUTION if gender == 'F' else MALE_DISTRIBUTION
    point = randint(1, 1000)
    for race_info in distribution:
        if race_info[0] <= point <= race_info[1]:
            return race_info[2]


def population_field_name(gender):
    return 'females_population' if gender == 'F' else 'males_population'


def random_in_jail():
    return choice([True, False, True, True, True, True, True, True, False, True])


def random_string(str_length=10):
    return ''.join([choice(string.ascii_letters + string.digits) for _ in xrange(str_length)])


class RandomDates:

    def __init__(self, starting_date):
        if starting_date.lower() == 'random':
            self._starting_date = datetime.strptime(NEXT_DAY, '%Y-%m-%d').date()
            self._number_days = (date.today() - self._starting_date).days - 1
            self._one_day = timedelta(1)
            self._next = self._random_next
        else:
            self._starting_date = starting_date
            self._next = self._static_next

    def next(self):
        return self._next()

    def _random_next(self):
        return str(self._starting_date + (self._one_day * randint(0, self._number_days))) + 'T01:01:01'

    def _static_next(self):
        return self._starting_date


class UpdatePopulationCounts:

    def __init__(self, starting_population_counts, population_change_counts):
        self._population_change_counts = population_change_counts
        self._new_population_counts = copy(starting_population_counts)
        self._new_population_counts[DATE] = population_change_counts[DATE]

    def dpc_format(self):
        self._update_counts()
        return self._dpc_format()

    def _dpc_format(self):
        dpc_formatted = {DATE: self._new_population_counts[DATE]}
        dpc_formatted[POPULATION] = self._new_population_counts[POPULATION]
        for gender in GENDERS:
            base_field_name = population_field_name(gender)
            dpc_formatted[base_field_name] = self._new_population_counts[base_field_name]
            for race, counts in self._new_population_counts[gender].iteritems():
                dpc_formatted[NAME_FORMATTER % (base_field_name, race.lower())] = counts
        dpc_formatted[BOOKED] = 0
        dpc_formatted[LEFT] = 0
        for gender in GENDERS:
            for action, race_counts in self._population_change_counts[gender].iteritems():
                base_field_name = NAME_FORMATTER % (GENDER_NAME_MAP[gender], action)
                dpc_formatted[base_field_name] = 0
                for race, counts in race_counts.iteritems():
                    dpc_formatted[action] += counts
                    dpc_formatted[base_field_name] += counts
                    dpc_formatted[NAME_FORMATTER % (base_field_name, race.lower())] = counts
        return dpc_formatted

    def _update_counts(self):
        self._new_population_counts[POPULATION] = 0
        for gender in GENDERS:
            self._update_booked(gender)
            self._update_left(gender)
            self._new_population_counts[POPULATION] += self._new_population_counts[population_field_name(gender)]

    def _update_booked(self, gender):
        field_name = population_field_name(gender)
        for race, counts in self._population_change_counts[gender][BOOKED].iteritems():
            self._new_population_counts[field_name] += counts
            self._new_population_counts[gender][race] += counts

    def _update_left(self, gender):
        field_name = population_field_name(gender)
        for race, counts in self._population_change_counts[gender][LEFT].iteritems():
            self._new_population_counts[field_name] -= counts
            self._new_population_counts[gender][race] -= counts
