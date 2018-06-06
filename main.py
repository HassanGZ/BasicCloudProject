#Name:PRADEEP RAVICHANDRAN
#ID:1001553352
#CSE 6331-Cloud Computing
#Assignment 1


import os
from flask import Flask, render_template, request
import sqlite3 as sql
#from werkzeug import secure_filename
#ALLOWED EXTENSIONS is used to restrict the types of input files uploaded by the user
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
UPLOAD_FOLDER = 'templates/'

import sqlite3, csv, base64
#sqlite database connection
conn = sqlite3.connect('database.db')

#creating cursor to perform database operations
cur = conn.cursor()
cur.execute("DROP TABLE people")
conn.commit()
#executing create table query
cur.execute("CREATE TABLE people (name, grade, room, telnum, picture, keywords);")
cur.execute("DROP TABLE course")
cur.execute("CREATE TABLE course (id, days, start, end, approval, max, current, seats, wait, instructor, courseno, section);")
cur.execute("DROP TABLE pic")
conn.commit()
#executing create table query
cur.execute("CREATE TABLE pic (picture TEXT, img BLOB);")
UPLOAD_FOLDER = os.path.basename('uploads/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#@app.route are decorators in Flask
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/course')
def course():
    return render_template('courseform.html')

@app.route('/search_by_no', methods=['GET','POST'])
def search_by_no():
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("select instructor, courseno, start, end from course where courseno = ? and day = ? ", (request.form['cno']),(request.form['day']))
    rows = cur.fetchall()
    if len(rows) == 0:
        return render_template("sresult.html", res=[request.form['name'], ''])
    cur.execute("select img from pic where picture = ? ", (str(rows[0][0]).lower(),))
    rows = cur.fetchall()
    if len(rows) == 0:
        images = ''
    else:
        # decode the image
        images = rows[0][0].decode('utf-8')
    return render_template("sresult.html", res=[request.form['name'], images])

@app.route('/newpic')
def newpic():
   con = sql.connect("database.db")
   cur = con.cursor()
   cur.execute("select name from people")
   rows = cur.fetchall()
   return render_template('newpic.html', rows=rows)

@app.route('/deletionpage')
def deletionpage():
   con = sql.connect("database.db")
   cur = con.cursor()
   cur.execute("select name from people")
   rows = cur.fetchall()
   return render_template('deletionpage.html',rows = rows)

@app.route('/editingpage')
def editingpage():
   con = sql.connect("database.db")
   cur = con.cursor()
   cur.execute("select name from people")
   rows = cur.fetchall()
   return render_template('editingpage.html',rows = rows)

@app.route('/csvtodb', methods=['GET','POST'])
def csvtodb():
    if request.method == 'POST':
        data_len = {}
        try:
            fname = request.files.getlist("images")
            for i in range(len(fname)):
                print(fname[i].filename)
                filename =fname[i].filename
                file = fname[i]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file.close()
                readimg = fname[i]
                img = readimg.read()
                data_len[fname[i].filename] = len(img)
                #using base64 to encode image
                img = base64.b64encode(img)
                con = sql.connect("database.db")
                cur = con.cursor()
                #inserting image into table 'pic'
                cur.execute("INSERT INTO pic(picture,img) values(?,?)", (fname[i].filename.lower(), img))
                con.commit()
            #converting csv file into table with values
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

                cur.executemany("INSERT INTO people (name , grade, room, telnum, picture, keywords) VALUES (?, ? ,? ,? ,? ,?);", to_db)
                conn.commit()
                #cur.execute("select * from people")
                conn.close()
                msg = "Record successfully added"
        except:
                con.rollback()
                msg = "Error occured while performing the operation"
        finally:
            msg="Performed Successfully"
            return render_template("home.html")
            con.close()


@app.route('/namesearch', methods=['GET','POST'])
def name_search():
    return render_template('namesearch.html')


@app.route('/gradesearch', methods=['GET','POST'])
def grade_search():
    return render_template('gradesearch.html')


#def picture():
#    conn = sqlite3.connect('database.db')
##    cur = conn.cursor()
 #   cur.execute('Insert into img (id, name, bin) values(?, ?, ?);', (id, name, sqlite3.Binary(file.read())))
#@app.route('/getpic',methods = ['POST','Get'])
#def getpic():
#   if request.method == 'POST':
#      file = request.files['pic']
#      f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#      file.save(f)
#      return render_template("home.html")

#function to list the table
@app.route('/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from people")
    rows = cur.fetchall();
    return render_template("list.html", rows=rows)

#function to search picture using name
@app.route('/search_by_name', methods=['POST', 'GET'])
def search_by_name():
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("select picture from people where name = ? ", (request.form['name'],))
    rows = cur.fetchall()
    if len(rows) == 0:
        return render_template("sresult.html", res=[request.form['name'], ''])
    cur.execute("select img from pic where picture = ? ", (str(rows[0][0]).lower(),))
    rows = cur.fetchall()
    if len(rows) == 0:
        images = ''
    else:
        #decode the image
        images = rows[0][0].decode('utf-8')
    return render_template("sresult.html", res=[request.form['name'], images])

#function for searching using grade
@app.route('/search_by_grade', methods=['POST', 'GET'])
def search_by_grade():
    con = sql.connect("database.db")
    cur = con.cursor()
    op = request.form['op']
    if op == 'lt':
        cur.execute("select i.img from people p,pic i where p.picture=i.picture and grade < ? ",
                    (request.form['grade'],))
    elif op == 'gt':
        cur.execute("select i.img from people p,pic i where p.picture=i.picture and grade > ? ",
                    (request.form['grade'],))
    else:
        cur.execute("select i.img from people p,pic i where p.picture=i.picture and grade = ? ",
                    (request.form['grade'],))
    rows = cur.fetchall()
    if len(rows) == 0:
        return render_template("sresult.html", res=[op, request.form['grade'], ''])
    images = []
    for row in rows:
        images.append(row[0].decode('utf-8'))
    return render_template("gimg.html", res=[op, request.form['grade'], images])

#function to add image for people
@app.route('/addimage', methods=['POST', 'GET'])
def addimage():
    con = sql.connect("database.db")
    cur = con.cursor()
    op = request.form['name']
    readimg = request.files.get("images")
    fname = readimg.filename
    img = readimg.read()
    img = base64.b64encode(img)
    cur.execute("update people set picture = ? where name = ?", (fname.lower(), op))
    con.commit()
    cur.execute("select img from pic where picture = ? ", (fname.lower(),))
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.execute("insert into pic(picture,img) values(?,?)", (fname.lower(), img))
        con.commit()
    else:
        cur.execute("update pic set img = ? where picture = ?", (img, fname.lower()))
        con.commit()
    con.close()
    return render_template("result.html", msg="Data Updated successfully")

#function to remove people
@app.route('/delete_people', methods=['POST', 'GET'])
def delete_people():
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("select picture from people where name=?", (request.form['name'],))
    rows = cur.fetchall()
    cur.execute("delete from people where name = ?", (request.form['name'],))
    # con.commit()
    print(rows)
    cur.execute("delete from pic where picture = ?", rows[0])
    con.commit()
    con.close()
    return render_template("result.html", msg="Data Updated successfully")

#function to edit any column in the table 'people'
@app.route('/edit', methods=['POST', 'GET'])
def edit():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from people where name=?", (request.form['name'],))
    rows = cur.fetchall();
    return render_template("edit.html", rows=rows)

#function to update any column in table 'people'
@app.route('/updatedata', methods=['POST', 'GET'])
def updatedata():
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("update people set grade = ?,room=?,telnum=?,keywords=? where name = ?",
                (request.form['grade'], request.form['room'], request.form['telnum'], request.form['keywords'],request.form['username']))
    con.commit()
    con.close()
    return render_template("result.html", msg="Data Updated successfully")

if __name__ == '__main__':
    app.run(debug=True)