import os
import sys
import sqlite3
import urllib.request
import json
from datetime import datetime
from src.new_enc import enc
from src.new_dec import dec
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, flash, request, redirect, url_for, render_template, session, jsonify
from functools import wraps

UPLOAD_FOLDER = 'src/'
DATABASE = 'database.db'
FEEDBACK_FILE = 'static/feedback/feedback.json'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'txt'])

# Create feedback directory and initialize JSON file
os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump([], f)

# Database initialization
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
        ''')
        conn.commit()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Feedback route
@app.route('/save-feedback', methods=['POST'])
def save_feedback():
    try:
        # Get feedback data
        feedback_data = request.json
        
        # Add timestamp and user information if logged in
        feedback_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'username' in session:
            feedback_data['submitted_by'] = session['username']
        
        # Read existing feedback
        try:
            with open(FEEDBACK_FILE, 'r') as f:
                feedback_list = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            feedback_list = []
        
        # Append new feedback
        feedback_list.append(feedback_data)
        
        # Save updated feedback
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump(feedback_list, f, indent=2)
            
        return jsonify({"status": "success", "message": "Feedback saved successfully"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Optional: Admin route to view feedback (protected)
@app.route('/view-feedback')
@login_required
def view_feedback():
    try:
        with open(FEEDBACK_FILE, 'r') as f:
            feedback_list = json.load(f)
        return render_template('feedback.html', feedback=feedback_list)
    except (FileNotFoundError, json.JSONDecodeError):
        return render_template('feedback.html', feedback=[])

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[2], password):
                session['logged_in'] = True
                session['username'] = username
                flash('Login successful!')
                return redirect(url_for('index_page'))
            else:
                flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if not username or not password or not email:
            flash('All fields are required')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                             (username, hashed_password, email))
                conn.commit()
                flash('Registration successful! Please login.')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out')
    return redirect(url_for('login'))

# Protected routes
@app.route("/")
@login_required
def index_page():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/output/")
@login_required
def output_page():
    return render_template('output.html')

@app.route("/uploadenc/")
@login_required
def uploadenc_page():
    return render_template('uploadenc.html')

@app.route("/uploaddec/")
@login_required
def uploaddec_page():
    return render_template('uploaddec.html')

@app.route('/uploadenc/', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], "image.jpg"))
        print('upload_image filename: ' + filename)
        enc()
        return render_template('index.html')
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/uploaddec/', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], "encrypted.txt"))
        print('upload_image filename: ' + filename)
        dec()
        return render_template('index.html')
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)