# V-Scribe
<b>Exam virtual assistant for the specially abled</b><br>
A Virtual Scribe for helping out visually impaired in writing their exams.<br>

Once the repository has been cloned to local device, perform following steps :<br>

1> Go the folder containing all the files and folders.<br>
2> Open terminal or command prompt in that directory.<br>
3> Install all required python dependencies.<br>
4> Run 'python app2.py' to run the flask server.<br>
5> Go to 'localhost:3000/verify' in your web browser.<br>
6> Click on the 'VSCRIBE' logo to skip the face recognition part and go to question.<br>
7> Click anywhere on the screen to start the assistant.<br>
8> Speak commands like 'Go to question one' or 'read answer' or 'answer this question'.<br>

In order to understand more about the functioning of the application, you can watch the following video:
https://www.youtube.com/watch?v=3-dK5BlAyW8&feature=youtu.be

rasa run --enable-api -m /models/nlu-20210520-193828.tar.gz
