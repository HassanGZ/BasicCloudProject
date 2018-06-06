import os
from flask import Flask, render_template, request
import sqlite3 as sql
import cgi

app = Flask(__name__)

import sqlite3, csv

conn = sqlite3.connect('database.db')
# print("Opened database successfully")
cur = conn.cursor()
cur.execute("DROP TABLE people")
conn.commit()
cur.execute("CREATE TABLE people (Name, Grade, Room, Telnum, Picture, Keywords);")
cur.execute("DROP TABLE img")
conn.commit()
cur.execute("CREATE TABLE img (id NUMBER, name TEXT, bin BLOB);")
UPLOAD_FOLDER = os.path.basename('uploads/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/csvtodb', methods=['GET','POST'])
def csvtodb():
    if request.method == 'POST':
        file = request.files['myfile']
    conn = sqlite3.connect('database.db')
    #print("Opened database successfully")
    cur = conn.cursor()
    #cur.execute("DROP TABLE people")
    #conn.commit()
    #cur.execute("CREATE TABLE people (Name PRIMARY KEY, Grade, Room, Telnum, Picture, Keywords);")
    with open(file.filename, 'r') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['Name'], i['Grade'], i['Room'], i['Telnum'], i['Picture'], i['Keywords']) for i in dr]

    cur.executemany("INSERT INTO people (Name , Grade, Room, Telnum, Picture, Keywords) VALUES (?, ? ,? ,? ,? ,?);", to_db)
    conn.commit()
    #cur.execute("select * from people")
    conn.close()
    return render_template('home.html')


#def picture():
#    conn = sqlite3.connect('database.db')
##    cur = conn.cursor()
 #   cur.execute('Insert into img (id, name, bin) values(?, ?, ?);', (id, name, sqlite3.Binary(file.read())))
@app.route('/getpic',methods = ['POST','Get'])
def getpic():
   if request.method == 'POST':
      file = request.files['pic']
      f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
      file.save(f)
      return render_template("home.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT picture FROM people WHERE Name = %s', (request.form["search"],))
    result = cur.fetchall()
    cur.close()
    return render_template('results.html', result = result)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/enternew')
def new_student():
    return render_template('student.html')


@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            name = request.form['Name']
            grade = request.form['Grade']
            room = request.form['Room']
            telnum = request.form['Telnum']
            picture = request.form['Picture']
            keywords = request.form['Keywords']

            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("INSERT INTO people (name,grade,room,telnum,picture,keywords) VALUES (?,?,?,?)", (name, grade, room, telnum,picture,keywords))

                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from people")

    rows = cur.fetchall();
    return render_template("list.html", rows=rows)


if __name__ == '__main__':
    app.run(debug=True)