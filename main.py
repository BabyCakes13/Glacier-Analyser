#! /usr/bin/python3

"""Main caller of the application."""
from data_gathering import download

# works
# csvhandler = download.CSVHandler(0, 20)
# csvhandler.open_csv()

# BUG crashes at line 839, position 2201
# (UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf1 in position 2201: invalid continuation byte)
csvhandler = download.CSVHandler()
csvhandler.open_csv()
