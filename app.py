from flask import url_for, Flask, request, render_template
import openai
openai.api_key = ""
responses = []
messages = [{"role": "system", "content": "You are al, an ai that has access to a collection of tools"}]

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
@app.route('/<user>', methods=["GET", "POST"])
def home(user=None):
    response=""

    
    if(request.method == "POST"):
        ms = request.form["chat"]
        messages.append({"role":"user", "content":ms})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=messages,
            temperature=0.8,
        )
        responses.append({"role":"user","content":ms})

        responses.append({"role":completion.choices[0].message.role,"content":completion.choices[0].message.content})
        
    return render_template('hello.html', user=user, responses=responses, len = len(responses))
