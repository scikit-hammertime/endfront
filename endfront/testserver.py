from flask import Flask, jsonify, request
app = Flask(__name__)

from pytrie import StringTrie




@app.before_first_request
def init():

	app.meditems = StringTrie()
	drugs = ['advil','tylenol']

	app.conitems = StringTrie()
	conditions = ['high cholesterol','fatness']

	for d in drugs:
		app.meditems[d] = d



	for c in conditions:
		app.conitems[c] = c
    #load users data file


#TODO partial match search with tree

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route("/medicinalproducts")
def medlist():
	partialmed = request.args.get('startsWith')
	matches = app.meditems.values(prefix=partialmed)
	return jsonify(drugs=matches)


@app.route("/preexistingconditions")
def conlist():
	partialcon = request.args.get('startsWith')
	matches = app.conitems.values(prefix=partialcon)
	return jsonify(conditions=matches)

#GET /interactions?medicinalproducts=medicinalproduct1,...&conditions=condition1,...


@app.route('/interactions')
def interact():
	meds = request.args.get('medicinalproducts')
	cons = request.args.get('conditions')

	testlist = [{'se': 'headache', 'score': 4},{'se': 'headache', 'score': 4},{'se': 'headache', 'score': 4},{'se': 'headache', 'score' : 4}]

	return jsonify(results=testlist)



if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0', port=8888)