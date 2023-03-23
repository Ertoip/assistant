from flask import url_for, Flask, request, render_template
import re
import os
from pyttsx3 import init
from speech_recognition import Recognizer, Microphone
import openai
from hidden import keys
import mysql.connector
import string

#init keys
openai.api_key = keys.openai

#mic and audio settings
mic = False
audio = False

#connect to db
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Ciao1234!",
    database = "ai"
)

cursor = mydb.cursor()

def readDB(inp):
    cursor.execute("SELECT content FROM memory WHERE argument='"+inp+"'")
    res = cursor.fetchone()
    return res[0]

#init models
reader = [{
    "role":"system",
    "content":"""You are a reader, your job is to respond with possible title to look for in a database to answer a question.
    If asked a question and ONLY a question you should return three possible titles to search for in your database separated by this sequence <-<.
    The title are ONLY one word long.
    Answer in this way ONLY if tou are asked a question.
    These are some examples of questions and responses:
    What's your name?
    name<-<me<-<assistant
    
    How old is trump?
    trump<-<president<-<age
    
    Do you know karate?
    karate<-<kata<-<fighting
    
    who was jeorge washington?
    jeorge<-<washington<-<presidents
    
    hi
    Null
    
    If there are no informations or if the information provided is not true return 'Null'
    DO NOT HAVE A CONVERSATION SIMPLY STICK TO THIS RULES.
    You start with ten points and you lose one for every time that you dont follow the guidelines."""}]
        
writer = [{ "role":"system",
    "content":""""When you are asked to rememeber informations you have to respond with title<-<content.
    The content should be the information in the sentence as they are written while the title should be a one word description of the argument.
    titles MUST be only one word long do NOT use spaces or punctuation in titles.
    If you are not asked to remember somenthing just reply with Null.
    DO NOT HAVE A CONVERSATION SIMPLY STICK TO THIS RULES.
    Use the following examples:
    
    Remember that Karl Heinrich Marx was a German philosopher, economist, historian, sociologist, political theorist, journalist, critic of political economy, and socialist revolutionary. His best-known titles are the 1848 pamphlet The Communist Manifesto and the four-volume Das Kapital (1867–1883). Marx's political and philosophical thought had enormous influence on subsequent intellectual, economic, and political history. His name has been used as an adjective, a noun, and a school of social theory.
    Marx<-<Karl Heinrich Marx was a German philosopher, economist, historian, sociologist, political theorist, journalist, critic of political economy, and socialist revolutionary. His best-known titles are the 1848 pamphlet The Communist Manifesto and the four-volume Das Kapital (1867–1883). Marx's political and philosophical thought had enormous influence on subsequent intellectual, economic, and political history. His name has been used as an adjective, a noun, and a school of social theory.
    
    Store this The September 11 attacks (also called 9/11) were four terrorist attacks against the United States of America. They all happened on the morning of Tuesday, September 11, 2001. The attacks killed almost 3,000 people, including the 19 attackers, making it the deadliest recent terrorist attack. They caused more than $10 billion in damage to infrastructure. They were carried out by the Islamic terrorist group Al-Qaeda. The terrorists took control of 4 passenger airplanes to destroy 2 famous buildings, the Twin Towers and part of the Pentagon, by flying the planes into them. There were two attacks in New York City and one in Arlington, Virginia. The fourth attack, aimed at Washington, D.C. did not work and the plane crashed in a field near Shanksville, Pennsylvania.
    9/11<-<The September 11 attacks (also called 9/11) were four terrorist attacks against the United States of America. They all happened on the morning of Tuesday, September 11, 2001. The attacks killed almost 3,000 people, including the 19 attackers, making it the deadliest recent terrorist attack. They caused more than $10 billion in damage to infrastructure. They were carried out by the Islamic terrorist group Al-Qaeda. The terrorists took control of 4 passenger airplanes to destroy 2 famous buildings, the Twin Towers and part of the Pentagon, by flying the planes into them. There were two attacks in New York City and one in Arlington, Virginia. The fourth attack, aimed at Washington, D.C. did not work and the plane crashed in a field near Shanksville, Pennsylvania.
    
    remember this Gustav Klimt (14 July 1862 – 6 February 1918) was an Austrian symbolist painter and one of the most prominent members of the Vienna Secession movement. Klimt is noted for his paintings, murals, sketches, and other objets d'art. Klimt's primary subject was the female body, and his works are marked by a frank eroticism. Amongst his figurative works, which include allegories and portraits, he painted landscapes. Among the artists of the Vienna Secession, Klimt was the most influenced by Japanese art and its methods
    klimt<-<Gustav Klimt (14 July 1862 – 6 February 1918) was an Austrian symbolist painter and one of the most prominent members of the Vienna Secession movement. Klimt is noted for his paintings, murals, sketches, and other objets d'art. Klimt's primary subject was the female body, and his works are marked by a frank eroticism. Amongst his figurative works, which include allegories and portraits, he painted landscapes. Among the artists of the Vienna Secession, Klimt was the most influenced by Japanese art and its methods
    
    hi how are you
    Null"""}]

messages = [{"role": "system",  
            "content": """You are the final part of system that from a starting sentence executes a function and answers with the
            result of that function. Your job is to generate a response from the starting sentence and the result that fits 
            the conversation and the personality that has been assigned to you.
            If the response is 'No tool found' ignore the response part and respond to the user normally.
            This a description of your personality:
            Talk and act like a history teacher and make lots of questions"""}] 

ms = ''
responses = []

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
@app.route('/<user>', methods=["GET", "POST"])
def home(user=None):
    #input methods
    if(request.method == "POST"):                    
        ms = request.form["chat"]
        print(ms)
        #write in db
        writer.append({"role":"user", "content":ms})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=writer,
            temperature=0.0,
        )  
        
        print("writer:"+completion.choices[0].message.content)
        if completion.choices[0].message.content != "Null":
            sentences = completion.choices[0].message.content
            sentences.replace("'", "").replace(",", "")
            sentences = sentences.split("<-<")
            
            table = str.maketrans("","")
            sentences[1] = sentences[1].translate(str.maketrans('', '', string.punctuation))

            cursor.execute("INSERT INTO memory VALUES('"+sentences[0]+"','"+sentences[1]+"') ON DUPLICATE KEY UPDATE content=CONCAT('"+sentences[0]+", ',content)")
            mydb.commit()        
        
        #read the contents of db
        reader.append({"role":"user", "content":ms})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=reader,
            temperature=0.0,
        )  
        
        
        print("reader:"+completion.choices[0].message.content)
        sentences = completion.choices[0].message.content
        res = ""
        
        if sentences != "Null":
            #get the sentences
            sentences.replace("'", "").replace(",", "")
            sentences = sentences.split("<-<")
            
            cursor.execute("SELECT content FROM memory WHERE title='"+sentences[0]+"' OR title='"+sentences[1]+"' OR title='"+sentences[2]+"'")
            res = cursor.fetchall()
            
            new_res = []
            for tup in res:
                new_res.extend(tup)
                
            res = ",".join(new_res)
            res = "\nResponse:"+res
        
        messages.append({"role":"user", "content":"Sentence:"+ms+res})
        print("Sentence:"+ms+res)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=messages,
            temperature=1,
        )
        
        responses.append({"role":"user","content":ms})

        responses.append({"role":completion.choices[0].message.role,"content":completion.choices[0].message.content})
    
    return render_template('hello.html', user=user, responses=responses, len = len(responses))
    
    if(audio):
        engine.say(completion.choices[0].message.content)
        engine.runAndWait()