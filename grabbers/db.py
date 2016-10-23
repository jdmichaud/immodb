import json
import shutil
import logging

SEPARATOR = ';'

#format:
#(uid, postal_code, type_bien, nb_piece, surface, price, timestamp, latest)

def loaddata(filename):
  try:
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()
  except IOError as e:
    logging.info('file %s, does not exist' % filename)
    return []
  else:
    data = []
    for line in lines[1:]: # ignore the header
      e = tuple(line.split(SEPARATOR))
      data.append(e)
    return data

# Preprocess the DB for statitics computation
# Remove all non-latest data and all '?''
def preprocess(db):
  return [entry for entry in db if entry[4] != '?' and entry[5] != '?' and entry[7].startswith('1')]


def writedb(filename, db):
  try:
    file = open(filename + '.tmp', 'w')
  except IOError as e:
    logging.error('error opening file %s, data not backed up' % filename)
    return 0
  else:
    file.write(SEPARATOR.join(map(str, ('uid', 'postal_code', 'type_bien', 'nb_piece', 'surface', 'price', 'timestamp', 'latest'))))
    file.write('\n')
    for entry in sorted(db):
      file.write(SEPARATOR.join(map(str, entry)))
      file.write('\n')
    file.close()
    # Check the new file has more line 
    if len(open(filename, 'r').read().splitlines()) <= len(open(filename + '.tmp', 'r').read().splitlines()):
      shutil.move(filename + '.tmp', filename) # atomic transaction
    else: # warning !!
      logging.error("DB not backed up to %s because it's size is smaller than the original database !" % (filename + '.tmp', ))
    return len(db)

def addentry(db, entry, timestamp):
  # Does the entry already exists in base?
  index_list = [(i, db[i]) for i, x in enumerate(db) if x[0] == entry[0]]
  if index_list:
    latest_index = next(i for i, x in index_list if x[7] == '1')
    # Yes, is the entry different from the last one OR there is only one element
    if entry != db[latest_index][:-2] or len(index_list) == 1:
      # Yes, then unflag the latest
      db[latest_index] = db[latest_index][:-1] + ('0',)
      # and create a new entry
      db.append(entry + (timestamp, '1'))
    else:
      # No, update the timestamp
      db[latest_index] = db[latest_index][:-2] + (timestamp, '1')
  else:
    # No, create an entry
    db.append(entry + (timestamp, '1'))

def addentries(db, entries, timestamp):
  for entry in entries:
    addentry(db, entry, timestamp)

def getjson(db, file=None):
  d = [k + data for (k, data) in db.iteritems()]
  if file is not None:
    return json.dump(d, file)
  else:
    return json.dumps(d)

if __name__ == '__main__':
  import time
  db = loaddata('test.db.csv')
  ts = int(time.time())
  addentry(db, ('annonce-92598149-319327', '780646', 'Appartement', '1', '9', '65000'), ts)
  addentry(db, ('annonce-92598149-319327', '780646', 'Appartement', '1', '12', '63000'), ts + 1)
  writedb('test.db.csv', db)
  db = loaddata('test.db.csv')
  addentry(db, ('annonce-92598149-319327', '780646', 'Appartement', '1', '12', '62000'), ts + 2)
  writedb('test.db.csv', db)  
  db = loaddata('test.db.csv')
  addentry(db, ('annonce-92598149-319327', '780646', 'Appartement', '1', '12', '62000'), ts + 10)
  writedb('test.db.csv', db)  
