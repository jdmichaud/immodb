from grabbers.db import loaddata, preprocess

def average_price_m_square_per_departement(db):
  size = {}
  acc = {}
  for entry in db:
    key = entry[1][:2]
    size[key] = size[key] + 1 if key in size else 1
    acc[key] = acc[key] + float(entry[5]) / float(entry[4]) if key in acc else float(entry[5]) / float(entry[4])
  for key, value in acc.iteritems():
    acc[key] = round(value / size[key])
    print key, acc[key]
  return { "average_price_per_m_square": acc, "number_of_annonces_per_departement": size }

def compute_annonce_histogram(db):
  total = {}
  dpts = {}
  for entry in db:
    key = entry[1][:2]
    nb_piece = entry[3] 
    total[nb_piece] = total[nb_piece] + 1 if nb_piece in total else 0
    if key not in dpts:
      dpts[key] = { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '5+': 0, '6': 0 }
    dpts[key][nb_piece] = dpts[key][nb_piece] + 1
  return { "number_of_annonces_per_pieces": total, "number_of_annonces_per_departement_per_pieces": dpts }

def compute_departement_stats():
  db = preprocess(loaddata('grabbers/seloger.db.csv'))
  result = average_price_m_square_per_departement(db)
  result.update(compute_annonce_histogram(db))
  return result