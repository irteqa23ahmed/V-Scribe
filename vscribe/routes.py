from vscribe import app, mycol
from vscribe.utils import *
from flask import Flask,render_template,request,url_for,redirect,jsonify
import os,docx
#import cv2

@app.route('/brail',methods = ['GET'])
def braild():
    try:
        f  = open('answers.txt','r')
        str = f.read()
    except:
        str = "empty string"
    asciicodes = [' ','!','"','#','$','%','&','','(',')','*','+',',','-','.','/',
          '0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@',
          'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
          'r','s','t','u','v','w','x','y','z','[','\\',']','^','_']


    brailles = ['⠀','⠮','⠐','⠼','⠫','⠩','⠯','⠄','⠷','⠾','⠡','⠬','⠠','⠤','⠨','⠌','⠴','⠂','⠆','⠒','⠲','⠢',
        '⠖','⠶','⠦','⠔','⠱','⠰','⠣','⠿','⠜','⠹','⠈','⠁','⠃','⠉','⠙','⠑','⠋','⠛','⠓','⠊','⠚','⠅',
        '⠇','⠍','⠝','⠕','⠏','⠟','⠗','⠎','⠞','⠥','⠧','⠺','⠭','⠽','⠵','⠪','⠳','⠻','⠘','⠸']

    text = ""
    for i in str:
        if i != '\n':
            text += brailles[asciicodes.index(i.lower())]
    d = docx.Document()
    d.add_paragraph(str + "\n--------------------------------------------------------------------------------\n"+text)
    d.save('braille.docx')
    os.startfile(r'C:\Users\91930\Desktop\vscribe\vscribe\braille.docx')
    return render_template('test.htm')

@app.route('/end',methods = ['GET'])
def endf():
    #if request.method == 'GET':
    scribe_speaks("All the best for results")
    return render_template("test.htm")

@app.route('/error',methods = ['GET'])
def novery():
    #if request.method == 'GET':
    scribe_speaks("User not verified. Click Again to try verifying again.")
    return render_template("login.html")

@app.route('/',methods = ['GET','POST'])
def trial():
    welcome()
    return render_template('ques1.html')

@app.route('/verify',methods = ['GET','POST'])
def verify():
    if request.method == 'GET':
        scribe_speaks("Click anywhere to start the exam. All the best.")
        return render_template("login.html")
    else:
        # video_capture = cv2.VideoCapture(0)
        # # Check success
        # if not video_capture.isOpened():
        #     raise Exception("Could not open video device")
        #     # Read picture. ret === True on success
        # ret, frame = video_capture.read()
        # # Close device
        # video_capture.release()
        # frameRGB = frame[:,:,::-1] # BGR => RGB
        # cv2.imwrite('check.jpg',frameRGB)
        # known_image = face_recognition.load_image_file("realimage.jpg")
        # unknown_image = face_recognition.load_image_file("check.jpg")
        # app.logger.info("check1")
        # biden_encoding = face_recognition.face_encodings(known_image)[0]
        # app.logger.info("check2")
        # unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        # app.logger.info("check3")
        # results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
        # app.logger.info("res is ",results)
        # if results[0]:
        return jsonify({"res":"1"})
        # else:
        #     return jsonify({"res":"0"})


@app.route('/speech',methods = ['POST'])
def process_text():
    question = request.form["question"]
    q_no = request.form["qno"]
    answer = request.form["answer"]

    scribe_speaks("How can I help you?")
    choice = get_audio(8).lower()

    if "question 1" in choice:
        scribe_speaks("alright, going to question 1, question is , when did India get Independence")
        myquery={"qno":"1"}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            return jsonify({"qno":"1","question":"When did India get Independence","answer":x['answer'],"option1":"true","option2":"false"})
    elif "question 2" in choice:
        scribe_speaks("alright, going to question 2, question is, explain solar energy in points")
        myquery={"qno":"2"}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            return jsonify({"qno":"2","question":"Explain Solar energy in points","answer":x['answer'],"option1":"true","option2":"false"})
    elif "question 3" in choice:
        scribe_speaks("alright, going to question 3 the question is, Tomato is a fruit? and your options are option A true and option B false")
        myquery={"qno":"3"}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            return jsonify({"qno":"3","question":x['question'],"answer":x['answer'],"option1":"true","option2":"false"})

    elif "read" in choice and "answer" in choice:
        if q_no == '3':
            read_answer(answer,q_no)
        elif len(answer.split())==0:
            scribe_speaks("No answer to read")
        else:
            read_answer(answer)

    elif "read" in choice:
        read_question(question,q_no)

    elif "answer" in choice:
        if q_no == "3":
            scribe_speaks("Choose option!")
            answer = choose_answer()
        else:
            answer = write_answer()
        myquery = { "qno": q_no }
        newvalues = { "$set": { "answer": answer } }
        mycol.update_one(myquery, newvalues)
        resp = {"qno":q_no,"question":question,"answer":answer,"option1":"true","option2":"false"}
        return jsonify(resp)

    elif "edit" in choice:
        scribe_speaks("Edit a line or complete answer")
        sub_choice = get_audio(5).lower()

        if "line" in sub_choice:
            ln=-1
            while True:
                scribe_speaks("Specify line number")
                ln = [int(i) for i in get_audio(3).split() if i.isdigit()][0]
                if ln!=None and ln!=0:
                    break
                else:
                    scribe_speaks("Try again!")
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
                        if word!=0:
                            answer = erase_till_word(answer,ln,word)
                            app.logger.info("----------\n"+answer+"\n--------------")
                            break
                        else:
                            scribe_speaks("Try again!")
                elif "add" in sub_choice:
                    answer = add_line(answer, ln)
                    app.logger.info("----------\n"+answer+"\n--------------")
                elif "append" in sub_choice:
                    answer = add_line(answer,ln,True)
                    app.logger.info("----------\n"+answer+"\n--------------")
                elif "exit" in sub_choice.lower():
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
            resp = {"qno":q_no,"question":question,"answer":answer,"option1":"true","option2":"false"}
            return jsonify(resp)

        else:
            scribe_speaks("Didn't get you there, try again!")

    elif "finish paper" in choice:
        scribe_speaks("Thanks for writing the paper.")
        L = []
        file1 = open("answers.txt","w")
        for x in mycol.find():
            L.append('Q '+x['qno']+'> '+x['answer']+'\n\n')
        file1.writelines(L)
        file1.close() #to change file access modes
        return jsonify({"qno":"end"})

    else:
        scribe_speaks("Didn't get you there, try again!")
    myquery = { "qno": q_no }
    newvalues = { "$set": { "answer": answer } }
    mycol.update_one(myquery, newvalues)
    resp = {"qno":q_no,"question":question,"answer":answer,"option1":"true","option2":"false"}
    return jsonify(resp)