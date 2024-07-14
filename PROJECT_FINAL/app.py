from flask import Flask, render_template, url_for, request
import sqlite3
from yolo_detect import Start
from cnn_detect import Analyse

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('animal.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']

        query = "SELECT name, password FROM user WHERE name = '"+name+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchall()

        if result:
            return render_template('animal.html')
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')

    return render_template('index.html')


@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
        cursor.execute(command)

        cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/animal', methods=['GET', 'POST'])
def animal():
    if request.method == 'POST':
        img1 = request.form['img1']
        yolo = 'static/test/yolo/'+img1
        print(yolo)
        Start(yolo)
        return render_template('animal.html', yolo_img = 'http://127.0.0.1:5000/static/result/'+img1)
    return render_template('animal.html')

@app.route('/leaf', methods=['GET', 'POST'])
def leaf():
    if request.method == 'POST':
        cnn = request.form['img2']
        print(cnn)
        out, accuracy = Analyse(cnn)
        print(out)

        status = {0:'HEMORRHAGE', 1:'NORMAL'}
        return render_template('leaf.html',accuracy=accuracy, out=status[int(out)], cnn_img = 'http://127.0.0.1:5000/static/test/cnn/'+cnn)
    return render_template('leaf.html')

@app.route('/logout')
def logout():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
