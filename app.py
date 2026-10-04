from flask import Flask, url_for, render_template,redirect, session, request, flash, jsonify
from forms import LoginForm, QuestionForm, ExaminationForm, AddUserForm
import os
import json
from datetime import datetime


app = Flask(__name__)
app.secret_key = "cbt_v2_ultra_secure_secret_key_2026"


DATA_DIR = 'data'#folder name
USERS_FILE = os.path.join(DATA_DIR,'users.json')#put json file inside folder name using join
QUESTIONS_FILE = os.path.join(DATA_DIR, 'questions.json')
RESULTS_FILE = os.path.join(DATA_DIR, 'results.json')




def init_db():
  os.makedirs(DATA_DIR, exist_ok=True)#create a folder
  if not os.path.exists(USERS_FILE):
    #Default Admin account pre-seeded
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
      json.dump([
        {
          "username":"admin",
          "role":"admin"
        }
      ], f, indent=4)

  if not os.path.exists(QUESTIONS_FILE):
    with open(QUESTIONS_FILE, 'w',encoding='utf-8') as f:
      json.dump([], f, indent=4)

  if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
      json.dump([], f, indent=4)


init_db()



def load_json(filepath):
  with open(filepath, 'r', encoding='utf-8') as f:
    return json.load(f)


def save_json(filepath, data):
  with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)



#Login is the home or index page
@app.route('/', methods=['GET', 'POST'])
def login():
  """Login Page"""
  #Get your Login Form
  form = LoginForm()
  if form.validate_on_submit():
    username = form.username.data.strip()
    role = form.role.data

    users = load_json(USERS_FILE)
    user = next((u for u in users if u['username'].lower() == username.lower() and u['role'] == role), None)

    if not user:
      flash(
        f"Account for '{username}' as ' {role}' does not exist. Ask an admin to create it."
      )
      return redirect(url_for('login'))

    session['username'] = user['username']
    session['role'] = user['role']
    flash(f"Welcome back, {user['username']}!")
    if user['role'] == 'admin':
      return redirect(url_for('admin_dashboard'))
    else:
      return redirect(url_for('exam_config'))
  return render_template('login.html', form=form)



@app.route('/logout')
def logout():
  session.clear() #This helps to logout
  flash(
    "You have been logged out successfully."
  )
  return redirect(url_for('login'))