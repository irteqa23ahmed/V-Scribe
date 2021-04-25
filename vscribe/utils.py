from vscribe import app
import requests
import speech_recognition as sr
import playsound
from pygame import mixer
from gtts import gTTS

from io import BytesIO,StringIO
from tempfile import TemporaryFile
import re,time,os

punctuationURL = "http://bark.phon.ioc.ee/punctuator"

def scribe_speaks(output):
    ts = time.time()
    app.logger.info("V-Scribe : ", output)
    toSpeak = gTTS(text=output, lang='en-US', slow=False)
    file = str(ts)+".mp3"
    toSpeak.save(file)
    playsound.playsound(file, True)
    os.remove(file)
    
def punc(text):
    payload = {"text" : text}
    response = requests.post(punctuationURL, data=payload)
    return response.text

def super_punc(ans):
    try:
        ans = punc(ans)
    except:
        scribe_speaks("Cannot punctuate answer")
    return ans

def get_audio(time_limit = None,isstop = False):
    r = sr.Recognizer()
    audio = ''
    with sr.Microphone() as source:
        app.logger.info("Begin speaking")
        audio = r.listen(source, phrase_time_limit=time_limit)
    app.logger.info("Stop speaking")
    try:
        text = r.recognize_google(audio,language='en-US')
        app.logger.info("You : ", text)
        return text
    except:
        if isstop == False:
            scribe_speaks("Could not understand your audio, PLease try again!")
        return '0'

def read_question(question,num):
    app.logger.info("entered")
    if num == "3":
        app.logger.info("entered if")
        scribe_speaks("The question is Tomato is a fruit and your options are option A true and option B false")
    else:
        scribe_speaks("Reading question number "+str(num)+" \n"+question)

def read_answer(answer,qon=None):
    if qon != None:
        scribe_speaks("Option chosen : "+answer)
    else:
        flag_ind = 0
        app.logger.info(answer)
        answer = answer.split(".")
        scribe_speaks("Reading...")
        j = 0
        for i in range(len(answer)):
            if len(answer[i])!=0:
                scribe_speaks("Line "+str(j+1)+": "+answer[i])
                j+=1
                stop = get_audio(5,True)
                if stop!=0 and ("stop" in stop):
                    flag_ind = i+1
                    break
        return flag_ind

def read_line(answer,line):
    answer = answer.split(".")
    scribe_speaks("Reading...line "+str(line))
    scribe_speaks(answer[line-1])

def choose_answer():
    scribe_speaks("Enter your option")
    choice = get_audio(5)
    if "option A" in choice:
        scribe_speaks("option A selected")
        return "option A"
    elif "option B" in choice:
        scribe_speaks("option B  selected")
        return "option B"
    else:
        scribe_speaks("No appropriate option selected")
        return ""

def write_answer():
    final_dict_ans = ""
    flag = 1
    while flag==1:
        scribe_speaks("You may start dictating the answer now!")
        dict_ans = get_audio()
        if dict_ans!=0:
            final_dict_ans += super_punc(dict_ans)
            scribe_speaks("your answer is recorded successfully")
            # app.logger.info("Wait! last word recorded is "+dict_ans.split()[-1]) #Remove
            # scribe_speaks("Wait, last word recorded is "+dict_ans.split()[-1])
            while True:
                scribe_speaks("Do you wish to continue?")
                choice = get_audio(5)
                if choice!=0:
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
                        scribe_speaks("Didn't get you there, try again!")
    return final_dict_ans

def point_wise_answer(ans):
    scribe_speaks("dictate point wise...")
    line_num = 0
    same = False
    while True:
        scribe_speaks("Dictate Point ")
        dict_ans = get_audio()
        if dict_ans!=0:
            if same == False:
                line_num+=1
                ans += '&#13;&#10;'+str(line_num)+") "
            ans += super_punc(dict_ans)
            scribe_speaks("your point is recorded successfully")
            # scribe_speaks("Wait, last word recorded for point "+str(line_num)+" is "+dict_ans.split()[-1])
            while True:
                scribe_speaks("continue point? or next point? or para mode? or exit")
                choice = get_audio(5)
                if choice!=0:
                    if "continue" in choice.lower():
                        same = True
                        break
                    elif "next" in choice.lower():
                        same = False
                        break
                    elif "para" in choice.lower():
                        app.logger.info(ans)
                        return [ans,'yes']
                    elif "exit" in choice.lower():
                        app.logger.info(ans)
                        return [ans,'no']
                    else:
                        scribe_speaks("Didn't get you there, try again!")


def erase_line(answer, index):
    answer = answer.split(".")
    try:
        removed = answer[index-1]
        answer.pop(index-1)
        scribe_speaks("Removed line : "+removed)
    except:
        scribe_speaks("No such line")
    return ".".join(answer)

def erase_till_word(answer,index,word):
    answer = answer.split(".")
    try:
        removed = answer[index-1].split(" ")
        try:
            find = removed.index(word)
            answer[index-1] = re.sub(r''+word+'.*', word, answer[index-1])
            scribe_speaks("Updated answer")
        except:
            scribe_speaks("Could'nt find "+word+" in this line")
    except:
        scribe_speaks("No such line")
    return ".".join(answer)

def add_line(answer, index = None, append = False):
    answer = answer.split(".")
    while True:
        scribe_speaks("Speak line to be added!")
        addline = get_audio()
        if addline!=0:
            if index!=None:
                if append == False:
                    answer.insert(index-1,super_punc(addline))
                else:
                    answer[index-1] += str(" "+super_punc(addline))
            else:
                answer.append(super_punc(addline))
            scribe_speaks("line added was : "+super_punc(addline))
            break
    return ".".join(answer)

def del_answer():
    scribe_speaks("Are you sure? Deleting will permanently remove the answer")
    choice = get_audio(5)
    if "no" in choice.lower():
        scribe_speaks("Cancelled deletion")
        return 0
    scribe_speaks("Deleted successfully")
    return 1

def welcome():
    speak = "Hello, I am V-Scribe. Your personal scribe for this session."
    scribe_speaks(speak)