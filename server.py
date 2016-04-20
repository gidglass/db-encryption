from flask import Flask, request
from database import Database
import pymysql

app = Flask(__name__)

@app.route('/table', methods = ['POST'])
def create_table ():
  db = Database(
    host = 'localhost', 
    username = 'student', 
    password = 'Password123!',
    db = 'sample')

  # sample_schema_json = {
  #   "schema": {
  #     "table": "EMPLOYEE",
  #     "fields": {
  #       "FIRST_NAME": "CHAR(20) NOT NULL",
  #       "LAST_NAME": "CHAR(20)",
  #       "AGE": "INT",
  #       "SEX": "CHAR(1)",
  #       "INCOME": "FLOAT"
  #     }
  #   }
  # }
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

  # sample_request_json = {
  #   "row": {
  #     "table": "EMPLOYEE",
  #     "fields": {
  #       "FIRST_NAME": "Gideon",
  #       "LAST_NAME": "Glass",
  #       "AGE": "24",
  #       "SEX": "M",
  #       "INCOME": "80000"
  #     }
  #   }
  # }
  json = request.get_json()
  output = []
  for entry in json:
    db.insert(entry['row'])
    log = "INSERTED NEW ROW: %s into %s" % (str(entry['row']['fields']), str(entry['row']['table']))
    output.append(log)
  
  # TODO: ENCRYPT SENSATIVE JSON FIELDS HERE!!!
  # e.g. json['row']['fields']['FIRST_NAME'] = encrypt(key, data)
  return str(output)

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

  # TODO: DECRYPT SENSATIVE JSON FIELDS HERE!!!
  # e.g. json['row']['fields']['FIRST_NAME'] = decrypt(key, data)

  results = db.select(json['query'])  

  # TODO: Parse results, for now just print...
  return "RESULTS: " + str(results)

if __name__ == '__main__':
    app.run(debug=True)