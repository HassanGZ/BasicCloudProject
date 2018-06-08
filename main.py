#Name:PRADEEP RAVICHANDRAN
#ID:1001553352
#CSE 6331-Cloud Computing
#Assignment 1


import os
from flask import Flask, render_template, request
import sqlite3 as sql
#ALLOWED EXTENSIONS is used to restrict the types of input files uploaded by the user
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
UPLOAD_FOLDER = 'templates/'

import sqlite3, csv, base64
#sqlite database connection
con = sqlite3.connect('database.db')

#creating cursor to perform database operations
cursor = con.cursor()
cursor.execute("DROP TABLE people")
con.commit()
#executing create table query
cursor.execute("CREATE TABLE people (name, grade, room, telnum, picture, keywords);")
cursor.execute("DROP TABLE course")
cursor.execute("CREATE TABLE course (id, days, start, end, approval, max, current, seats, wait, instructor, courseno, section);")
cursor.execute("DROP TABLE pic")
con.commit()
#executing create table query
cursor.execute("CREATE TABLE pic (picture TEXT, img BLOB);")
#UPLOAD_FOLDER = os.path.basename('uploads/')
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
    cursor = con.cursor()
    cursor.execute("select instructor, courseno, start, end from course where courseno = ? and days = ? ",((request.form['cno']), (request.form['days'])))
    rows = cursor.fetchall()
    if len(rows) == 0:
        return render_template("sresult.html", res=[request.form['cno'],request.form['days'], ''])
    #cursor.execute("select img from pic where picture = ? ", (str(rows[0][0]).lower(),))
    #rows = cursor.fetchall()
    #if len(rows) == 0:
    #    images = ''
    else:
        #decode the image
        #images = rows[0][0].decode('utf-8')
        return render_template("sresult.html", res=[request.form['cno'],request.form['days'],''])

@app.route('/getsize')
def getsize():
    cwd = os.getcwd()
    size = os.path.getsize(cwd)
    return render_template('size.html',size=size)

@app.route('/newpic')
def newpic():
   con = sql.connect("database.db")
   cursor = con.cursor()
   cursor.execute("select name from people")
   rows = cursor.fetchall()
   return render_template('newpic.html', rows=rows)

@app.route('/deletionpage')
def deletionpage():
   con = sql.connect("database.db")
   cursor = con.cursor()
   cursor.execute("select name from people")
   rows = cursor.fetchall()
   return render_template('deletionpage.html',rows = rows)

@app.route('/editingpage')
def editingpage():
   con = sql.connect("database.db")
   cursor = con.cursor()
   cursor.execute("select name from people")
   rows = cursor.fetchall()
   return render_template('editingpage.html',rows = rows)

@app.route('/csvtodb', methods=['GET','POST'])
def csvtodb():

    if request.method == 'POST':
        dlen = {}
        try:
            fname = request.files.getlist("images")
            for i in range(len(fname)):
                print(fname[i].filename)
                filename = fname[i].filename
                file = fname[i]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                myfile = open('templates/'+filename,'rb')
                readimg = myfile
                image = readimg.read()
                dlen[filename] = len(image)
                #using base64 to encode image
                image = base64.b64encode(image)
                con = sql.connect("database.db")
                cursor = con.cursor()
                #inserting image into table 'pic'
                cursor.execute("INSERT INTO pic(picture,img) values(?,?)", (fname[i].filename.lower(), image))
                con.commit()
            #converting csv file into table with values
            if request.method == 'POST':
                 file = request.files['myfile']
                 con = sqlite3.connect('database.db')
                 cursor = con.cursor()
            with open(file.filename, 'r') as finput:
                read = csv.DictReader(finput)
                fromcsv = [(i['Name'], i['Grade'], i['Room'], i['Telnum'], i['Picture'], i['Keywords']) for i in read]

                cursor.executemany("INSERT INTO people (name, grade, room, telnum, picture, keywords) VALUES (?, ? ,? ,? ,? ,?);", fromcsv)
                con.commit()
                #cursor.execute("select * from people")
                con.close()
                msg = "Record successfully added"
        except:
                con.rollback()
                msg = "Error"
        finally:
            msg="Performed Successfully"
            return render_template("home.html")
            con.close()
            print(msg)


@app.route('/namesearch', methods=['GET','POST'])
def name_search():
    return render_template('namesearch.html')


