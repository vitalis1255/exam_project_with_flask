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


init_db()#function call



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



@app.route('/admin', methods=['GET','POST'])
def admin_dashboard():
  #Check if the role is admin
  if session.get('role') != 'admin':
    return redirect(url_for('login'))

  #Get AddUserForn() class and QuestionForm() class
  user_form = AddUserForm()
  q_form =  QuestionForm()

  users = load_json(USERS_FILE)
  questions = load_json(QUESTIONS_FILE)

  if user_form.validate_on_submit() and 'submit_user' in request.form:
    new_username = user_form.username.data.strip()
    
    #check if username exist
    if any(u['username'].lower() == new_username.lower() for u in users):
      flash("Username already exists!")
    else:
      users.append({
        "username":new_username,
        "role":user_form.role.data
      })
      save_json(USERS_FILE, users)
      flash(
        f"Successfully created account for {new_username}!"
      )
      return redirect(url_for('admin_dashboard'))


  if q_form.validate_on_submit() and 'submit_question' in request.form:
    questions.append({
      "id":len(questions) + 1,
      "subject":q_form.subject.data.strip().title(),
      "question_text":q_form.question_text.data,
      "option_a":q_form.option_a.data,
      "option_b":q_form.option_b.data,
      "option_c":q_form.option_c.data,
      "option_d":q_form.option_d.data,
      "correct_answer":q_form.correct_answer.data
    })
    save_json(QUESTIONS_FILE,questions)
    flash("Question added successfully to bank!")
    return redirect(url_for('admin_dashboard'))

  return render_template('admin_dashboard.html', user_form=user_form, q_form=q_form, users=users, questions=questions)



@app.route('/exam/config', methods=['GET', 'POST'])
def exam_config():
  if session.get('role') != 'student':
    return redirect(url_for('login'))

  questions = load_json(QUESTIONS_FILE)
  subjects = sorted(list(set(q['subject'] for q in questions)))

  if not subjects:
    flash("No exam subjects available yet. Contact administrator.")
    return  render_template("exam_config.html",form=None,subjects_exist=False)


  form = ExaminationForm()
  form.subject.choices = [(s,s) for s in subjects]

  if form.validate_on_submit():
    subject = form.subject.data
    count = form.question_count.data
    duration = form.duration_minutes.data

    # Filter questions for this subject
    subj_questions = [q for q in questions if q['subject'] == subject]
    if count > len(subj_questions):
      flash(
        f"Requested count exceeds available questions ({len(subj_questions)})."
      )
      return redirect(url_for('exam_config'))

    session['exam_session'] = {
      'subject':subject,
      'duration_seconds':duration * 60,
      'questions':subj_questions[:count],
      'start_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    session['user_answers'] = {}
    return redirect(url_for('exam_room'))


  return render_template('exam_config.html',form=form,subjects_exist=True)




@app.route('/exam/room', methods=['GET','POST'])
def exam_room():
  if session.get('role') != 'student' or 'exam_session' not in session:
    return redirect(url_for('login'))

  exam = session['exam_session']
  return render_template('exam.html',exam=exam)



@app.route('/exam/submit', methods=['GET','POST'])
def exam_submit():
  if session.get('role') != 'student' or 'exam_session' not in session:
    return jsonify({
      "error":"Unauthorized"
    }), 401

  data = request.get_json()
  # format: {question_id: selected_option}
  submitted_answers = data.get('answers', {})

  exam = session['exam_session']
  questions = exam['questions']

  score = 0
  total = len(questions)
  breakdown = []

  for q in questions:
    q_id = str(q['id'])
    user_choice = submitted_answers.get(q_id, None)
    is_correct = (user_choice == q['correct_answer'])
    if is_correct:
      score +=1

    breakdown.append({
      'question_text':q['question_text'],
      'options':{
        'A':q['option_a'],
        'B':q['option_b'],
        'C':q['option_c'],
        'D':q['option_c']
      },
      'user_choice':user_choice,
      'correct_answer':q['correct_answer'],
      'is_correct':is_correct
    })
  percentage = round((score / total) * 100, 1) if total > 0 else 0

  result_record = {
    'username':session['username'],
    'subject':exam['subject'],
    'score':score,
    'total':total,
    'percentage':percentage,
    'submitted_at':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'breakdown':breakdown
  }

  results = load_json(RESULTS_FILE)
  results.append(result_record)
  save_json(RESULTS_FILE, results)


  # store latest result in session for rendering
  session['last_result'] = result_record
  session.pop('exam_session', None)

  return jsonify({
    "redirect":url_for('exam_result')
  })



@app.route('/exam/result')
def exam_result():
  if session.get('role') != 'student' or 'last_result' not in session:
    return redirect(url_for('login'))


  result = session['last_result']
  return render_template('result.html',result=result)




if __name__ == "__main__":
  app.run(host="127.0.0.1",port=5000,debug=True)
