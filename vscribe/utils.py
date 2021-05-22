from vscribe import app, db #, storage
from vscribe.models import *
import requests, json
import speech_recognition as sr
import playsound, imutils
from pygame import mixer
# from gtts import gTTS
import socket, cv2,pickle,struct
from io import BytesIO,StringIO
from tempfile import TemporaryFile
import re,time,os,sys,copy, datetime, pymongo
from fpdf import FPDF
import pyttsx3

'''---CONSTANTS-------------------------------------------------------------------------------------------------------------------------'''

punctuationURL = 'http://bark.phon.ioc.ee/punctuator'
intentRecognitionURL = 'http://localhost:5005/model/parse'

mongo_username = "ahmedmumtaz"
mongo_password = "muoNL53BaoUoDr4x"
mongoURL = "mongodb+srv://{0}:{1}@vscribecluster.he6v4.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(mongo_username,mongo_password)
path_on_cloud = '/{0}/{1}/{2}{3}'
path_local = './assets/{0}{1}'

MONGO_DB = 'mydatabase'
MONGO_COLL = 'questions'
STUDENT_RESPONSE = "StudentResponse"
FIRST_QNO = 1
ENTITY_FIRST_QNO = [{'value':FIRST_QNO}]
WIP = 'Work In Progress'
WELCOME = 'Hello! I am Vscribe, your personal scribe for this session.'
SERVICE_FAILURE = 'Service Failed! Please try again!'
CONTINUE = "Do you wish to continue?"
AUDIO_EXT = '.mp3'
PDF_XTN = '.pdf'
ENG_US_LANGUAGE = 'en'
FULL_STOP = '.'
SESSION_END = 'All the best for results'
AUTH_FAILURE = 'User not verified. Click to try again.'
OFFER_ASSISTANCE = 'How can I help you?'
TRY_AGAIN = 'Try Again with a click!'
AUDIO_NOT_RECOGNISED = 'I am sorry. Did not get you there'
READ_QUESTION = "question {0}, question is , {1}"
NAVIGATE_TO_QUESTION = "Going to "+READ_QUESTION
UNAVAILABLE_Q = "Question does not exist"
UNAVAILABLE_OP = "No options available"
READING_OPTIONS = "reading options"
EACH_OPTION = "Option {0}, {1}"
SELECTED_OPTION = "Selected "+EACH_OPTION
SINGLE_RESPONSE_FORMAT = 'Q {0}. {1} \n>> {2}\n\n'
TIMEOUT = 'Time Up, Finishing the session'
SOMETHING_WENT_WRONG = 'Something went wrong! Retry with right choice'
READING_LINE_NO = "Reading...line {0}"
START_DICTATING = "You may start dictating the answer now!"
RECORDED = "Successfully recorded"
FORMATTING_OPTIONS = "continue point? or next point? or para mode? or exit"
RESOURCE_UNAVAILABLE = "No such line"
EXITTING = "Exiting from this command"
EXIT_CMD = "exit"
EMPTY_STRING = ''
FAILED_AUDIO_SYM = '0'
MCQ_QUESTION_TYPE = 'MCQ'
UNANSWERED = '-- NOT ATTEMPTED --'

numTonum = {
    1 : 'one',
    2 : 'two',
    3 : 'three',
    4 : 'four',
    5 : 'five'
}


'''-----UITLITY-FUNCTIONS----------------------------------------------------------------------------------------------------------------'''

# def scribe_speaks(output):
#     ts = time.time()
#     print("V-Scribe : ", output)
#     toSpeak = gTTS(text=output, lang=ENG_US_LANGUAGE, slow=False)
#     file = str(ts)+AUDIO_EXT
#     toSpeak.save(file)
#     playsound.playsound(file, True)
#     os.remove(file)

def scribe_speaks(output):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(output)
    engine.runAndWait()
    engine.stop()

def get_audio(time_limit = None,isstop = False):
    r = sr.Recognizer()
    audio = EMPTY_STRING
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Begin speaking")
        audio = r.listen(source) #, phrase_time_limit=time_limit)
    print("Stop speaking")
    try:
        text = r.recognize_google(audio,language=ENG_US_LANGUAGE)
        print("You : ", text)
        return text
    except Exception as e:
        if isstop == False:
            print(e)
            scribe_speaks(AUDIO_NOT_RECOGNISED)
        return FAILED_AUDIO_SYM