@app.route('/gradesearch', methods=['GET','POST'])
def grade_search():
    return render_template('gradesearch.html')

#function to list the table
@app.route('/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cursor = con.cursor()
    cursor.execute("select * from people")
    rows = cursor.fetchall();
    return render_template("list.html", rows=rows)

#function to search picture using name
@app.route('/search_by_name', methods=['POST', 'GET'])
def search_by_name():
    con = sql.connect("database.db")
    cursor = con.cursor()
    cursor.execute("select picture from people where name = ? ", (request.form['name'],))
    rows = cursor.fetchall()
    if len(rows) == 0:
        return render_template("results.html", res=[request.form['name'], ''])
    cursor.execute("select img from pic where picture = ? ", (str(rows[0][0]).lower(),))
    rows = cursor.fetchall()
    if len(rows) == 0:
        pictures = ''
    else:
        #decode the image
        pictures = rows[0][0].decode('utf-8')
    return render_template("results.html", res=[request.form['name'], pictures])

#function for searching using grade
@app.route('/search_by_grade', methods=['POST', 'GET'])
def search_by_grade():
    con = sql.connect("database.db")
    cursor = con.cursor()
    operation = request.form['op']
    print(operation)
    if operation == 'lt':
        cursor.execute("select i.img from people p,pic i where p.picture=i.picture and grade < ? ",(request.form['grade'],))
    elif operation == 'gt':
        cursor.execute("select i.img from people p,pic i where p.picture=i.picture and grade > ? ",(request.form['grade'],))
    else:
        cursor.execute("select i.img from people p,pic i where p.picture=i.picture and grade = ? ",(request.form['grade'],))
    rows = cursor.fetchall()
    print(rows)
    if len(rows) == 0:
        return render_template("gimg.html", res=[operation, request.form['grade'], ''])
    pictures = []
    for row in rows:
       pictures.append(row[0].decode('utf-8'))
    #else:
        #images = rows[0][0].decode('utf-8')
    return render_template("gimg.html", res=[request.form['grade'], pictures])

#function to add image for people
@app.route('/addimage', methods=['POST', 'GET'])
def addimage():
    con = sql.connect("database.db")
    cursor = con.cursor()
    op = request.form['name']
    readimg = request.files.get("images")
    fname = readimg.filename
    image = readimg.read()
    image = base64.b64encode(image)
    cursor.execute("update people set picture = ? where name = ?", (fname.lower(), op))
    con.commit()
    cursor.execute("select img from pic where picture = ? ", (fname.lower(),))
    rows = cursor.fetchall()
    if len(rows) == 0:
        cursor.execute("insert into pic(picture,img) values(?,?)", (fname.lower(), image))
        con.commit()
    else:
        cursor.execute("update pic set img = ? where picture = ?", (image, fname.lower()))
        con.commit()
    con.close()
    return render_template("result.html", msg="Picture Added successfully")

#function to remove people
@app.route('/delete_people', methods=['POST', 'GET'])
def delete_people():
    con = sql.connect("database.db")
    cursor = con.cursor()
    cursor.execute("select picture from people where name=?", (request.form['name'],))
    rows = cursor.fetchall()
    cursor.execute("delete from people where name = ?", (request.form['name'],))
    # con.commit()
    print(rows)
    cursor.execute("delete from pic where picture = ?", rows[0])
    con.commit()
    con.close()
    return render_template("deleteresult.html", msg="Record Deleted successfully")

#function to edit any column in the table 'people'
@app.route('/edit', methods=['POST', 'GET'])
def edit():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cursor = con.cursor()
    cursor.execute("select * from people where name=?", (request.form['name'],))
    rows = cursor.fetchall();
    return render_template("edit.html", rows=rows)

#function to update any column in table 'people'
@app.route('/updatedata', methods=['POST', 'GET'])
def updatedata():
    con = sql.connect("database.db")
    cursor = con.cursor()
    cursor.execute("update people set grade = ?,room=?,telnum=?,keywords=? where name = ?",
                (request.form['grade'], request.form['room'], request.form['telnum'], request.form['keywords'],request.form['username']))
    con.commit()
    con.close()
    return render_template("result.html", msg="Data Edited successfully")

if __name__ == '__main__':
    app.run(debug=True)