import pymysql

class Database:
  def __init__(self, host, username, password, db):
    self._host = host
    self._username = username
    self._password = password
    self._db = db

  def _get_connection(self):
    return pymysql.connect(
      host = self._host,
      user = self._username,
      password = self._password,
      db = self._db)

  def _execute (self, sql):
    db = self._get_connection()
    cursor = db.cursor()
    results = []
    try:
      cursor.execute(sql)
      results = cursor.fetchall()
      db.commit()
    except:
      db.rollback()
    finally:
      db.close()
      return results

  def create_table (self, schema, drop_if_exists=False):
    TABLE = schema['table']
    COLS, TYPES = self._split_fields(schema['fields'])

    sql_table = "CREATE TABLE %s (" % TABLE
    sql_schema = ", ".join('%s %s' % t for t in zip(COLS, TYPES)) + ")"

    if drop_if_exists:
      self._execute("DROP TABLE IF EXISTS %s" % table)

    self._execute(sql_table + sql_schema)

  def insert (self, row):
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
    TABLE = row['table']
    COLS, VALS = self._split_fields(row['fields'])

    # Construct query
    sql_table = "INSERT INTO %s" % TABLE
    sql_cols = "(%s)" % ", ".join(COLS)
    sql_vals = "VALUES ('%s')" % "\', \'".join(VALS)
    self._execute(sql_table + sql_cols + sql_vals)

  def select (self, query):
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
    TABLE, COLS, VALS = query['table'], query['cols'], query['fields']
    sql_select = "SELECT %s " % ", ".join(COLS)
    sql_from = "FROM %s.%s " % (self._db, TABLE)
    sql_where = "WHERE %s;" % " AND ".join(self._json_to_where_clause(VALS))
    return self._execute(sql_select + sql_from + sql_where)

  ###
  # HELPER METHODS
  ##

  def _json_to_where_clause (self, json):
    result = []
    for k,v in json.iteritems():
        result.append(k + "=" + "\'" + v + "\'")
    return result

  def _split_fields(self, fields):
    a, b = [], []
    for k, v in fields.iteritems():
      a.append(k)
      b.append(str(v))
    return (a, b)