def get_intent(text):
    payload = {'text':text}
    headers = {'content-type': 'application/json'}
    try:
        response = requests.post(intentRecognitionURL, json=payload,headers=headers)
        json_response = response.json()
        intent = json_response.get('intent')
        entities = json_response.get('entities') # List of entities
        intent_name = intent.get('name')
        print("intent :"+str(intent_name))
        return intent_name,entities
    except Exception as e:
        print(e)
        return SERVICE_FAILURE,[]

def punc(text):
    payload = {"text" : text}
    try:
        response = requests.post(punctuationURL, data=payload)
        if response.status_code==200:
            return response.text
        raise Exception(SERVICE_FAILURE)
    except Exception as e:
        print(e)
        return SERVICE_FAILURE

def super_punc(ans):
    # try:
    #     ans = punc(ans)
    # except Exception as e:
    #     print(e)
    #     scribe_speaks(SERVICE_FAILURE)
    return ans

def read_line(answer,line):
    answer = answer.split(FULL_STOP)
    scribe_speaks(READING_LINE_NO.format(line))
    scribe_speaks(answer[line-1])

def write_answer():
    final_dict_ans = ""
    flag = 1
    while flag==1:
        scribe_speaks(START_DICTATING)
        dict_ans = get_audio()
        if dict_ans!=FAILED_AUDIO_SYM or EXIT_CMD in dict_ans:
            final_dict_ans += super_punc(dict_ans)
            scribe_speaks(RECORDED)
            while True:
                scribe_speaks(CONTINUE)
                choice = get_audio(5)
                if choice!=FAILED_AUDIO_SYM:
                    if "yes" in choice.lower():
                        if "list" in choice.lower():
                            final_dict_ans,ch = point_wise_answer(final_dict_ans)
                            if ch == 'no':
                                flag = 0
                        break
                    elif "no" in choice.lower():
                        flag=0
                        break
                    else:
                        scribe_speaks(AUDIO_NOT_RECOGNISED)
        else:
            scribe_speaks(EXITTING)
            break
    return final_dict_ans

def point_wise_answer(ans):
    scribe_speaks("dictate point wise...")
    line_num = 0
    same = False
    while True:
        scribe_speaks("Dictate Point ")
        dict_ans = get_audio()
        if dict_ans!=FAILED_AUDIO_SYM:
            if same == False:
                line_num+=1
                ans += '\n'+str(line_num)+") "
            temp = super_punc(dict_ans)
            ans += temp+FULL_STOP if (temp!='' and temp[-1]!=FULL_STOP) else temp
            scribe_speaks(RECORDED)
            while True:
                scribe_speaks(FORMATTING_OPTIONS)
                choice = get_audio(5)
                if choice!=FAILED_AUDIO_SYM:
                    if "continue" in choice.lower():
                        same = True
                        break
                    elif "next" in choice.lower():
                        same = False
                        break
                    elif "para" in choice.lower():
                        return [ans,'yes']
                    elif EXIT_CMD in choice.lower():
                        return [ans,'no']
                    else:
                        scribe_speaks(AUDIO_NOT_RECOGNISED)

def erase_line(answer, index):
    answer = answer.split(FULL_STOP)
    try:
        removed = answer[index-1]
        answer.pop(index-1)
        scribe_speaks("Removed line : "+removed)
    except Exception as e:
        print(e)
        scribe_speaks(RESOURCE_UNAVAILABLE)
    return FULL_STOP.join(answer)

def erase_till_word(answer,index,word):
    answer = answer.split(FULL_STOP)
    try:
        removed = answer[index-1].split(" ")
        try:
            find = removed.index(word)
            answer[index-1] = re.sub(r''+word+'.*', word, answer[index-1])
            scribe_speaks("Updated answer")
        except Exception as e:
            print(e)
            scribe_speaks("Could'nt find "+word+" in this line")
    except Exception as e:
        print(e)
        scribe_speaks("No such line")
    return FULL_STOP.join(answer)

