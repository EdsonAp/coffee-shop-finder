from flask import Flask, render_template, request, session, flash, redirect
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from flask import Flask
from yelp_api import apiKey
import requests
import re 


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')     
#INVALID_PASSWORD_REGEX = re.compile(r'^[^0-9]*|[^A-Z]*)$')

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "Keep it secret"

@app.route('/')
def register():
    return render_template('index.html')

@app.route('/usernew', methods = ['POST'])
def newuser_registration():
    is_valid=True
    if len(request.form['fname'])<2:
        is_valid=False
        flash('Please enter first name')
    if len(request.form['lname'])<2:
        is_valid=False
        flash('Please enter last name')
    if not EMAIL_REGEX.match(request.form['email']):
        flash('Please enter a valid email')    
    if len(request.form['password'])<5:
        is_valid=False
        flash('Password must be at least 8 characters long')
    if request.form['c_password'] != request.form['password']:
        is_valid=False
        flash('Passwords do no match')
    if is_valid:
        print('[PASS HASH FUNTION')
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        mysql = connectToMySQL('dbcafe')
        query = 'INSERT INTO users(firstname, lastname, email, password, created_at, updated_at) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s, NOW(), NOW())'
        data = {
            'nombre' : request.form['fname'], 
            'apellido' : request.form['lname'], 
            'email' : request.form['email'], 
            'password' : pw_hash
        }
        new_userid = mysql.query_db(query, data)
        print('query')
        session['user_id'] = new_userid
        session['greeting'] = request.form['fname']
        session['greeting2'] = request.form['lname']
        return redirect('/success')
    return redirect('/')   

@app.route('/login', methods = ['POST'])
def log():
    print('LOGINFUNCTION')
    is_valid=True
    if not EMAIL_REGEX.match(request.form['email']):
        flash('Please enter your email')
    if len(request.form['password'])<1:
        is_valid = False
        flash('Please enter your password')
    if not is_valid:
        return redirect('/')
    else:
        mysql = connectToMySQL('dbcafe')
        query = 'SELECT * FROM users WHERE email = %(em)s;'
        data = { 'em': request.form['email']}
        output = mysql.query_db(query, data)
        session['greeting'] = output[0]['firstname']
        session['greeting2'] = output[0]['lastname']
        session['user_id'] = output[0]['id']
        print('OUTPUT PRINTED BELOW')
        print(output)
        if len(output) > 0:
            if bcrypt.check_password_hash(output[0]['password'],request.form['password']):
                return redirect('/success')
            else:
                flash('Email and password do not match')
        else:
            flash('Email has not been registered')
        return redirect('/')


@app.route('/success', methods =['POST','GET'])
def registration_land():
    if 'user_id' not in session:
        return redirect('/')

    api_key = apiKey
    end_point = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'bearer %s' %api_key}
    # Define parameters for search request 
    parameters = {
            'term' : 'coffee',
            'location' : request.form.get('location'),
            'radius':10000,
            'limit': 10 }
     # Make request to the Yelp Api
    response = requests.get(url = end_point, params = parameters , headers = headers) 
    #convert JSON to Dictionary
    data_results = response.json()
    session['data'] = data_results
    print('data_results')
    return render_template('success.html', data=data_results)


@app.route('/sub', methods = ['POST'])
def submit_comment():
    mysql = connectToMySQL('dbcafe')
    query = 'INSERT INTO comments (message, created_at, updated_at, user_id) VALUES (%(msg)s,NOW(),NOW(), %(id)s);'
    data = {
        'msg': request.form['comment'],
        'id' : session['user_id']
    }
    inserted = mysql.query_db(query, data)
    print(inserted)
    return redirect('/comments')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

    

if __name__ == "__main__":
    app.run(debug=True)