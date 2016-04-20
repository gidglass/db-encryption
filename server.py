from flask import Flask, request
from database import Database
import pymysql
from fernet2 import Fernet2
import os

app = Flask(__name__)

# TODO: ACTUAL KEY MANAGEMENT! THIS IS FOR TESTING...
SECRET_KEY = "Gb-xBmBDKrjs7AYkOkO4B8roifAG-PTvVp6m_D6SoAw="
ASSOCIATED_DATA = b"GIDEON_ROCKS"
ENCRYPTED_COLS = set(["SSN"])

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

  json = request.get_json()
  
  db.create_table(json['schema'])

  return "CREATED NEW TABLE: %s" % json['schema']['table']

@app.route('/insert', methods = ['POST'])
def insert_row ():
  db = Database(
    host = 'localhost', 
    username = 'student', 
    password = 'Password123!',
    db = 'sample')

  json = request.get_json()
  
  transaction_log = []
  
  for entry in json:
    entry['row']['fields'] = _encrypt(entry['row']['fields'])
    db.insert(entry['row'])
    log.append("INSERTED NEW ROW: %s into %s" % (str(entry['row']['fields']), str(entry['row']['table'])))

  return str(transaction_log)

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

  json = request.get_json()

  cols = json['query']['cols']
  raw_results = db.select(json['query'])

  json_results = [dict(zip(cols, row)) for row in raw_results]

  decrypted = [_decrypt(entry) for entry in json_results]


  # TODO: DECRYPT SENSATIVE JSON FIELDS HERE!!!
  # e.g. json['row']['fields']['FIRST_NAME'] = decrypt(key, data)

  # results = db.select(json['query'])  

  # TODO: Parse results, for now just print...
  return "RESULTS: " + str(decrypted)

if __name__ == '__main__':
    app.run(debug=True)