def add_line(answer, index = None, append = False):
    answer = answer.split(FULL_STOP)
    while True:
        scribe_speaks("Speak line to be added!")
        addline = get_audio()
        if addline!=FAILED_AUDIO_SYM:
            if index!=None:
                if append == False:
                    answer.insert(index-1,super_punc(addline))
                else:
                    answer[index-1] += str(" "+super_punc(addline))
            else:
                answer.append(super_punc(addline))
            scribe_speaks("line added was : "+super_punc(addline))
            break
    return FULL_STOP.join(answer)

def del_answer():
    scribe_speaks("Are you sure? Deleting will permanently remove the answer")
    choice = get_audio(5)
    if "no" in choice.lower():
        scribe_speaks("Cancelled deletion")
        return 0
    scribe_speaks("Deleted successfully")
    return 1

def thread_function():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_name = socket.gethostname()
    print(host_name)
    host_ip = socket.gethostbyname(host_name)
    print(host_ip)
    port = 5001
    socket_address = (host_ip,port)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(socket_address)
    server_socket.listen(5)
    while True:
        client_socket,addr = server_socket.accept()
        print("client_socket :"+str(client_socket))
        print("addr :"+str(addr))
        if client_socket:
            vid = cv2.VideoCapture(0)
            print(vid.isOpened())
            while(vid.isOpened()):
                try:
                    img,frame = vid.read()
                    # print("Before : "+sys.getsizeof(frame))
                    frame = imutils.resize(frame,width=320)
                    # print("After : "+sys.getsizeof(frame))
                    a = pickle.dumps(frame)
                #compressed = lz4.frame.compress(frame)
                #print(len(compressed))
                #print(len(a))
                    message = struct.pack("Q",len(a))+a
                #client_socket.sendall(message)
                    client_socket.sendall(message)
                #client_socket.sendall(compressed)
                except Exception as e:
                    print(e)
                    break
            print("here")
    client_socket.close()
    print("done-with-thread")

def get_question_paper_and_store():

    questions_db_client = pymongo.MongoClient(mongoURL)
    questions_db = questions_db_client[MONGO_DB]
    questions_collection = questions_db[MONGO_COLL]
    
    qp = questions_collection.find_one({"subject":{"$exists":True}})
    paper_object = Paper(subject=qp.get('subject'),total_time=qp.get('total_time'),total_marks=qp.get('total_marks'),start_time=datetime.datetime.now())
    db.session.add(paper_object)
    db.session.commit()

    questions = questions_collection.find({"subject":{"$exists":False}})
    for i in questions:
        question_no = int(i.get('QNo'))
        question_type = i.get('type')
        marks_alloted = int(i.get('marks'))
        question = i.get('question')
        parent_qpaper_id = paper_object.id
        db.session.add(Element(question_no=question_no,question_type=question_type,marks_alloted=marks_alloted,question=question,parent_qpaper_id=parent_qpaper_id))
        db.session.commit()

        if question_type == MCQ_QUESTION_TYPE:
            options = i.get('options')
            for option_name in options:
                db.session.add(MCQ_OP(option_name=option_name,parent_question_no=question_no))
        db.session.commit()

    return paper_object.id

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return (int(hour),int(minutes),int(round(seconds)))

def upload_to_cloud(subject,student_id='1MS17CS067'):
    date = (datetime.datetime.utcnow())[0:9]
    storage.child(path_on_cloud.format(subject,date,student_id,PDF_XTN)).put(path_local.format(STUDENT_RESPONSE,PDF_XTN))  

'''-----ACTION-DEFINITIONS----------------------------------------------------------------------------------------------------------'''

def go_to_question_num(q_no,entities):
    try:
        question_no = entities[0].get('value')
        print(question_no)
        if question_no == 'next': 
            question_no=int(q_no)+1
        elif question_no == 'previous':
            question_no=int(q_no)-1
        question_element = Element.query.get(int(question_no))
        scribe_speaks(NAVIGATE_TO_QUESTION.format(question_element.question_no,question_element.question))
        if (Element.query.get(int(question_no)).question_type == MCQ_QUESTION_TYPE): read_options(question_no) # Put this in a new intent
        return question_element
    except Exception as e:
        print(e)
        scribe_speaks(UNAVAILABLE_Q)

