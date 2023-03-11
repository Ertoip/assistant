import os
import openai
import datetime
import wikipedia
from pyttsx3 import init
from speech_recognition import Recognizer, Microphone
from langchain import OpenAI, LLMMathChain
from langchain.utilities import PythonREPL

#init keys
openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"

mic = False
audio = False

#langchain
llm = OpenAI(temperature=0)
llm_math = LLMMathChain(llm=llm, verbose=True)
python_repl = PythonREPL()

#init speech and voice recognition
engine = init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[36].id)#16 #36
r = Recognizer()

#init tools for ai
class tool:
    def __init__(self, name, function, description):
        self.name = name
        self.function = function
        self.description = description
        
def time(*args):
    now = datetime.datetime.now()
    time = now.time()
    return str(time)[:str(time).find(".")]

def math(arg):
    return llm_math.run(arg[0])

def wikiSearch(arg):
    search = wikipedia.search(arg[0], results = 1)
    return wikipedia.summary(search[0])

def pythonRepl(arg):
    return python_repl.run(arg[0])

def writefile(filename: str=None) -> str:
    title = filename[0]
    content = ",".join(filename[1:])
    f = open(title , "w")
    
    c = f.write(str(content))
    
    if c:
        f.close()
        return f'File was written'
    
def readfile(filename: str=None) -> str:
    try:
        f = open(filename[0], "r")
    except:
        return "File not found"
    content = f.read()
    
    if content:
        f.close()
        return f'In the file was written this: {content}'

tools = [
    tool("time", time, "useful when you need to know the current time"),
    tool("math", math, "useful when you need to solve calculations of any type it require only one argument wich is the mathematical operation written with math symbols. multiply 2 by 2 should become 2*2"),
    tool("search", wikiSearch, "Useful for when you have to answer questions about historic, literary and artistic facts"),
    tool("read", readfile, "Allows you to read the content of a file given the filename"),
    tool("write", writefile, "Allows you to write text or code into a file given the filename and the content of the file as params, for example if i say write a code in file.py you should write the code in that file"),
]

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

print(toolsText)

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
    I need to know the current time"""}]

classifier = [{
    "role":"system",
    "content":"""Your job is understanding from the parameter 'Sentence' if among the tools you
            have at your disposal there is one that can be useful for executing the task requested in 
            the sentence and if there is a request in the first place, 
            you should only respond in this format and nothing more:
            tool:name of the tool, params: params that must be passed split them with this ,,
            this is an example of your job:
            
            I need to know the age of obama.
            tool:search,params:age of obama
            
            Response:61, I need to multiply the result by 4
            tool:math,params:61*4
            
            If the tool search does not appear in the list you or if you've finished you should instead say:
            tool:None,params:None
            
            List of tools:
            """+toolsText
}]

messages = [{"role": "system",  
            "content": """You are the final part of system that from a starting sentence executes a function and answers with the
            result of that function. Your job is to generate a response from the starting sentence and the result that fits 
            the conversation and the personality that has been assigned to you.
            If the response is 'No tool found' ignore the response part and respond to the user normally.
            This a description of your personality:
            You dont have anything special respond like chat gpt"""}] 

ms = ''

while(ms != "quit"):
    #input methods
    if(mic):
        try:
            with Microphone() as source:
                print("Ascolto...")
                a = r.listen(source, timeout=10, phrase_time_limit=5,)
                ms = r.recognize_google(a, language="it-IT", show_all=False)#en-US it-IT
                print(ms)
        except:
            break
    else:
        ms = input("\nUser:")

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
            
        args[1] = args[1:]
        del args[2:]
        
        print(args)
        
        try:
            res = "Result:"+execute(args[0], args[1])+","
        except:
            print("not found")
        print(res)
    
    messages.append({"role":"user", "content":"Sentence:"+ms+"\n"+res})
    print("Sentence:"+ms+"\n"+res)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=messages,
        temperature=1,
    )
    
    print(completion.choices[0].message.role+": "+completion.choices[0].message.content)
    
    if(audio):
        engine.say(completion.choices[0].message.content)
        engine.runAndWait()