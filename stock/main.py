from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import csv
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    # if 'loggedin' in session:
    #     # We need all the account info for the user so we can display it on the profile page
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
    #     account = cursor.fetchone()
    #     # Show the profile page with account info
    #     return render_template('profile.html', account=account)
    # # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/nse')
def nse():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open('static/nse.csv'))
        cursor.execute('TRUNCATE TABLE nse')
        for row in csv_data:
            cursor.execute('INSERT INTO nse (id, open, high, low, close, adj, volume) values (%s, %s, %s, %s, %s, %s, %s)', row)
        mysql.connection.commit()    
        sql1 = """ SELECT low FROM nse WHERE low =  ( SELECT MIN(low) FROM nse where id between '2019-08-13' AND '2020-08-13' and open > 0); """
        sql2 = """ SELECT high FROM nse WHERE high =  ( SELECT MAX(high) FROM nse where id between '2019-08-13' AND '2020-08-13' and open > 0); """
        sql3 = """ select open from nse where id = '2020-08-13'; """
        sql4 = """ select high from nse where id = '2020-08-13'; """
        sql5 = """ select low from nse where id = '2020-08-13'; """
        sql6 = """ select close from nse where id = '2020-08-13'; """
        cursor.execute(sql1)
        var1 = cursor.fetchone()
        cursor.execute(sql2)
        var2 = cursor.fetchone()
        cursor.execute(sql3)
        var3 = cursor.fetchone()
        cursor.execute(sql4)
        var4 = cursor.fetchone()
        cursor.execute(sql5)
        var5 = cursor.fetchone()
        cursor.execute(sql6)
        var6 = cursor.fetchone()
    return render_template('fun1.html', low = var1, high = var2, open = var3, dh = var4, dl = var5, dc = var6)

@app.route('/pythonlogin/bse')
def bse():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open('static/bse.csv'))
        cursor.execute('TRUNCATE TABLE BSE')
        for row in csv_data:
            cursor.execute('INSERT INTO BSE (id, open, high, low, close, adj, volume) values (%s, %s, %s, %s, %s, %s, %s)', row)
        mysql.connection.commit()    
        sql1 = """ SELECT low FROM bse WHERE low =  ( SELECT MIN(low) FROM bse where id between '2019-08-13' AND '2020-08-13' and open > 0); """
        sql2 = """ SELECT high FROM bse WHERE high =  ( SELECT MAX(high) FROM bse where id between '2019-08-13' AND '2020-08-13' and open > 0); """
        sql3 = """ select open from bse where id = '2020-08-13'; """
        sql4 = """ select high from bse where id = '2020-08-13'; """
        sql5 = """ select low from bse where id = '2020-08-13'; """
        sql6 = """ select close from bse where id = '2020-08-13'; """
        cursor.execute(sql1)
        var1 = cursor.fetchone()
        cursor.execute(sql2)
        var2 = cursor.fetchone()
        cursor.execute(sql3)
        var3 = cursor.fetchone()
        cursor.execute(sql4)
        var4 = cursor.fetchone()
        cursor.execute(sql5)
        var5 = cursor.fetchone()
        cursor.execute(sql6)
        var6 = cursor.fetchone()
    return render_template('fun1.html', low = var1, high = var2, open = var3, dh = var4, dl = var5, dc = var6)

@app.route('/pythonlogin/ashokley')
def ashokley():
    if 'loggedin' in session:
        name = 'ashokley'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open('static/ashokley.csv'))
        cursor.execute('TRUNCATE TABLE ashokley')
        for row in csv_data:
            cursor.execute('INSERT INTO ashokley (id, open, high, low, close, adj, volume) values (%s, %s, %s, %s, %s, %s, %s)', row)
        mysql.connection.commit()  
        sql1 = """ select id from ashokley """  
        sql2 = """ select open from ashokley """
        cursor.execute(sql1)
        var1 = cursor.fetchall()
        cursor.execute(sql2)
        var2 = cursor.fetchall()
    return render_template('base.html', date = var1, open = var2, name = name)

@app.route('/pythonlogin/cipla')
def cipla():
    if 'loggedin' in session:
        name = 'cipla'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open('static/cipla.csv'))
        cursor.execute('TRUNCATE TABLE cipla')
        for row in csv_data:
            cursor.execute('INSERT INTO cipla (id, open, high, low, close, adj, volume) values (%s, %s, %s, %s, %s, %s, %s)', row)
        mysql.connection.commit()  
        sql1 = """ select id from cipla """  
        sql2 = """ select open from cipla """
        cursor.execute(sql1)
        var1 = cursor.fetchall()
        cursor.execute(sql2)
        var2 = cursor.fetchall()
    return render_template('base.html', date = var1, open = var2, name = name)

@app.route('/pythonlogin/eichermot')
def eichermot():
    if 'loggedin' in session:
        name = 'eichermot'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open('static/eichermot.csv'))
        cursor.execute('TRUNCATE TABLE eichermot')
        for row in csv_data:
            cursor.execute('INSERT INTO eichermot (id, open, high, low, close, adj, volume) values (%s, %s, %s, %s, %s, %s, %s)', row)
        mysql.connection.commit()  
        sql1 = """ select id from eichermot """  
        sql2 = """ select open from eichermot """
        cursor.execute(sql1)
        var1 = cursor.fetchall()
        cursor.execute(sql2)
        var2 = cursor.fetchall()
    return render_template('base.html', date = var1, open = var2, name = name)

@app.route('/pythonlogin/reliance')
def reliance():
    if 'loggedin' in session:
        name = 'reliance'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open('static/reliance.csv'))
        cursor.execute('TRUNCATE TABLE reliance')
        for row in csv_data:
            cursor.execute('INSERT INTO reliance (id, open, high, low, close, adj, volume) values (%s, %s, %s, %s, %s, %s, %s)', row)
        mysql.connection.commit()  
        sql1 = """ select id from reliance """  
        sql2 = """ select open from reliance """
        cursor.execute(sql1)
        var1 = cursor.fetchall()
        cursor.execute(sql2)
        var2 = cursor.fetchall()
    return render_template('base.html', date = var1, open = var2, name = name)

@app.route('/pythonlogin/tatasteel')
def tatasteel():
    if 'loggedin' in session:
        name = 'tatasteel'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        csv_data = csv.reader(open('static/tatasteel.csv'))
        cursor.execute('TRUNCATE TABLE tatasteel')
        for row in csv_data:
            cursor.execute('INSERT INTO tatasteel (id, open, high, low, close, adj, volume) values (%s, %s, %s, %s, %s, %s, %s)', row)
        mysql.connection.commit()  
        sql1 = """ select id from tatasteel """  
        sql2 = """ select open from tatasteel """
        cursor.execute(sql1)
        var1 = cursor.fetchall()
        cursor.execute(sql2)
        var2 = cursor.fetchall()
    return render_template('base.html', date = var1, open = var2, name = name)

if __name__ == "__main__":
    app.run(debug = True)