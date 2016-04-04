# nrgRecords.cf

**By Jeremy Zhang - [http://nrgRecords.cf](http://nrgRecords.cf/)**

Newport Robotics Group (NRG948) Records Site

The site's purpose is to quickly look up one's attendance and outreach hours.

Make any changes/fixes that are needed and submit a pull-request! Thank you for your contribution! :)

## Pip Packages Dependancies

**These are required packages (pip install) in order for the site to run smoothly**
* Flask
* flask_oauth
* xlrd

## Files

**Significant files and their purpose**

* main.py - The main python file.
* /static/ - CSS, javascripts, and more!
* /templates/ - HTML files used for rendering the site
* /csv/ - Folder to store nrgAttendance.csv and nrgOutreach.csv
* /panelContent/ - Where content for the panels are located and used by the program
* admins.txt - Seperated by line breaks, this file contains email addresses for logging into the admin panel
* config.json - Configuration file for ip, port, debug state, google client id, google client secret

## URL Format

Url format example: `http://nrgrecords.cf/record?fn=Jeremy&ln=Zhang`

* First Name (fn): Jeremy
* Last Name (ln): Zhang

## Thanks

Thank you Mr. Quick for kindly providing me Media Team's photos for the website's background.
