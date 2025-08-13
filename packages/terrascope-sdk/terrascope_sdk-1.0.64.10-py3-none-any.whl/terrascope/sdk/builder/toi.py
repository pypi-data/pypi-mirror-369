import logging
from datetime import datetime
from enum import Enum
from typing import List

from google.protobuf.timestamp_pb2 import Timestamp
from terrascope_api.models.toi_pb2 import TOI, Recurrence, Cadence


class Frequency(Enum):
    UNKNOWN_FREQUENCY = 0
    MINUTELY = 1
    HOURLY = 2
    DAILY = 3
    WEEKLY = 4
    MONTHLY = 5
    YEARLY = 6


class TOIBuilder:
    def __init__(self):
        self.__recurrences = []
        self.__toi = None
        self.__exclusion_dates = None

    def build_toi(self, start: datetime, finish: datetime, description: str = None):
        """
        The TOI service is responsible for determining what data a Computation should process.
        TOIs define the time period from which input data should be taken for a Computation or Analysis.
        The times specified in TOIs are not tied to time zones or UTC time - they are “floating” times.

        **Algorithm Impacts:**
        If an Algorithm has a *grouping* strategy of TOI defined in the algorithm manifest, then DEM will use the
        TOI configuration to ensure data delivered to an algorithm job meets the time interval unit specifications
        defined here.

        If an Algorithm does not have a *grouping* strategy of TOI defined in the algorithm manifest, then DEM will not
        consider time as a relevant data chunk and will deliver data to an Algorithm Job however it sees fit. The
        Algorithm must be designed in a way where the time groups DO NOT MATTER to the final results delivered.

        :param start: local start time (datetime)
        :param finish: local finish time (datetime)
        :param description: a description of the TOI
        :return:
        """
        start_ts = Timestamp()
        start_ts.FromDatetime(start)
        finish_ts = Timestamp()
        finish_ts.FromDatetime(finish)
        toi = TOI(
            start_local=start_ts,
            finish_local=finish_ts
        )
        if description is not None:
            toi.MergeFrom(TOI(description=description))
        self.__toi = toi

    def build_recurrence(self, rrule: str, cadence: Cadence = None):
        """
        Recurrences provide greater control over what data should be processed by a Computation. They replace the
        concept of dwell start and dwell end times in Platform 1.0.

        Recurrences include a rule and a duration. They leverage the power of iCalendar to define complex rules such as:

            - Monday-Friday for three months
            - Monday-Friday from 9am to 5pm for a year
            - Monday-Friday from 9am to 5pm for a year except holidays
            - Tuesday and Thursday every other week
            - Monday-Friday 8am to 6pm, Saturday-Sunday 9am to 5pm

        The rule maps to the iCalendar Recurrence Rule property. To learn more about recurrence rules, the rrule.js site
        provides an excellent online rule generator.

        online-rule-tool: https://jakubroztocil.github.io/rrule/

        :param rrule: Use RRuleBuilder.build_rule to get a valid rule string.
        :param cadence: [Optional] Cadence
        :return: None
        """
        if cadence is not None:
            self.__recurrences.append(Recurrence(rule=rrule, cadence=cadence))
        else:
            self.__recurrences.append(Recurrence(rule=rrule))

    def build_exclusion_dates(self, exclusion_dates: List[datetime]):
        """
        A list of dates
        :param exclusion_dates:
        :return:
        """
        for exclusion_date in exclusion_dates:
            self.__exclusion_dates.append(Timestamp().FromDateTime(exclusion_date))

    def get(self):
        assert self.__recurrences is not None
        toi = TOI()
        toi.MergeFrom(self.__toi)
        toi.MergeFrom(TOI(recurrences=self.__recurrences))
        if self.__exclusion_dates is not None:
            toi.MergeFrom(self.__exclusion_dates)
        return toi


class TOIRuleBuilder:
    @staticmethod
    def build_rule(**kwargs):
        """
        This is a basic class that follows the https://icalendar.org/RFC-Specifications/iCalendar-RFC-5545/
        specification. use this to construct rules for the given TOIBuilder

        UNTIL - If present, will override the TOI finish

         recur           = recur-rule-part *( ";" recur-rule-part )
                 ;
                 ; The rule parts are not ordered in any
                 ; particular sequence.
                 ;
                 ; The FREQ rule part is REQUIRED,
                 ; but MUST NOT occur more than once.
                 ;
                 ; The UNTIL or COUNT rule parts are OPTIONAL,
                 ; but they MUST NOT occur in the same 'recur'.
                 ;
                 ; The other rule parts are OPTIONAL,
                 ; but MUST NOT occur more than once.

        :param kwargs:
            - frequency: Frequency, the rate of occurrences,
            - interval: int, the step for the frequency. Frequency.Daily w/ interval=2 is every other day,
            - until: str, datetime format %Y%m%dT%H%M%SZ the future date to end by,
            - count: int, the number of occurrences,

        :return: rule: str - the RRule for a recurrence
        """
        valid_args = ['frequency', 'interval', 'until', 'count']
        assert len(kwargs.keys()) <= 3
        assert valid_args[0] and valid_args[1] in kwargs.keys()
        # Assume until and count are mutually exclusive to a rule
        assert valid_args[2] or valid_args[3] not in kwargs.keys()

        for key in kwargs.keys():
            if key not in valid_args:
                assert key in kwargs.keys()

        rule = "FREQ={};INTERVAL={}".format(Frequency(kwargs['frequency']).name, kwargs['interval'])
        if 'until' in kwargs.keys():
            logging.info("Rule contains [UNTIL] option - OVERRIDING TOI finish time")
            rule = rule + ";UNTIL={}".format(kwargs['until'])

        if 'count' in kwargs.keys():
            rule = rule + ";COUNT={}".format(kwargs['count'])

        return rule


class TOICadenceBuilder:
    @staticmethod
    def build_cadence(frequency: Frequency, value: int):
        """

        Cadences consist of a frequency and an interval. The frequency takes one of following values:
            - Minutely
            - Hourly
            - Daily
            - Weekly
            - Monthly
            - Yearly

        The interval is the value to apply to the frequency. Example group cadences would include:
            - 1 hour
            - 12 hours
            - 5 day
            - 2 weeks
            - 3 months
            - 1 year

        :param frequency:
        :param value:
        :return:
        """
        return Cadence(frequency=frequency, value=value)
