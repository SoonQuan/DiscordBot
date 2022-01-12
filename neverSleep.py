from flask import Flask
from threading import Thread
import random
import time
import requests
import logging
logging.basicConfig(filename="log.dat", filemode="a+",format='%(asctime)s: %(message)s', level=logging.WARNING)
logging.warn(str(time.strftime("%d-%b-%Y (%H:%M:%S)",time.gmtime(time.time()+28800))))
app = Flask('')
@app.route('/')
def home():
    return "You have found the home of a Python program!"

def run():
  app.run(host='0.0.0.0',port=random.randint(2000,9000)) 
def ping(target, debug):
    while(True):
        r = requests.get(target)
        if(debug == True):
            print("Status Code: " + str(r.status_code))
        time.sleep(random.randint(180,300)) #alternate ping time between 3 and 5 minutes
def awake(target, debug=False):  
    # log = logging.getLogger('werkzeug')
    # log.disabled = True
    # app.logger.disabled = True  
    b = "time now is: " + str(time.strftime("%d-%b-%Y (%H:%M:%S)",time.gmtime(time.time()+28800)))
    logging.warn(b)
    t = Thread(target=run)
    r = Thread(target=ping, args=(target,debug,))
    t.start()
    r.start()

