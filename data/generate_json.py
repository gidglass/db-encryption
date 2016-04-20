import pandas as pd
import json

DATA = pd.read_csv('customer.csv')
TABLE = 'CUSTOMER'
COLS = ('ID', 'FIRST_NAME', 'LAST_NAME', 'ADDRESS', 'CITY', 'STATE', 'ZIP', 'PHONE', 'EMAIL', 'SSN')

results = []
for row in DATA.values:
  entry = {
      'row': {
          'table': TABLE,
          'fields': dict(zip(COLS, row))
      }
  }
  results.append(entry)

  with open('sql_insert.json', 'w') as outfile:
    json.dump(results, outfile)
    
  outfile.close()