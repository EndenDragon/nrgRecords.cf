from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug import secure_filename
from flask_oauth import OAuth
import os
import random
import csv
import json
import xlrd
import time
import re
from shutil import move
app = Flask(__name__)

html_escape_table = {
    "&": "&amp;",
    '"': "\"",
    "'": "\\'",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

def file_get_contents(filename):
    with open(os.path.dirname(os.path.realpath(__file__)) + "/" + filename) as f:
        return f.read()

def randBG():
    filepath = os.path.dirname(os.path.realpath(__file__))
    files = [os.path.join(path, filename)
             for path, dirs, files in os.walk(filepath + "/static/portfolio/")
             for filename in files
             if not filename.endswith(".bak")]
    return random.choice(files)[len(filepath)+1:]

def remove_extra_spaces(data):
    p = re.compile(r'\s+')
    return p.sub(' ', data)

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return remove_extra_spaces(p.sub('', data))

def getAttendancePanelContent():
    return file_get_contents("panelContent/attendancePanel.txt")

def getOutreachPanelContent():
    return file_get_contents("panelContent/outreachPanel.txt")

def convertDate(inDate):
    if inDate == "Design Day 1" or inDate == "Design Day 2" or inDate == "Kickoff":
        if inDate == "Design Day 1":
            return '2016-01-09'
        if inDate == "Kickoff":
            return '2016-01-09'
        if inDate == "Design Day 2":
            return '2016-01-10'
    else:
        month = inDate[:inDate.find("/")]
        day = inDate[inDate.find("/") + 1:inDate.find("/",inDate.find("/") + 1)]
        year = inDate[inDate.find("/",inDate.find("/") + 1) + 1:]
        if len(month) == 1:
            month = str(0) + month
        if len(day) == 1:
            day = str(0) + day
        return str(year) + "-" + str(month) + "-" + str(day)

def getFN():
    fnList = []
    with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "csv/nrgAttendance.csv") as csvfile:
        cr = csv.DictReader(csvfile)
        for row in cr:
            if fnList.count(row['First Name'].strip()) == 0:
                fnList.append(row['First Name'].strip())
    with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "csv/nrgOutreach.csv") as csvfile:
        cr = csv.DictReader(csvfile)
        for row in cr:
            if fnList.count(row['First Name'].strip()) == 0:
                fnList.append(row['First Name'].strip())
    return fnList

def getLN():
    lnList = []
    with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "csv/nrgAttendance.csv") as csvfile:
        cr = csv.DictReader(csvfile)
        for row in cr:
            if lnList.count(row['Last Name'].strip()) == 0:
                lnList.append(row['Last Name'].strip())
    with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "csv/nrgOutreach.csv") as csvfile:
        cr = csv.DictReader(csvfile)
        for row in cr:
            if lnList.count(row['Last Name'].strip()) == 0:
                lnList.append(row['Last Name'].strip())
    return lnList

def jsonifyFN():
    fnList = getFN()
    JSON = "["
    for x in fnList:
        JSON = JSON + '''{"label":"''' + html_escape(x) + '''"},'''
    JSON = JSON[:len(JSON) - 1] + ']'
    return JSON

def jsonifyLN():
    lnList = getLN()
    JSON = "["
    for x in lnList:
        JSON = JSON + '''{"label":"''' + html_escape(x) + '''"},'''
    JSON = JSON[:len(JSON) - 1] + ']'
    return JSON

@app.route("/")
def index():
    try:
        oldRef = remove_html_tags(request.args.get('oldRef', None))
    except:
        oldRef = None
    if not oldRef == None:
        flash(u'''It appears that you have been redirected from our old domain (''' + oldRef + '''). Please update your bookmarks to the new domain (<a href="http://nrgRecords.cf/">http://nrgRecords.cf/</a>). Thanks!''', 'warning')
    flashcfg = file_get_contents("globalHeaderMSG.json")
    flashcfg = json.loads(flashcfg)
    if flashcfg['enabled']:
        flash(flashcfg['message'], flashcfg['category'])
    return render_template("header.html", randBackground=randBG()) + render_template("panel_empty.html") + render_template("reminderPanel.html", attendancePanelContent=getAttendancePanelContent(), outreachPanelContent=getOutreachPanelContent()) + render_template("endScripts.html") + render_template("footer.html", fnTypeaheadJSON=jsonifyFN(), lnTypeaheadJSON=jsonifyLN())

