from os import path

import pendulum
import scrapy
from datetime import timedelta
import dateparser

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"


class BaseScraper(scrapy.Spider):
    timezone = ""
    timeslot_day = ''
    timeslot_number = 0
    elapsed_hours = 0
    referred_link = ''
    ranked = 0
    edition = []
    time_slots_ending_hour = [1, 4, 7, 10, 13, 16, 19, 22]

    def parse(self, response):
        [day, timeslot_no] = self.calculateTimeSlot(self.calculate_local_time())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no
        self.elapsed_hours = self.getEsapsedHourEndingTimeslot(self.calculate_local_time())

    def calculate_local_time(self):
        pen = pendulum.now()
        return pen.in_timezone(self.timezone).to_datetime_string()

    def calculateTimeSlot(self, dt: str):
        dt = dateparser.parse(dt)
        day = dt.date()
        hour = dt.hour
        if hour in [2, 3, 4]:
            return [day, 1]
        if hour in [5, 6, 7]:
            return [day, 2]
        if hour in [8, 9, 10]:
            return [day, 3]
        if hour in [11, 12, 13]:
            return [day, 4]
        if hour in [14, 15, 16]:
            return [day, 5]
        if hour in [17, 18, 19]:
            return [day, 6]
        if hour in [20, 21, 22]:
            return [day, 7]
        if hour == 23:
            return [day, 8]
        if hour in [0, 1]:
            return [dt.now() - timedelta(days=1), 8]

    def previousTimeSlot(self, day, timeslot_no: int):
        timeslot_no = timeslot_no - 1
        if timeslot_no == 0:
            timeslot_no = 8
            day = day - timedelta(days=1)
        return [day, timeslot_no]

    def getEsapsedHourEndingTimeslot(self, dt: str) -> int:
        dt = dateparser.parse(dt)
        hour = dt.hour
        max_not_ended = self.time_slots_ending_hour[0]
        for ending_hour in self.time_slots_ending_hour:
            if ending_hour < hour and max_not_ended < ending_hour:
                max_not_ended = ending_hour
        return hour - max_not_ended - 1
