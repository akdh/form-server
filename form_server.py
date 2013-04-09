from flask import *
import sqlite3
import csv
import json
from jinja2 import Template
import argparse
from random import choice
import uuid

index_template = """<!DOCTYPE html>
<html>
<head>
	<meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
	<style>
		.notice {
			border: 1px solid #fcefa1;
			background: #fbf9ee;
			color: #363636;
			padding: 0.5em 1em;
		}
	</style>
</head>
<body>
{% for notice in get_flashed_messages() %}
<div class="notice">{{ notice }}</div>
{% endfor %}
<ul>
{% for attraction in attractions %}
	<li><a href="{{ attraction["url"] }}">{{ attraction["id"] }}</a></li>
{% endfor %}
</ul>
</body>
</html>
"""

app = Flask(__name__)

def next_id(db, username):
	all_keys = db.execute("SELECT key FROM input").fetchall()
	answered_keys = db.execute("SELECT key FROM results WHERE author = ?", (username,)).fetchall()
	all_keys = map(lambda row: row[0], all_keys)
	answered_keys = map(lambda row: row[0], answered_keys)
	unanswered_keys = filter(lambda key: not key in answered_keys, all_keys)
	if len(unanswered_keys) == 0:
		return None
	return choice(unanswered_keys)

@app.before_request
def before_request():
	g.db = sqlite3.connect(app.config['DB_NAME'])

@app.teardown_request
def teardown_request(exception):
	if hasattr(g, "db"):
		g.db.close()

@app.route("/<username>")
def index(username):
	rows = g.db.execute("SELECT key FROM input").fetchall()
	urls = map(lambda row: {"url": url_for('item', username=username, id=row[0]), "id": row[0]}, rows)
	return render_template_string(index_template, attractions=urls)

@app.route("/<username>/<id>", methods=["GET", "POST"])
def item(username, id):
	row = g.db.execute("SELECT value FROM input WHERE key = ?", (id,)).fetchone()

	if request.method == "POST":
		count = g.db.execute("SELECT COUNT(*) FROM results WHERE key = ?", (id,)).fetchone()[0]
		d = request.form.to_dict()
		d["username"] = username
		d.update(json.loads(row[0]))
		if count == 0:
			g.db.execute("INSERT INTO results (key, value, author) VALUES (?, ?, ?)", (id, json.dumps(d), username))
		else:
			g.db.execute("UPDATE results SET value = ? WHERE key = ? AND author = ?", (json.dumps(d), id, username))
		g.db.commit()
		id = next_id(g.db, username)
		if id is None:
			flash("No more questions.")
			return redirect(url_for('index', username=username))
		return redirect(url_for('item', username=username, id=id))

	value = json.loads(row[0])
	row = g.db.execute("SELECT value FROM results WHERE key = ? LIMIT 1", (id,)).fetchone()
	if not row is None:
		value.update(json.loads(row[0]))

	return render_template_string(app.config['HTML'], **value)

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help="command", dest="command")

results_subparser = subparsers.add_parser("results", help="get results")
results_subparser.add_argument("csv", action="store")

results_subparser = subparsers.add_parser("run", help="run the server")
results_subparser.add_argument("html", action="store")

parser.add_argument("--input", action="store", help="input questions into DB")
parser.add_argument("--db", action="store", default="db.sqlite", help="location of sqlite DB file (default: db.sqlite)")

args = parser.parse_args()

if not args.input is None:
	db = sqlite3.connect(args.db)
	db.execute("DROP TABLE IF EXISTS input")
	db.execute("CREATE TABLE input (key, value)")
	db.execute("CREATE TABLE IF NOT EXISTS results (key, value, author)")
	with open(args.input, "rb") as file:
		rows = csv.DictReader(file, delimiter="\t")
		for row in rows:
			db.execute("INSERT INTO input (key, value) VALUES (?, ?)", (str(uuid.uuid4()), json.dumps(row)))
	db.commit()
	db.close()

if args.command == "run":
	app.secret_key = "\xaa\nJE\xf6\xab\xa2\x15\xd2{ETN'\xce\xcd\x97\xb8\xf4\xae3\x92\x19)"
	app.config['DB_NAME'] = args.db
	try:
		with open(args.html, "r") as file:
			source = file.read()
	except:
		exit("No such file %s" % args.html)
	app.config['HTML'] = source
	app.run()
elif args.command == "results":
	db = sqlite3.connect(args.db)
	rows = db.execute("SELECT value FROM results").fetchall()
	if len(rows) > 0:
		s = set()
		for row in rows:
			s.update(json.loads(row[0]).keys())
		fieldnames = list(s)
		with open(args.csv, "wb") as file:
			writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter="\t")
			writer.writeheader()
			for row in rows:
				writer.writerow(json.loads(row[0]))
	db.close()
