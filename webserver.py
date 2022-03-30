from flask import Flask,request

from threading import Thread




app = Flask('')



@app.route('/',methods=["GET","POST"])
def home():

  if request.method == "POST":

    print("there was a post?")

    return "I'm alive"

  



def run():

  app.run(host='0.0.0.0',port=8080)



def keep_alive():  

    t = Thread(target=run)

    t.start()