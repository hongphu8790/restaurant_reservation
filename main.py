import csv
from datetime import timedelta, datetime, date
import re

TIME_FORMAT1 = "%I:%M %p"
TIME_FORMAT2 = "%I %p"

REGEX_PARSE_PERIOD = r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)-(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\d{1,2}:?\d{0,2}\s+(am|pm))\s+-\s+(\d{1,2}:?\d{0,2}\s+(am|pm))"
DATE_DICTIONARY = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}


class Restaurant:

    def __init__(self):
        self.periods = []
        self.name = None

    def __init__(self, name):
        self.periods = []
        self.name = name

    def add_periods(self, periods):
        self.periods = periods

    def check_time_available(self, book_on, book_at_str, duration_in_minutes):
        for period in self.periods:
            if period.check_booking_in_date(book_on) and period.check_booking_in_duration(book_at_str, duration_in_minutes):
                return True
        return False

    def __repr__(self):
        return self.name


class ReservablePeriod:

    def __init__(self, from_date_str, to_date_str, open_time_str, close_time_str):
        self.open_dates = range(DATE_DICTIONARY.get(from_date_str.upper()), DATE_DICTIONARY.get(to_date_str.upper()) + 1)
        self.open_time = self.parse_time(open_time_str)
        self.close_time = self.parse_time(close_time_str)

    def parse_time(self, time_str):
        try:
            timestamp = datetime.strptime(time_str, TIME_FORMAT1).time()
        except ValueError:
            timestamp = datetime.strptime(time_str, TIME_FORMAT2).time()
        return timestamp

    def check_booking_in_date(self, date):
        return date in self.open_dates

    def check_booking_in_duration(self, book_at_str, book_duration_in_minutes):
        book_at = self.parse_time(book_at_str)
        book_to = datetime.combine(date.min, book_at) + timedelta(minutes=book_duration_in_minutes)
        return self.check_booking_in_openhour(book_at, book_to.time())

    def check_booking_in_openhour(self, book_at, book_to):
        return book_at >= self.open_time and book_to <= self.close_time


class Reservation:

    def __init__(self):
        self.restaurants = []

    def load_csv(self, file_name):
        self.restaurants.clear()
        with open(file_name, newline='', encoding='utf-8') as csv_file:
            rows = csv.reader(csv_file, delimiter=',')
            for row in rows:
                restaurant = Restaurant(row[0])
                restaurant.add_periods(self.parse_period(row[1]))
                self.restaurants.append(restaurant)

    def parse_period(self, resource_str):
        matches = re.findall(REGEX_PARSE_PERIOD, resource_str, re.MULTILINE)
        periods = []
        for match in matches:
            if len(match) == 6:
                from_date_str = match[0]
                to_date_str = match[1]
                open_time = match[2]
                close_time = match[4]
                period = ReservablePeriod(from_date_str, to_date_str, open_time, close_time)
                periods.append(period)
        return periods

    def reservation(self, book_on, book_at_str, duration_in_minutes):
        restaurant_allocations = []
        for restaurant in self.restaurants:
            if restaurant.check_time_available(book_on, book_at_str, duration_in_minutes):
                restaurant_allocations.append(restaurant)
        return restaurant_allocations


if __name__ == "__main__":
    reserv = Reservation()
    reserv.load_csv("./restaurant_reservation_hours.csv")

    print("=== RESTAURANT RESERVATION APPLICATION ===")
    try:
        book_on = int(input("Enter a day to book (0: Mon, 1:Tue, 2:Wed, 3:Thu, 4:Fri, 5:Sat, 6:Sun) : "))
        book_at = input("Enter a hour to book (example is 10:00 am) : ")
        book_duration = int(input("Enter a duration time to book (in minutes) : "))
        #book_on = 6
        #book_at = "10:00 pm"
        #book_duration = 40

        #book_on = 0
        #book_at = "11:00 am"
        #book_duration = 30

        restaurant_allocations = reserv.reservation(book_on, book_at, book_duration)
        if restaurant_allocations:
            print("There are allocation restaurant: {}".format(restaurant_allocations))
        else:
            print("No available restaurant for booking")
    except ValueError:
        print("Invalid input.")
