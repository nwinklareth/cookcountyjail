#
# Fetches the Daily Population values for a date
# and summarizes population changes for it.
#

from copy import copy
from helpers import GENDERS, RACE_COUNTS, RACE_MAP


BOOKED = 'booked'
BOOKING_DATE = 'booking_date'
DATE = 'date'
GENDER = 'gender'
IN_JAIL = 'in_jail'
LEFT = 'left'
POPULATION = 'population'
RACE = 'race'
UNKNOWN_ID = 'UN'


class SummarizeDailyPopulation:

    def __init__(self):
        self._change_counts = None

    @staticmethod
    def calculate_starting_population(inmates, population_date):
        counts = {DATE: population_date}
        for gender in GENDERS:
            counts[gender] = {IN_JAIL: copy(RACE_COUNTS), POPULATION: copy(RACE_COUNTS)}
        for inmate in inmates:
            gender = inmate[GENDER]
            race = SummarizeDailyPopulation.__map_race_id(inmate)
            counts[gender][POPULATION][race] += 1
            if inmate[IN_JAIL]:
                counts[gender][IN_JAIL][race] += 1
        return counts

    def __count_changes(self, inmates, booking_date):
        for inmate in inmates:
            action = BOOKED if inmate[BOOKING_DATE] == booking_date else LEFT
            race = self.__map_race_id(inmate)
            self._change_counts[inmate[GENDER]][action][race] += 1

    def __initialize_change_counts(self, change_date):
        self._change_counts = {DATE: change_date}
        for gender in GENDERS:
            self._change_counts[gender] = {
                BOOKED: copy(RACE_COUNTS),
                LEFT: copy(RACE_COUNTS)
            }

    @staticmethod
    def __map_race_id(inmate):
        race = inmate[RACE]
        return RACE_MAP[race] if race in RACE_MAP else UNKNOWN_ID

    def summarize(self, change_date, inmates):
        """
        Summarizes population change by counting how many inmates where booked and how many where discharged
        Assumes that the parameter inmates contains only the set of inmates booked and the set of inmates
        discharged for the date specified in parameter change_date
        """
        self.__initialize_change_counts(change_date)
        self.__count_changes(inmates, change_date + 'T00:00:00')
        return self._change_counts
