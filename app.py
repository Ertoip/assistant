from flask import url_for, Flask, request, render_template
import openai
openai.api_key = "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"

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
        response = completion.choices[0].message.content
        
    return render_template('hello.html', user=user, response=response)
