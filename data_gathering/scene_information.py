"""
Module which handles information extraction from the scene's name by Landsat 8 naming convention.
"""
import calendar


class SceneInformation:
    """
    Class which extracts information from a scene's name.
    """

    def __init__(self, scene):
        """
        Initializes the scene object which represents the name of a scene.
        :param scene: Name of a Landsat 8 scene.
        """
        self.scene = scene

    def get_year(self) -> int:
        """
        Returns the year of the scene based on the character location.
        :return: int
        """
        year = int(self.scene[9:13])

        return year

    def get_days(self) -> int:
        """
        Returns the number of days passed from the start of the year till the capturing of the scene.
        :return: int
        """
        days = int(self.scene[13:16])

        return days

    def get_month(self) -> int:
        """
        Returns the month in which the scene was taken, based on the total of days passed from the start of the year.
        :return: int
        """
        year = self.get_year()
        days = self.get_days()
        total_days = 0
        month = 0

        while total_days < days and month <= 12:
            month += 1
            days_in_month = calendar.monthrange(year, month)[1]
            total_days += days_in_month

        return month

    def get_day(self) -> int:
        """
        Returns the day of the month in which the scene was taken, based on the total days passed from the start of the
        year.
        :return: int
        """
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

    def get_satellite(self) -> str:
        """
        Returns the initials of the satellite which took the scene. The satellite should be L from Landsat.
        :return: str
        """
        satellite = self.scene[0:1]

        return satellite

    def get_satellite_number(self) -> str:
        """
        Returns the satellite number, which should be 8.
        :return: str
        """
        number = self.scene[2:3]

        return number

    def get_path(self) -> str:
        """
        Returns the path of the Landsat 8  scene.
        :return:
        """
        path = self.scene[3:6]
        return path

    def get_row(self) -> str:
        """
        Returns the row of the Landsat 8  scene.
        :return: int
        """

        row = self.scene[6:9]
        return row
