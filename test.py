from hidden import keys
import openai

#init keys
openai.api_key = keys.openai
argument = [{
    "role":"system",
    "content":"""When you are asked to rememeber informations you have to respond with title<-<content.
    The content should be the information in the sentence as they are written while the title should be a very short description of the content.
    If you are not asked to remember somenthing just reply with None.
    DO NOT HAVE A CONVERSATION SIMPLY STICK TO THIS RULES.
    Use the following examples:
    
    Remember that Karl Heinrich Marx was a German philosopher, economist, historian, sociologist, political theorist, journalist, critic of political economy, and socialist revolutionary. His best-known titles are the 1848 pamphlet The Communist Manifesto and the four-volume Das Kapital (1867–1883). Marx's political and philosophical thought had enormous influence on subsequent intellectual, economic, and political history. His name has been used as an adjective, a noun, and a school of social theory.
    Karl Marx<-<Karl Heinrich Marx was a German philosopher, economist, historian, sociologist, political theorist, journalist, critic of political economy, and socialist revolutionary. His best-known titles are the 1848 pamphlet The Communist Manifesto and the four-volume Das Kapital (1867–1883). Marx's political and philosophical thought had enormous influence on subsequent intellectual, economic, and political history. His name has been used as an adjective, a noun, and a school of social theory.
    
    Store this The September 11 attacks (also called 9/11) were four terrorist attacks against the United States of America. They all happened on the morning of Tuesday, September 11, 2001. The attacks killed almost 3,000 people, including the 19 attackers, making it the deadliest recent terrorist attack. They caused more than $10 billion in damage to infrastructure. They were carried out by the Islamic terrorist group Al-Qaeda. The terrorists took control of 4 passenger airplanes to destroy 2 famous buildings, the Twin Towers and part of the Pentagon, by flying the planes into them. There were two attacks in New York City and one in Arlington, Virginia. The fourth attack, aimed at Washington, D.C. did not work and the plane crashed in a field near Shanksville, Pennsylvania.
    9/11<-<The September 11 attacks (also called 9/11) were four terrorist attacks against the United States of America. They all happened on the morning of Tuesday, September 11, 2001. The attacks killed almost 3,000 people, including the 19 attackers, making it the deadliest recent terrorist attack. They caused more than $10 billion in damage to infrastructure. They were carried out by the Islamic terrorist group Al-Qaeda. The terrorists took control of 4 passenger airplanes to destroy 2 famous buildings, the Twin Towers and part of the Pentagon, by flying the planes into them. There were two attacks in New York City and one in Arlington, Virginia. The fourth attack, aimed at Washington, D.C. did not work and the plane crashed in a field near Shanksville, Pennsylvania.
    
    hi how are you
    None
    
    END OF INSTRUCTIONS"""}]

while 1:
    ms = input("User:")

    argument.append({"role":"user", "content":ms})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=argument,
        temperature=0.0,
    )  

    print(completion.choices[0].message.content)