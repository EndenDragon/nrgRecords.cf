import xlrd
import csv
import os

def file_get_contents(filename):
    with open(os.path.dirname(os.path.realpath(__file__)) + "/" + filename) as f:
        return f.read()

def csv_from_excel():
    wb = xlrd.open_workbook(os.path.dirname(os.path.realpath(__file__)) + "/" + 'Attendance-Master.xlsx')
    sh = wb.sheet_by_name('Main')
    your_csv_file = open('your_csv_file.csv', 'wb')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
    for rownum in xrange(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()
    
csv_from_excel()