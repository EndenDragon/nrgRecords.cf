# nrgRecords.cf

**By Jeremy Zhang - [http://nrgRecords.cf](http://nrgRecords.cf/)**

Newport Robotics Group (NRG948) Records Site

The site's purpose is to quickly look up one's attendance and outreach hours. Built onto the Flask microframework above python, it provides a great base to create a simple website. The deployed server is located on [PythonAnywhere](http://pythonanywhere.com/) using two web workers to speed up the content delivery.

Make any changes/fixes that are needed and submit a pull-request! Thank you for your contribution! :)

## Pip Packages Dependancies

**These are required packages (pip install) in order for the site to run smoothly**
* Flask
* flask_oauth
* xlrd
* flask-compress

## Files

**Significant files and their purpose**

* main.py - The main python file.
* /static/ - CSS, javascripts, and more!
* /templates/ - HTML files used for rendering the site
* /csv/ - Folder to store nrgAttendance.csv and nrgOutreach.csv
* /panelContent/ - Where content for the panels are located and used by the program
* admins.txt - Seperated by line breaks, this file contains email addresses for logging into the admin panel
* config.json - Configuration file for ip, port, debug state, google client id, google client secret
* globalHeaderMSG.json - The global header JSON file stores the message to be displayed globally. It also saves the state (enabled/disabled) and category (color effect) of the global header.

## Running the development server

To run the website in development mode, edit the ip, port and set debug to true in config.json (create a file & copy the contents from config copy.json). Setting debug to true means when you save the file, it automatically compiles and render the code on the server. During a crash, it also shows the stack trace and use the browser console. To be able to access the admin panel, you also need to provide the Google's Client ID & Secret from [https://console.developers.google.com](https://console.developers.google.com) and add your gmail email address into admins.txt file (create a file & copy the contents from admins copy.json). Also, copy the globalHeaderMSG copy.json file contents and create a file called globalHeaderMSG.json with the contents in clipboard. Once everything is properly configured, you may open up the shell and cd into the nrgRecords.cf folder. Then run `python main.py`. If everything is properly working and no errors to be found, point your browser to the address on the console and view the development site.

## URL Format

Url format example: `http://nrgrecords.cf/record?fn=Jeremy&ln=Zhang`

* First Name (fn): Jeremy
* Last Name (ln): Zhang

## Thanks

Thank you Mr. Quick for kindly providing me Media Team's photos for the website's background.
