import matplotlib.pyplot as plt
import pandas as pd


class CSVReader:
    def __init__(self, csv):
        self.csv = csv

    def read_csv(self):
        d = pd.read_csv(self.csv)
        year = d['RESULT']
        sea_levels = d['CSIRO_SEALEVEL_INCHES']
        plt.scatter(year, sea_levels, edgecolors='r')
        plt.xlabel('Year')
        plt.ylabel('Sea Level (inches)')
        plt.title('Rise in Sealevel')
        plt.show()


if __name__ == "__main__":
    girls_grades = [89, 90, 70, 89, 100, 80, 90, 100, 80, 34]
    boys_grades = [30, 29, 49, 48, 100, 48, 38, 45, 20, 30]
    grades_range = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    plt.scatter(grades_range, girls_grades, color='r')
    plt.scatter(grades_range, boys_grades, color='g')
    plt.xlabel('Grades Range')
    plt.ylabel('Grades Scored')
    plt.show()