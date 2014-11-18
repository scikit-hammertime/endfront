from SQL import *
import pickle

db = DB()
drug_names_old = pickle.load(open('/data/aers/formatted/drug_names.pkl','r'))

new_drug_names = []
for drug_name in drug_names_old:
	response = db.query(drug_name)
	if response is None:
		continue
	else:
		new_drug_names.append(drug_name)

print len(new_drug_names)
pickle.dump(new_drug_names, open('/data/aers/formatted/new_drug_names.pkl','w'))