@app.route("/record")
def record():
    flashcfg = file_get_contents("globalHeaderMSG.json")
    flashcfg = json.loads(flashcfg)
    if flashcfg['enabled']:
        flash(flashcfg['message'], flashcfg['category'])

    fn = request.args.get('fn', 'null')
    ln = request.args.get('ln', 'null')
    #0 = Both Attendance & Outreach works
    #1 = Both fails
    #2 = Attendance fails, not outreach
    #3 = Outreach fails, not attendance
    error = 0

    if (fn.lower().title() in getFN() and ln.lower().title() in getLN()):
        try:
            with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "csv/nrgAttendance.csv") as csvfile:
                cr = csv.DictReader(csvfile)
                for row in cr:
                    if row['First Name'].replace(" ", "").lower() == fn.replace(" ", "").lower() and row['Last Name'].replace(" ", "").lower() == ln.replace(" ", "").lower():
                        dictionary = row
                        del dictionary['First Name']
                        del dictionary['Last Name']
                dateCount = 0
                attendedCount = 0
                for x in dictionary:
                    dateCount = dateCount + 1
                    if dictionary[x].lower() == "x":
                        attendedCount = attendedCount + 1
                attnPercentage = (float(attendedCount) / dateCount) * 100
                attendanceDictionary = {}
                for key in dictionary:
                    convertedKey = convertDate(key)
                    if convertedKey not in attendanceDictionary:
                        attendanceDictionary[convertedKey] = 0
                        if dictionary[key] == "x":
                            attendanceDictionary[convertedKey] = attendanceDictionary[convertedKey] + 1
                    else:
                        if dictionary[key] == "x":
                            attendanceDictionary[convertedKey] = attendanceDictionary[convertedKey] + 1
                attendanceJSON = "{"
                for key in attendanceDictionary:
                    if attendanceDictionary[key] == 0:
                        attendanceJSON = attendanceJSON + '"' + key + '''":{},'''
                    else:
                        attendanceJSON = attendanceJSON + '"' + key + '''":{"number": ''' + str(attendanceDictionary[key]) + '},'
                attendanceJSON = attendanceJSON[:len(attendanceJSON) - 1] + '}'
        except:
            error = 2

        try:
            with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "csv/nrgOutreach.csv") as csvfile:
                cr = csv.DictReader(csvfile)
                for row in cr:
                    if row['First Name'].replace(" ", "").lower() == fn.replace(" ", "").lower() and row['Last Name'].replace(" ", "").lower() == ln.replace(" ", "").lower():
                        odictionary = row
                        del odictionary['First Name']
                        del odictionary['Last Name']
                outreachStr = ""
                totalHrs = 0
                for x in odictionary:
                    if odictionary[x] == "":
                        odictionary[x] = 0
                    outreachStr = outreachStr + x + ": "
                    outreachStr = outreachStr + str(odictionary[x])
                    totalHrs = totalHrs + float(odictionary[x])
                    outreachStr = outreachStr + "</br>"
                outreachStr = outreachStr + '''<hr><h4 style="color: black;"><strong>Total hours participated in outreach: ''' + str(totalHrs) + "</strong></h4>"
        except:
            if error == 2:
                error = 1
            else:
                error = 3

        if error == 0:
            return render_template("header.html", randBackground=randBG()) + render_template("panel_content.html", firstName=fn, lastName=ln, attnPercentage=attnPercentage, outreachData=outreachStr) + render_template("reminderPanel.html", attendancePanelContent=getAttendancePanelContent(), outreachPanelContent=getOutreachPanelContent()) + render_template("endScripts.html") + render_template("calendarData.html", calendarJSON=attendanceJSON) + render_template("footer.html", fnTypeaheadJSON=jsonifyFN(), lnTypeaheadJSON=jsonifyLN())
        elif error == 1:
            return render_template("header.html", randBackground=randBG()) + render_template("panel_bothMissing.html", firstName=fn, lastName=ln) + render_template("reminderPanel.html", attendancePanelContent=getAttendancePanelContent(), outreachPanelContent=getOutreachPanelContent()) + render_template("endScripts.html") + render_template("footer.html", fnTypeaheadJSON=jsonifyFN(), lnTypeaheadJSON=jsonifyLN())
        elif error == 2:
            return render_template("header.html", randBackground=randBG()) + render_template("panel_attendanceMissing.html", firstName=fn, lastName=ln, outreachData=outreachStr) + render_template("reminderPanel.html", attendancePanelContent=getAttendancePanelContent(), outreachPanelContent=getOutreachPanelContent()) + render_template("endScripts.html") + render_template("footer.html", fnTypeaheadJSON=jsonifyFN(), lnTypeaheadJSON=jsonifyLN())
        elif error == 3:
            return render_template("header.html", randBackground=randBG()) + render_template("panel_outreachMissing.html", firstName=fn, lastName=ln, attnPercentage=attnPercentage) + render_template("reminderPanel.html", attendancePanelContent=getAttendancePanelContent(), outreachPanelContent=getOutreachPanelContent()) + render_template("endScripts.html") + render_template("calendarData.html", calendarJSON=attendanceJSON) + render_template("footer.html", fnTypeaheadJSON=jsonifyFN(), lnTypeaheadJSON=jsonifyLN())
        else:
            return render_template("header.html", randBackground=randBG()) + render_template("panel_bothMissing.html", firstName=fn, lastName=ln) + render_template("reminderPanel.html", attendancePanelContent=getAttendancePanelContent(), outreachPanelContent=getOutreachPanelContent()) + render_template("endScripts.html") + render_template("footer.html", fnTypeaheadJSON=jsonifyFN(), lnTypeaheadJSON=jsonifyLN())
    else:
        return render_template("header.html", randBackground=randBG()) + render_template("panel_bothMissing.html", firstName=fn, lastName=ln) + render_template("reminderPanel.html", attendancePanelContent=getAttendancePanelContent(), outreachPanelContent=getOutreachPanelContent()) + render_template("endScripts.html") + render_template("footer.html", fnTypeaheadJSON=jsonifyFN(), lnTypeaheadJSON=jsonifyLN())
    return render_template("header.html", randBackground=randBG()) + render_template("panel_bothMissing.html", firstName=fn, lastName=ln) + render_template("reminderPanel.html", attendancePanelContent=getAttendancePanelContent(), outreachPanelContent=getOutreachPanelContent()) + render_template("endScripts.html") + render_template("footer.html", fnTypeaheadJSON=jsonifyFN(), lnTypeaheadJSON=jsonifyLN())

