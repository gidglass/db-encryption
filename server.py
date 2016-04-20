from flask import Flask, request
from database import Database
import pymysql
import json
from fernet2 import Fernet2

app = Flask(__name__)

# CONFIG
with open('config.json', 'r') as f:
  config = json.load(f)
  SECRET_KEY = config['secret'].encode('utf-8')
  ASSOCIATED_DATA = config['associated_data'].encode('utf-8')
  ENCRYPTED_COLS = set(config['encrypted_cols'])
f.close()

def _encrypt (fields):
  fn = Fernet2(SECRET_KEY)
  result = {}
  for k, v in fields.iteritems():
    if k in ENCRYPTED_COLS:
      result[k] = fn.encrypt(str(v).encode('utf-8'), ASSOCIATED_DATA)
    else:
      result[k] = str(v).encode('utf-8')
  return result

def _decrypt (fields):
  fn = Fernet2(SECRET_KEY)
  result = {}
  for k, v in fields.iteritems():
    if k in ENCRYPTED_COLS:
      result[k] = fn.decrypt(str(v).encode('utf-8'), ASSOCIATED_DATA)
    else:
      result[k] = str(v).encode('utf-8')
  return result

@app.route('/table', methods = ['POST'])
def create_table ():
  db = Database(
    host = 'localhost', 
    username = 'student', 
    password = 'Password123!',
    db = 'sample')

  response = request.get_json()
  
  db.create_table(response['schema'])

  return "CREATED NEW TABLE: %s" % json['schema']['table']

@app.route('/insert', methods = ['POST'])
def insert_row ():
  db = Database(
    host = 'localhost', 
    username = 'student', 
    password = 'Password123!',
    db = 'sample')

  response = request.get_json()
  log = []
  
  for entry in response:
    entry['row']['fields'] = _encrypt(entry['row']['fields'])
    db.insert(entry['row'])
    log.append("INSERTED NEW ROW: %s into %s" % (str(entry['row']['fields']), str(entry['row']['table'])))

  return str(log)

@app.route('/query', methods = ['POST'])
def query ():
  db = Database(
      host = 'localhost', 
      username = 'student', 
      password = 'Password123!',
      db = 'sample')

    # sample_query_json = {
    #   "query": {
    #     "table": "EMPLOYEE",
    #     "cols": ["AGE", "INCOME"],
    #     "fields": {
    #       "FIRST_NAME": "Gideon",
    #       "LAST_NAME": "Glass"
    #     }
    #   }
    # }

  response = request.get_json()
  log = []

  for entry in response:
    cols = entry['query']['cols']
    raw_results = db.select(entry['query'])
    json_results = [dict(zip(cols, row)) for row in raw_results]
    decrypted = [_decrypt(entry) for entry in json_results]
    log.append(decrypted)

  return "RESULTS: " + str(log)

if __name__ == '__main__':
    app.run(debug=True)