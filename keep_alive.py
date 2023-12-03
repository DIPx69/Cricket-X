from flask import Flask,jsonify
from threading import Thread
import time
import logging
app = Flask('')
uptime_start = time.time()
@app.route('/')
def uptime():
    uptime_seconds = int(time.time() - uptime_start)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    if days > 0:
       uptime_text = f"{days}d:{hours}h:{minutes}m:{seconds}s"
    else:
       uptime_text = f"{hours}h:{minutes}m:{seconds}s"
    return jsonify({'uptime': uptime_text})
def run():
  log = logging.getLogger('werkzeug')
  log.disabled = True   
  app.logger.disabled = True
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()
