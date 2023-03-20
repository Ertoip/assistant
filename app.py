from flask import url_for, Flask, request, render_template

import os
import openai
import datetime
import wikipedia
from pyttsx3 import init
from speech_recognition import Recognizer, Microphone
from langchain import OpenAI, LLMMathChain
from langchain.utilities import PythonREPL
import openai
from hidden import keys

#init keys
os.environ["OPENAI_API_KEY"] = keys.openai
openai.api_key = keys.openai

#mic and audio settings
mic = False
audio = False

#langchain
llm = OpenAI(temperature=0)
llm_math = LLMMathChain(llm=llm, verbose=True)
python_repl = PythonREPL()

def execute(fun, arg):
    for i in tools:
        if i.name.lower() == fun.lower() and i.name.lower() != "none":
            if arg == "None":
                arg == None
            return i.function(arg)
    return "No tool found"

toolsText = ""

for i in tools:
    toolsText += i.name+": "+i.description+"\n"

#init models

splitter = [{
    "role":"system",
    "content":"""You are a splitter, your job is, given a sentence, to split it in the actions necessary to get the result or to simplify the frase to the basic action you need to do.
    If the sentence does not make sense to you or if you cant split it respond with the sentence itself.
    DO NOT ANSWER THE QUESTIONS IN THE SENTENCES.
    here there are some examples:
    
    Multiply the age of obama by 62
    I need to know the age of obama,I need to multiply the result by 62
    
    Tell me the time and the temperature in singapore and put it in a table
    I need to know the time singapore,I need to know the temperature in singapore,I need to make a table with the time and the temperature of singapore
    
    What time is it?
    I need to know the current time
    
    che giorno è oggi?
    Devo sapere la data di oggi"""}]

messages = [{"role": "system",  
            "content": """You are the final part of system that from a starting sentence executes a function and answers with the
            result of that function. Your job is to generate a response from the starting sentence and the result that fits 
            the conversation and the personality that has been assigned to you.
            If the response is 'No tool found' ignore the response part and respond to the user normally.
            This a description of your personality:
            Your name is mario you speak only italian and you love pasta pizza and mandolino"""}] 

ms = ''
responses = []

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
@app.route('/<user>', methods=["GET", "POST"])
def home(user=None):
    #input methods
    if(request.method == "POST"):
        print("start")
                    
        ms = request.form["chat"]
        print("chat")
        splitter.append({"role":"user", "content":"Sentence:"+ms})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=splitter,
            temperature=0.0,
        )  
        
        print(completion.choices[0].message.content)
        sentences = completion.choices[0].message.content
        #get the sentences
        sentences = sentences.split(",")
        res = ""
            
        #for every action sentence execute a tool
        for sentence in sentences:
            #explain to the model the result and the sentence to think about
            classifier.append({"role":"user", "content":res+"Sentence:"+sentence})
            
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=classifier,
                temperature=0.0,
            )    
                    
            print("Thought: "+completion.choices[0].message.content)
            
            args = completion.choices[0].message.content.split(',')
            
            try:
                args[0]=args[0].lower().replace("tool:", "")
                args[1]=args[1].lower().replace("params:", "")
            except:
                print("non trovato")
                
            try:
                args[1] = args[1:]
                del args[2:]
            except:
                args[1] = args[1]
            print(args)
            
            try:
                res = "Result:"+execute(args[0], args[1])+","
            except:
                res = "Not found"
        
        messages.append({"role":"user", "content":"Sentence:"+ms+"\n"+res})
        print("Sentence:"+ms+"\n"+res)
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