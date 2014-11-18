from flask import Flask, jsonify, request
from flask.ext.cors import CORS

app = Flask(__name__)
cors = CORS(app)

from pytrie import StringTrie

from scikit_hammertime.Predictor import Predictor




def init():

	app.p = Predictor()
	app.meditems = StringTrie()
	drugs = app.p.get_drugs()

	app.conitems = StringTrie()
	conditions = app.p.get_conditions()

	for d in drugs:
		app.meditems[d] = d



	for c in conditions:
		app.conitems[c] = c
    #load users data file

init()
@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route("/medicinalproducts")
def medlist():
	partialmed = request.args.get('startsWith')
	matches = app.meditems.values(prefix=partialmed.lower())
	return jsonify(drugs=matches)


@app.route("/preexistingconditions")
def conlist():
	partialcon = request.args.get('startsWith')
	matches = app.conitems.values(prefix=partialcon.lower())
	return jsonify(conditions=matches)

#GET /interactions?medicinalproducts=medicinalproduct1,...&conditions=condition1,...


@app.route('/interactions')
def interact():
	meds = request.args.get('medicinalproducts')
	cons = request.args.get('conditions')

	marray = meds.split(',')
	returnlist = app.p.predict(marray)


	return jsonify(results=returnlist)



if __name__ == "__main__":
	app.debug = False
	app.run(host='0.0.0.0', port=8888)

