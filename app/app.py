from flask import Flask, jsonify, request
from flask import Flask, request, Response, render_template
from flask_pymongo import PyMongo
import json
#from flask_mongoengine import MongoEngine
#from pymongo import MongoClient

#from database.db import initialize_db
#from database.models import bps, sugars, spo2, temps

app = Flask(__name__)

# testing  db
# 'mongodb://cluster0-shard-00-00.lxvq0.mongodb.net:27017,cluster0-shard-00-01.lxvq0.mongodb.net:27017,cluster0-shard-00-02.lxvq0.mongodb.net:27017/mv2?ssl=true&replicaSet=atlas-13h83n-shard-0&authSource=admin&retryWrites=true&w=majority'

app.config['MONGO_URI'] = 'mongodb://agatsa62:jksparkle0605@40.83.251.117:4000/mv2?authSource=admin'

mongo = PyMongo(app)

@app.route('/', methods=['GET','POST'])
def hello():
    if request.method == 'GET':
        coll = mongo.db.collection_names()
        return render_template("index.html", collections=coll)
    elif request.method == 'POST':
        data = request.get_json()
        if data['Block'] == 1:
            print 'Block1: ',data, '\n'
            macID = mongo.db[data['select_col']].distinct('macId')
            print data['select_col'], macID

            return json.dumps({'macId':list(macID)}) # Response(list(macID),  mimetype='application/json')
        elif data['Block'] == 2:
            print 'Block2: ',data, '\n'
            collection_key_value = {    'sugars':'sugar',   'temps':'temp', 'spo2':'spo2'   }

            recrds = mongo.db[data['select_col']].find({'macId':data['select_mac']}).sort([('_id', -1)])
            recrds_data = [i for i in recrds]
            print 'Block2: Fetched ', data['select_col'], len(recrds_data), recrds_data, '\n'


            payload_data = []
            systolicSeries = []
            diastolicSeries = []
            otherSeries = []
            for rw in range(len(recrds_data)):
                #payload_data = [{'Reading':i[key], 'Timestamp':i['createdTs'], 'Name':i['name'] if 'name' in i.keys() else '', 'Email':i['email'] if 'email' in i.keys() else ''} for i in recrds_data]
                if data['select_col'] == 'bps':
                    payload_data.append({
                        'Timestamp': recrds_data[rw]['createdTs'], 
                        'Reading - Diastolic': recrds_data[rw]['diastolic'], 
                        'Reading - Systolic': recrds_data[rw]['systolic'], 
                        'Name': recrds_data[rw]['name'] if 'name' in recrds_data[rw].keys() else '', 
                        'Email': recrds_data[rw]['email'] if 'email' in recrds_data[rw].keys() else ''
                        })
                    #systolicSeries.sppend([,rw])
                else:
                    key = collection_key_value[ data['select_col'] ]
                    payload_data.append({
                        'Timestamp': recrds_data[rw]['createdTs'], 
                        str('Reading - '+key): recrds_data[rw][key], 
                        'Name': recrds_data[rw]['name'] if 'name' in recrds_data[rw].keys() else '', 
                        'Email': recrds_data[rw]['email'] if 'email' in recrds_data[rw].keys() else ''
                        })
                    otherSeries.append([rw, recrds_data[rw][key]])

            payload_object = {
                'macId': data['select_mac'],
                'data':payload_data,
                'otherSeries':otherSeries
            }
            print payload_object

            return payload_object
        
@app.route('/result', methods=['POST'])
def result():
    print request.form
    return render_template("result.html")

if __name__ == "__main__":
    app.run(port=5001, debug=True)