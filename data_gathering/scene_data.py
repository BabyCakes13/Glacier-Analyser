import calendar


class SceneData:
    def __init__(self, scene):
        self.scene = scene

    def get_year(self) -> int:
        """Returns the year of the scene."""
        year = int(self.scene[9:13])
        return year

    def get_days(self):
        """Returns the number of days passed from the start of the year till the capturing of the scene."""
        days = int(self.scene[13:16])
        return days

    def get_month(self):
        """Returns the month of the scene."""
        year = self.get_year()
        days = self.get_days()
        total_days = 0
        month = 0

        while total_days < days and month <= 12:
            month += 1
            days_in_month = calendar.monthrange(year, month)[1]
            total_days += days_in_month

        return month

    def get_day(self):
        """Returns the day of the scene."""
        year = self.get_year()
        days = self.get_days()
        total_days = 0
        month = 0
        day = 0

        while total_days < days and month <= 12:
            month += 1
            days_in_month = calendar.monthrange(year, month)[1]
            day = days - total_days
            total_days += days_in_month

        return day

    def get_satellite(self):
        """Returns the satellite of the scene."""
        satellite = self.scene[0:1]
        return satellite

    def get_satellite_number(self):
        """Returns the number of the satellite."""
        number = int(self.scene[2:3])
        return number

    def get_path(self):
        path = int(self.scene[3:6])
        return path

    def get_row(self):
        row = int(self.scene[6:9])
        return row