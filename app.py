from flask import Flask, render_template, make_response, request, redirect, url_for, flash, send_file, session, escape
import sqlite3 as sql
import math

app = Flask(__name__)

conn = sql.connect('Genesis.db')
conn.row_factory = sql.Row
cur = conn.cursor()
cur.execute("SELECT * FROM jobs")
jobsPerPage = 6
jobListings = len(cur.fetchall())
pages = math.ceil(jobListings / jobsPerPage)

cur.execute("UPDATE accounts SET loggedIn = 0")
conn.commit()

cur.execute("UPDATE jobs SET score = 0")
conn.commit()

currentUser = None

userKeywords = []

app.secret_key = 'ColesSuperSecretKey'
@app.route('/', methods=['GET','POST'])
def hello_world():  # put application's code here
    global jobListings

    if request.form.get('jobpage') is not None:
        page =int(request.form.get('jobpage'))
    else:
        page = 1

    if request.form.get('job') is not None:
        target = int(request.form.get('job'))
        conn = sql.connect('Genesis.db')
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute('''SELECT * FROM scored_jobs where row_id = ?''', [target])
        rows = cur.fetchall()
        return render_template("jobpage.html", rows = rows)


    conn = sql.connect('Genesis.db')
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("SELECT loggedIn FROM accounts WHERE loggedIn = 1")
    status = cur.fetchone()
    if status:
        cur.execute("SELECT username FROM accounts WHERE loggedIn = 1")
        currentUser = str(cur.fetchone()[0])
    else:
        return redirect(url_for('login'))

    cur.execute("SELECT row_id, keywords FROM jobs")
    keywords = {}

    for i in range(0, jobListings):
        try:
            next = cur.fetchone()
            keywords[next[0]] = next[1]
        except:
            pass

    score = 0

    matches = []
    matchstring = ""

    for i in keywords:
        if keywords[i] is not None:
            morekeywords = keywords[i].split(",")
            for word in morekeywords:
                for userword in userKeywords:
                    if word == userword:
                        matches.append(word)
                        score += 1
            if score != 0:
                keywords[i] = score
            else:
                keywords[i] = 0

            matchString = ""

            for match in matches:
                matchString += match + ","
            if len(matchString) > 1:
                matchString = list(matchString)
                matchString[len(matchString)-1] = ""
                matchString = "".join(matchString)
            print(matchString)

            cur.execute("UPDATE jobs SET score = ?, matches = ? WHERE row_id = ?", [score, matchString, i])
            conn.commit()
            score = 0
            matches = []

    cur.execute('''DROP TABLE IF EXISTS scored_jobs''')

    cur.execute('''CREATE TABLE IF NOT EXISTS "scored_jobs" (
                "row_id"	integer,
                "title"	text,
                "description"	text,
                "short_description"	text,
                "job_type"	text,
                "salary"	text,
                "location"	text,
                "fp_time"	text,
                "por"	text,
                "benefits"	text,
                "qualifications"	text,
                "keywords"	TEXT,
                "score"	INTEGER,
                "matches"	TEXT,
                PRIMARY KEY("row_id" AUTOINCREMENT)
                )''')

    conn.commit()

    cur.execute('''INSERT INTO "scored_jobs" (
                "title",
                "description",
                "short_description",
                "job_type",
                "salary",
                "location",
                "fp_time",
                "por",
                "benefits",
                "qualifications",
                "keywords",
                "score",
                "matches")  SELECT 
                "title",
                "description",
                "short_description",
                "job_type",
                "salary",
                "location",
                "fp_time",
                "por",
                "benefits",
                "qualifications",
                "keywords",
                "score",
                "matches" FROM jobs ORDER BY score DESC''')

    conn.commit()

    searchString = ""

    if request.form.get('search'):
        searchString = str(request.form.get('search'))
        print(searchString)
    rows = None

    if searchString != "":
        cur.execute("SELECT * FROM scored_jobs WHERE title LIKE ? limit ? OFFSET ?", ["%"+searchString+"%", jobsPerPage, (page - 1) * jobsPerPage])
        rows = cur.fetchall()
        listings = len(rows)
    else:
        cur.execute("SELECT * FROM scored_jobs limit ? OFFSET ?", [jobsPerPage,(page-1)*jobsPerPage])
        listings = jobListings
        rows = cur.fetchall()


    pages = math.ceil(listings / jobsPerPage)

    return render_template('firstpage.html', rows=rows, jobpage=page, pages=pages, username=currentUser)


