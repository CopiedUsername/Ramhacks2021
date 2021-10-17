import sqlite3

conn = sqlite3.connect('Genesis.db')

cur = conn.cursor()

cur.execute('''CREATE TABLE "jobs" (
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

cur.execute("INSERT OR IGNORE INTO jobs(title, short_description, job_type,salary, location) VALUES ('Software Developer', 'Example of a short desc', 'Full-Time', '60k/year', 'remote'), ('Data Architect', 'Another short desc', 'Part-time', '120k/year', 'Austin, TX') ")
conn.commit()


cur.execute('''CREATE TABLE "accounts" (
	"account_id"	integer,
	"username"	text,
	"password"	text,
	"skills"	TEXT,
	"loggedIn"	INTEGER,
	PRIMARY KEY("account_id" AUTOINCREMENT)

                )''')
conn.commit()

cur.execute("INSERT OR IGNORE INTO accounts (username, password) VALUES('bohanonc', 'ramhacks'), ('larkinb', 'donut')")
conn.commit()
