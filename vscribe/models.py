from vscribe import db
import datetime

class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_time = db.Column(db.Integer)
    total_marks = db.Column(db.Integer)
    subject = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime)
    questions = db.relationship('Element',backref='parent_qpaper', passive_deletes=True, lazy=True)

class Element(db.Model):
    question_no = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.String(10), nullable=False)
    marks_alloted = db.Column(db.Integer)
    question = db.Column(db.Text)
    subjective_answer = db.Column(db.Text)
    mcq_options = db.relationship('MCQ_OP',backref='parent_question', passive_deletes=True, lazy=True)
    parent_qpaper_id = db.Column(db.Integer, db.ForeignKey('paper.id',ondelete='CASCADE'), nullable=False)

class MCQ_OP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_question_no = db.Column(db.Integer, db.ForeignKey('element.question_no',ondelete='CASCADE'), nullable=False)
    option_name = db.Column(db.String(400), nullable=False)
    isSelected = db.Column(db.Boolean, default=False)