### DOWNLOAD CSVS ###
@app.route('/csv/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)

### OUTPUT LOG ###
@app.route('/log')
def log():
    app_config = file_get_contents("config.json")
    app_config = json.loads(app_config)
    try:
        return render_template("logViewer.html", contents=file_get_contents(app_config['log']))
    except:
        return "Sorry, Log file cannot be found"

### ADMIN PANEL ###
UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/" + "csv"
ALLOWED_EXTENSIONS = set(['csv', 'xlsx', 'xls'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app_config = file_get_contents("config.json")
app_config = json.loads(app_config)
GOOGLE_CLIENT_ID = app_config["gClientID"]
GOOGLE_CLIENT_SECRET = app_config["gClientSecret"]
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console
SECRET_KEY = 'development key'
app.secret_key = SECRET_KEY
oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)
def loggedInCheck():
    access_token = session.get('access_token')
    if access_token is None:
        return False

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return False
    loginStr = res.read()
    loginStr = json.loads(loginStr)
    with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "admins.txt") as f:
        adminEmails = f.read().splitlines()
    if loginStr['email'] in adminEmails:
        return True
    else:
        return False

def getAdminEmail():
    access_token = session.get('access_token')
    if access_token is None:
        return "null"

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return "null"
    loginStr = res.read()
    loginStr = json.loads(loginStr)
    with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "admins.txt") as f:
        adminEmails = f.read().splitlines()
    if loginStr['email'] in adminEmails:
        return str(loginStr['email'])
    else:
        return "null"

