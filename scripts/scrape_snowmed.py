import requests as re
import pickle as pkl
import lxml
import json


def hit_api(drug_name):
    '''
    hits snomed's class hierarchy api by first finding the drugs rxcui and then hitting the hierarcy api with params src=src and type=tp
    '''

    # first, get the drug's rxcui
    r = re.get('http://rxnav.nlm.nih.gov/REST/approximateTerm.json', params={'term':drug_name, 'maxEntries':1})

    js = json.loads(r.text)
    return js
    # parse the xml to find the id
    rxcui = get_rxcui_from_tree(r.text)

    # hit the class hierarchy endpoint
    hierarcy= re.get('http://rxnav.nlm.nih.gov/REST/rxcui/%s/hierarchy' % rxcui, params={'src':src, 'type':tp})




if __name__ == '__main__':
    df = pkl.load(open('example_data.df','r'))
    terms = set()
    for l in df.DRUG:
        for term in l:
            terms.add(term)

    mapping = {}
    for term in terms:
        try:
            js = hit_api(term)

            drug = js['approximateGroup']['candidate'][0]['rxcui']
            mapping[term] = drug
            print "mapping %s to %s" % (term, drug)

        except:
            continue
    pkl.dump(mapping,open('mapping.pkl','w'))
