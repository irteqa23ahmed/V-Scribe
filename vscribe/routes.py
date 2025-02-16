from flask import render_template, url_for, flash, redirect, request, Response, jsonify, abort
from vscribe import app
from vscribe.models import *
from vscribe.utils import *

#Temporary
@app.route('/')
@app.route('/start')
def start():
    get_question_paper_and_store()
    scribe_speaks(WELCOME)
    first_question = go_to_question_num(FIRST_QNO, ENTITY_FIRST_QNO)
    return render_template('question_page.html',question=first_question, isNotMcq = first_question.question_type!=MCQ_QUESTION_TYPE)

@app.route('/speech')
def process_text():
    q_no = request.args.get("q_no")
    scribe_speaks(OFFER_ASSISTANCE)
    choice = get_audio(time_limit = 8,isstop=True).lower()
    
    if choice == FAILED_AUDIO_SYM: choice = EMPTY_STRING
    
    intent,entities = get_intent(choice) #Also should return an entity if it exists or None
    action = actionOnIntent.get(intent)

    print("action : "+str(action))

    if action!=None:
        resp = action(q_no=q_no,entities=entities)
        if resp != None:
            return render_template('question_page.html',question=resp, isNotMcq = resp.question_type!='MCQ')
        elif intent == 'finish':
            return render_template('finish.htm')
    else:
        scribe_speaks(TRY_AGAIN)

    resp = Element.query.get(q_no)
    return render_template('question_page.html',question=resp, isNotMcq = resp.question_type!=MCQ_QUESTION_TYPE) # Should be an Element Model