# LOGIN, SIGNUP, LOGOUT, PROFILE, DASHBOARD, SETTINGS, HELP, PORTFOLIO, HOME PAGE

@app.route("/signup", methods=["POST", "GET"])
def signup():
    conn = sql.connect('Genesis.db')
    cur = conn.cursor()
    username = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT * FROM accounts WHERE username = ?", [username])
        users = cur.fetchall()
        if len(users) != 0:
            flash("This user already exists!")
        else:
            cur.execute("INSERT INTO accounts(username,password) VALUES(?, ?)", [username,password])
            conn.commit()
            return render_template('questions.html', username=username)
    return render_template('signup.html')

@app.route("/createaccount", methods=["POST", "GET"])
def createaccount():
    global userKeywords
    conn = sql.connect('Genesis.db')
    cur = conn.cursor()
    keywords = ""
    if request.method == 'POST':
        if request.form.get('code'):
            keywords += "Coding,"
        if request.form.get('python'):
            keywords += "Python,"
        if request.form.get('java'):
            keywords += "Java,"
        if request.form.get('cpp'):
            keywords += "C++,"
        if request.form.get('c'):
            keywords += "C,"
        if request.form.get('trucking'):
            keywords += "Truck Driving,"
        if request.form.get('manager'):
            keywords += "Managing,"
        if request.form.get('teach'):
            keywords += "Teaching,"
        if request.form.get('cook'):
            keywords += "Cooking,"
        if request.form.get('IT'):
            keywords += "IT,"
        if request.form.get('support'):
            keywords += "Support,"
        if request.form.get('delivery'):
            keywords += "Delivery,"
        if request.form.get('part-time'):
            keywords += "Part-Time,"
        if request.form.get('ft'):
            keywords += "Full-Time,"

        if len(keywords) > 1:
            keywords = list(keywords)
            keywords[len(keywords) - 1] = ""
            keywords = "".join(keywords)
        username = str(request.form.get('username'))
        print(username)
        cur.execute("UPDATE accounts SET skills = ?, loggedIn = 1 WHERE username = ?", [keywords, username])
        conn.commit()
        userKeywords = keywords.split(",")
        return redirect(url_for('hello_world', username=username))
    return render_template('questions.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    global userKeywords
    conn = sql.connect('Genesis.db')
    cur = conn.cursor()
    if request.method == 'POST':
        username = request.form['Uname']
        password = request.form['Pass']
        cur.execute("SELECT 1 FROM accounts WHERE username = ? AND password = ?", [username,password])
        users = cur.fetchall()
        print("row count is:", len(users))
        if len(users) == 0:
            flash("Invalid username or password")

            return render_template('login.html')
        else:
            cur.execute("SELECT loggedIn FROM accounts WHERE username = ?", [username])
            status = int(cur.fetchone()[0])
            if status == 1:
                flash("This user is already logged in!")
                return render_template('login.html')
            elif status == 0:
                cur.execute("UPDATE accounts SET loggedIn = 1 WHERE username = ?", [username])
                conn.commit()
                currentUser = username
                cur.execute("SELECT skills FROM accounts WHERE username = ?", [username])
                userKeywords = []
                try:
                    userKeywords = str(cur.fetchone()[0]).split(",")
                except:
                    pass
                print(userKeywords)
                return redirect(url_for('hello_world'))
            else:
                flash("Error! Please contact system admin!")
                return render_template('login.html')
    return render_template('login.html')

@app.route("/logout")
def logout():
    conn = sql.connect('Genesis.db')
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET loggedIn = 0")
    conn.commit()
    return redirect(url_for('login'))