def read_options(q_no,entities=None):
    try:
        options = Element.query.get(q_no).mcq_options
        if entities != None and len(entities) > 0:
            print(entities[0])
            option_no = int(entities[0].get('value'))
            print(option_no,options)
            if option_no in range(1,len(options)):
                scribe_speaks(EACH_OPTION.format(option_no, options[option_no-1].option_name))
            else:
                scribe_speaks(UNAVAILABLE_OP)
        else:
            scribe_speaks(READING_OPTIONS)
            print(q_no, len(options))
            for i in range(len(options)):
                scribe_speaks(EACH_OPTION.format(i+1, options[i].option_name))
    except Exception as e:
        print(e)
        scribe_speaks(UNAVAILABLE_OP)

def set_all_options_False(q_no):
    for i in Element.query.get(q_no).mcq_options:
        i.isSelected = False
    db.session.commit()

def getWordNum(text):
    for k,v in numTonum.items():
        if v in text:
            return k
    return None

def choose_option(q_no):
    try:
        choice = get_audio(5)
        element = Element.query.get(q_no)
        options = element.mcq_options
        propNum = getWordNum(choice)
        option_no = propNum if propNum!=None else int(re.findall(r'\d+',choice).pop())
        if option_no in range(1,len(options)+1):
            set_all_options_False(q_no)
            element.mcq_options[option_no-1].isSelected = True
            db.session.commit()
            scribe_speaks(SELECTED_OPTION.format(option_no,element.mcq_options[option_no-1].option_name))
            return element
        else:
            raise Exception("No appropriate option selected")
    except Exception as e:
        print(e)
        scribe_speaks("No appropriate option selected")

def dictate_answer(q_no,entities):
    element = Element.query.get(q_no)
    if element.question_type == MCQ_QUESTION_TYPE:
        scribe_speaks("Choose option!")
        choose_option(q_no) # db update is handled within the function
    else:
        answer = write_answer()
        element.subjective_answer = answer
        db.session.commit()
    return element

def get_selected_option(options):
    selected_option = "NO OPTION SELECTED"
    for i in options:
        if i.isSelected:
            return i.option_name
    return selected_option

def terminate_exam_session(q_no,entities):
    scribe_speaks("Thanks for writing the paper.")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
    for x in Element.query.all():
        q_no = x.question_no
        question = x.question
        solution = ( UNANSWERED if x.subjective_answer==None else x.subjective_answer ) if x.question_type != MCQ_QUESTION_TYPE  else get_selected_option(x.mcq_options)
        
        pdf.multi_cell(200, 10, txt = SINGLE_RESPONSE_FORMAT.format(q_no,question,solution),  align = 'L')
    pdf.output(STUDENT_RESPONSE+PDF_XTN)
    try:
        # upload_to_cloud(Paper.query.get(1).subject)
        Paper.query.delete()
        Element.query.delete()
        MCQ_OP.query.delete()
        db.session.commit()
    except Exception as e:
        print(e)


def read_question(q_no,entities):
    element = Element.query.get(q_no)
    scribe_speaks(READ_QUESTION.format(q_no,element.question))

def read_answer(q_no,entities):
    element = Element.query.get(q_no)
    if element.question_type == MCQ_QUESTION_TYPE:
        scribe_speaks("Option chosen : "+get_selected_option(element.mcq_options))
    else:
        # flag_ind = 0
        answer = copy.deepcopy(element.subjective_answer)
        answer = answer.split(FULL_STOP)
        scribe_speaks("Reading...")
        j = 0
        for i in range(len(answer)):
            if len(answer[i])!=FAILED_AUDIO_SYM:
                scribe_speaks("Line "+str(j+1)+": "+answer[i])
                j+=1
                # stop = get_audio(5,True)
                # if stop!=FAILED_AUDIO_SYM and ("stop" in stop):
                #     # flag_ind = i+1
                #     break
        # return flag_ind   #AutoMatic deletion till flag_ind indexed line [DISABLED NOW]

