"""
Forms to use across the whole
applications
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, length, NumberRange



#Login Form
class LoginForm(FlaskForm):
  """
  Handle Form Login Fields Generation
  and Validations
  """
  username = StringField("username/Identifier", validators=[DataRequired(message="Username is required."),length(min=2, max=30, message="Must be between 2 and 30 characters.")])
  role = SelectField("Portal Role", choices=[
    ("student","Student/Examinee"),
    ("admin","Administrator")
  ], validators=[DataRequired()])
  submit = SubmitField("Sign In")



#User Form
class AddUserForm(FlaskForm):
  """
  Create a new user
  """
  username = StringField("New Username",validators=[DataRequired(), length(min=2, max=30)])
  role = SelectField("Account Role", choices=[
    ("student","Student"),
    ("admin","Administrator")
  ],validators=[DataRequired()])
  submit = SubmitField("Create Account")



#Question Form
class QuestionForm(FlaskForm):
  """ Create Question """
  subject = StringField("Subject name", validators=[DataRequired(), length(min=2, max=50)])
  question_text = TextAreaField("Question Text", validators=[DataRequired()])
  option_a = StringField("Option A",validators=[DataRequired()])
  option_b = StringField("Option B",validators=[DataRequired()])
  option_c = StringField("Option C",validators=[DataRequired()])
  option_d = StringField("Option D",validators=[DataRequired()])
  correct_answer = SelectField("Correct Answer", choices=[
      ("A", "Option A"),
      ("B", "Option B"),
      ("C", "Option C"),
      ("D", "Option D"),
    ], validators=[DataRequired()])
  submit = SubmitField("Save Question")



# Start Examination Form
class ExaminationForm(FlaskForm):
  """ Exam configurations"""
  subject = SelectField("Select Subject", choices=[], validators=[DataRequired()])
  question_count = IntegerField("Questions to Attempt", validators=[
    DataRequired(), NumberRange(min=1, max=100)
  ])
  duration_minutes = IntegerField("Duration(Minutes)", validators=[DataRequired(), NumberRange(min=1, max=120)])
  submit = SubmitField("Start Examination")