@app.route('/admin')
def admin():
    loggedIn = loggedInCheck()
    if loggedIn:
        return render_template("adminPanel.html", adminEmail=getAdminEmail())
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template("adminLogin.html")

@app.route('/login-process')
def login_process():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect(url_for('admin'))

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('admin'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def excel2csvAttendance(fileName):
    wb = xlrd.open_workbook(os.path.dirname(os.path.realpath(__file__)) + "/csv/" + fileName)
    sh = wb.sheet_by_name('Main')
    your_csv_file = open('csv/nrgAttendance.csv', 'wb')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
    for rownum in xrange(sh.nrows):
        wr.writerow(sh.row_values(rownum))
    your_csv_file.close()

@app.route('/uploadAttendance', methods=['GET', 'POST'])
def uploadAttendance():
    loggedIn = loggedInCheck()
    if loggedIn:
        if request.method == 'POST':
            afile = request.files['file']
            if afile and allowed_file(afile.filename):
                filename = secure_filename(afile.filename)
                afile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if filename[len(filename)-3:] == "csv":
                    move(os.path.dirname(os.path.realpath(__file__)) + "/csv/" + filename, os.path.dirname(os.path.realpath(__file__)) + "/csv/nrgAttendance.csv")
                    flash(u'Successfully uploaded a CSV file!', 'success')
                else:
                    try:
                        os.remove(os.path.dirname(os.path.realpath(__file__)) + "/csv/" + "nrgAttendance.csv")
                    except:
                        pass
                    excel2csvAttendance(filename)
                    os.remove(os.path.dirname(os.path.realpath(__file__)) + "/csv/" + filename)
                    flash(u'Successfully uploaded a Microsoft Excel file!', 'success')
            else:
                flash(u'Only .csv, .xls, and .xlsx are accepted!', 'danger')
        return render_template('uploadAttendance.html', adminEmail=str(getAdminEmail()))
    else:
        return redirect(url_for('logout'))

def excel2csvOutreach(fileName):
    wb = xlrd.open_workbook(os.path.dirname(os.path.realpath(__file__)) + "/csv/" + fileName)
    sh = wb.sheet_by_name('Sheet1')
    your_csv_file = open('csv/nrgOutreach.csv', 'wb')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
    for rownum in xrange(sh.nrows):
        wr.writerow(sh.row_values(rownum))
    your_csv_file.close()

@app.route('/uploadOutreach', methods=['GET', 'POST'])
def uploadOutreach():
    loggedIn = loggedInCheck()
    if loggedIn:
        if request.method == 'POST':
            afile = request.files['file']
            if afile and allowed_file(afile.filename):
                filename = secure_filename(afile.filename)
                afile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if filename[len(filename)-3:] == "csv":
                    move(os.path.dirname(os.path.realpath(__file__)) + "/csv/" + filename, os.path.dirname(os.path.realpath(__file__)) + "/csv/nrgOutreach.csv")
                    flash(u'Successfully uploaded a CSV file!', 'success')
                else:
                    try:
                        os.remove(os.path.dirname(os.path.realpath(__file__)) + "/csv/" + "nrgOutreach.csv")
                    except:
                        pass
                    excel2csvOutreach(filename)
                    os.remove(os.path.dirname(os.path.realpath(__file__)) + "/csv/" + filename)
                    flash(u'Successfully uploaded a Microsoft Excel file!', 'success')
            else:
                flash(u'Only .csv, .xls, and .xlsx are accepted!', 'danger')
        return render_template('uploadOutreach.html', adminEmail=getAdminEmail())
    else:
        return redirect(url_for('logout'))

@app.route('/editAttendancePanel', methods=['GET','POST'])
def editAttendancePanel():
    loggedIn = loggedInCheck()
    if loggedIn:
        if request.method == 'POST':
            boxContent = request.form['textContent']
            fo = open(os.path.dirname(os.path.realpath(__file__)) + "/" + "panelContent/attendancePanel.txt", "wb")
            fo.write(boxContent);
            flash(u'Successfully updated attendance panel!', 'success')
            return redirect(url_for('editAttendancePanel'))
        return render_template("editAttendancePanel.html", adminEmail=getAdminEmail(), prefilledContent=file_get_contents("panelContent/attendancePanel.txt"))
    else:
        return redirect(url_for('logout'))

@app.route('/editOutreachPanel', methods=['GET','POST'])
def editOutreachPanel():
    loggedIn = loggedInCheck()
    if loggedIn:
        if request.method == 'POST':
            boxContent = request.form['textContent']
            fo = open(os.path.dirname(os.path.realpath(__file__)) + "/" + "panelContent/outreachPanel.txt", "wb")
            fo.write(boxContent);
            flash(u'Successfully updated outreach panel!', 'success')
            return redirect(url_for('editOutreachPanel'))
        return render_template("editOutreachPanel.html", adminEmail=getAdminEmail(), prefilledContent=file_get_contents("panelContent/outreachPanel.txt"))
    else:
        return redirect(url_for('logout'))

@app.route('/editAdmins', methods=['GET','POST'])
def editAdmins():
    loggedIn = loggedInCheck()
    if loggedIn:
        if request.method == 'POST':
            boxContent = request.form['textContent']
            fo = open(os.path.dirname(os.path.realpath(__file__)) + "/" + "admins.txt", "wb")
            fo.write(boxContent);
            flash(u'Successfully updated admins list!', 'success')
            return redirect(url_for('editAdmins'))
        return render_template("editAdmins.html", adminEmail=getAdminEmail(), prefilledContent=file_get_contents("admins.txt"))
    else:
        return redirect(url_for('logout'))

@app.route('/editGlobalMSG', methods=['GET','POST'])
def editGlobalMSG():
    loggedIn = loggedInCheck()
    if loggedIn:
        if request.method == 'POST':
            fstate = request.form['enabled'] == 'True'
            fcategory = request.form['category']
            fmessage = request.form['message']
            with open(os.path.dirname(os.path.realpath(__file__)) + "/" + "globalHeaderMSG.json", 'r+') as f:
                json_data = json.load(f)
                json_data['enabled'] = fstate
                json_data['category'] = fcategory
                json_data['message'] = fmessage
                f.seek(0)
                f.write(json.dumps(json_data))
                f.truncate()
            flash(u'Successfully updated global header message!', 'success')
            return redirect(url_for('editGlobalMSG'))
        globalMSGDef = file_get_contents("globalHeaderMSG.json")
        globalMSGDef = json.loads(globalMSGDef)
        return render_template("editGlobalMSG.html", adminEmail=getAdminEmail(), fstate=globalMSGDef['enabled'], fcategory=globalMSGDef['category'], fmessage=globalMSGDef['message'])
    else:
        return redirect(url_for('logout'))

if __name__ == "__main__":
    app_config = file_get_contents("config.json")
    app_config = json.loads(app_config)
    app.run(host=str(app_config["ip"]),port=int(float(str(app_config["port"]))),debug=app_config["debug"] in ["True","true"])