def time_left(q_no,entities):
    start_time = Paper.query.get(1).start_time
    curr_time = datetime.datetime.now()
    total_time = Paper.query.get(1).total_time
    diff = curr_time - start_time
    diff_in_secs = (total_time*60) - diff.total_seconds()

    if (diff_in_secs > 0):
        H,M,S = convert(diff_in_secs)
        time_rem = 'Time remaining is '
        if H != 0:
            time_rem += '{0} hours, '.format(H)
        if M != 0:
            time_rem += '{0} minutes, '.format(M)
        if S != 0:
            time_rem += '{0} seconds '.format(S)
        scribe_speaks(time_rem)
    else:
        scribe_speaks(TIMEOUT)

def edit_answer(q_no,entities):
    try:
        element = Element.query.get(q_no)
        if element.question_type == MCQ_QUESTION_TYPE:
            scribe_speaks("Option chosen : "+get_selected_option(element.mcq_options))
            scribe_speaks("Choose new option!")
            choose_option(q_no)
            return element
        scribe_speaks("Edit a line or complete answer")
        sub_choice = get_audio(5).lower()
        answer = element.subjective_answer
        if "line" in sub_choice:
            ln=-1
            while True:
                scribe_speaks("Specify line number")
                line_no_choice = get_audio(3)
                ln = int(re.findall(r'\d+',line_no_choice).pop())
                if ln!=None and ln!=0 and ln!=FAILED_AUDIO_SYM:
                    break
                else:
                    scribe_speaks(AUDIO_NOT_RECOGNISED)
            while True:
                scribe_speaks("Read line {0}  or Add before line {0} or Append to line {0} or Remove line {0} or delete line after a word or exit".format(ln))
                sub_choice = get_audio(5).lower()

                if "read" in sub_choice:
                    read_line(answer,ln)
                elif "remove" in sub_choice:
                    answer = erase_line(answer, ln)
                elif "delete" in sub_choice or "word" in sub_choice:
                    while True:
                        scribe_speaks('Specify word')
                        word = get_audio(5)
                        if word!=FAILED_AUDIO_SYM:
                            answer = erase_till_word(answer,ln,word)
                            #app.logger.info("----------\n"+answer+"\n--------------")
                            break
                        else:
                            scribe_speaks(AUDIO_NOT_RECOGNISED)
                elif "add" in sub_choice:
                    answer = add_line(answer, ln)
                    #app.logger.info("----------\n"+answer+"\n--------------")
                elif "append" in sub_choice:
                    answer = add_line(answer,ln,True)
                    #app.logger.info("----------\n"+answer+"\n--------------")
                elif EXIT_CMD in sub_choice.lower():
                    break
        elif "complete" in sub_choice:
            while True:
                scribe_speaks("delete answer or append to answer or exit")
                sub_choice = get_audio(5).lower()
                if 'delete' in sub_choice.lower():
                    if del_answer()==1:
                        answer = write_answer()
                    break
                elif 'append' in sub_choice.lower():
                    answer = add_line(answer)
                    break
                elif 'exit' in sub_choice.lower():
                    break
                scribe_speaks(AUDIO_NOT_RECOGNISED)
        else:
            scribe_speaks(TRY_AGAIN)
        element.subjective_answer = answer
        db.session.commit()
        return element
    except:
        scribe_speaks(RESOURCE_UNAVAILABLE)

def fetch_marks(q_no,entities):
    marks_alloted = Element.query.get(q_no).marks_alloted
    scribe_speaks("Marks Alloted : {0}".format(marks_alloted))

def fetch_total_marks(q_no,entities):
    total_marks = Paper.query.get(1).total_marks
    scribe_speaks("Total Marks : {0}".format(total_marks))

'''---ACTIONS-FOR-INTENTS----------------------------------------------------------------------------------------------------------------'''

actionOnIntent = {
    'question'  :   go_to_question_num,
    'answer'    :   dictate_answer,
    'finish'    :   terminate_exam_session, 
    'read_answer'  :   read_answer,
    'read_question'  :   read_question,
    'read_option' : read_options,
    'time'  :   time_left,
    'edit'  :   edit_answer,
    'marks' :   fetch_marks,
    'total_marks' : fetch_total_marks
    # 'mark'  :   mark_for_review,
    # 'unmark':   unmark_from_review,
}