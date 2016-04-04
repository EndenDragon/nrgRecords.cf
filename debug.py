import csv
import os


with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "csv/nrgAttendance.csv") as csvfile:
    cr = csv.DictReader(csvfile)
    for row in cr:
        print row