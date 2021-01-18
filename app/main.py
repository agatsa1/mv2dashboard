from flask import (
    Flask,
    render_template, 
    request, 
    redirect, 
    jsonify, 
    make_response, 
    url_for,
    send_file, 
    send_from_directory, 
    safe_join, 
    abort,
    after_this_request,
    session,
    Response,
    g)
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from pymongo.errors import ConnectionFailure, AutoReconnect
import json

app = Flask(__name__)
app.secret_key = "blahblahblahblah"
app.debug = True

CORS(app, resources={r"/*": {"origins": "*"}})

class User:
    def __init__(self, username, name, password):
        self.username = username
        self.name = name
        self.password = password

    def __repr__(self):
        #return "<User: ",self.username,">"
        return '<User: {}>'.format(self.username)

users = []
users.append(User(username='pg',name='Prashant',password='notadmin'))
users.append(User(username='agatsa',name='Admin',password='agatsa@57'))

@app.before_request
def before_request():
    #print('All Users: ',users)
    if 'user_id' in session:
        user = [res for res in users if res.username == session['user_id']]
        g.user = user[0]
        print("Global User: ",g.user)

# testing  db
# 'mongodb://cluster0-shard-00-00.lxvq0.mongodb.net:27017,cluster0-shard-00-01.lxvq0.mongodb.net:27017,cluster0-shard-00-02.lxvq0.mongodb.net:27017/mv2?ssl=true&replicaSet=atlas-13h83n-shard-0&authSource=admin&retryWrites=true&w=majority'

# AutoReconnect error
#https://www.digitalocean.com/community/questions/problems-with-mongodb-and-flask

app.config['MONGO_URI'] = 'mongodb://agatsa62:jksparkle0605@40.83.251.117:4000/mv2?authSource=admin'

mongo = PyMongo(app)

@app.route("/login", methods=["GET", "POST"])
@cross_origin()
def login():
    feedback = ""
    if request.method == "GET":
        session.pop('user_id',None)

        return render_template("login.html")
    
    elif request.method == "POST":
        if 'user_id' in session: print('Session Running: ',session,' Session Data: ',session['user_id'])
        session.pop('user_id',None)

        username = request.form['username']
        password = request.form['password']

        print("Logged in: ",username, password)

        user = [res for res in users if res.username == username]
        print('Query User: ',user,' Type: ',type(user))

        if user !=[] and user[0].password == password:
            session['user_id'] = user[0].username
            print('New Session: ',session['user_id'], ' Type: ', type(session['user_id']))
            
            feedback = "login successful"

            #return render_template("index.html", feedback=feedback)
            redirect(url_for('index'))
        else:
            feedback = "login unsuccessful"
            
            return render_template("login.html", feedback=feedback)

        return redirect(url_for('index'))

    return render_template("login.html", feedback=feedback)

@app.route('/', methods=["GET","POST"])
@cross_origin()
def index():
    if request.method == "GET":
        if 'user_id' in session: 
            print('Session Running: ',session,' Session Data: ',session['user_id'])

            try:
                coll = mongo.db.collection_names()
            except AutoReconnect:
                coll = mongo.db.collection_names()
                #mongo = PyMongo(app)
            return render_template("index.html", collections=coll)
        else:
            return redirect(url_for('login'))
            
    elif request.method == "POST" and 'user_id' in session: 
        print('Session Running: ',session,' Session Data: ',session['user_id'])

        data = request.get_json()
        if data['Block'] == 1:
            print('Block1: Fetched ', data, '\n')
            macID = mongo.db[data['select_col']].distinct('macId')
            print(data['select_col'], macID)

            return json.dumps({'macId':list(macID)}) # Response(list(macID),  mimetype='application/json')
        elif data['Block'] == 2:
            print('Block2: ',data, '\n')
            collection_key_value = {    'sugars':'sugar',   'temps':'temp', 'spo2':'spo2'   }

            recrds = mongo.db[data['select_col']].find({'macId':data['select_mac']}).sort([('_id', -1)])
            recrds_data = [i for i in recrds]
            print('Block2: Fetched ', data['select_col'], len(recrds_data), '\n')


            payload_data = []
            diasysSeries = []
            otherSeries = []
            for rw in range(len(recrds_data)):
                if data['select_col'] == 'bps':
                    payload_data.append({
                        'Timestamp': recrds_data[rw]['createdTs'], 
                        'Reading - Diastolic': recrds_data[rw]['diastolic'],
                        'Reading - Systolic': recrds_data[rw]['systolic'],
                        'Firmware Version': recrds_data[rw]['systolicArray'],
                        'Name': recrds_data[rw]['name'] if 'name' in recrds_data[rw].keys() else '', 
                        'Email': recrds_data[rw]['email'] if 'email' in recrds_data[rw].keys() else ''
                        })
                    diasysSeries.insert(0, [rw, recrds_data[rw]['diastolic'],recrds_data[rw]['systolic']])
                else:
                    key = collection_key_value[ data['select_col'] ]
                    payload_data.append({
                        'Timestamp': recrds_data[rw]['createdTs'], 
                        str('Reading - '+key): recrds_data[rw][key], 
                        'Name': recrds_data[rw]['name'] if 'name' in recrds_data[rw].keys() else '', 
                        'Email': recrds_data[rw]['email'] if 'email' in recrds_data[rw].keys() else ''
                        })
                    otherSeries.insert(0, [rw, recrds_data[rw][key]])

            if len(otherSeries) != []:
                for i in range(len(otherSeries)):
                    otherSeries[i][0] = i

            if len(diasysSeries) != []:
                for i in range(len(diasysSeries)):
                    diasysSeries[i][0] = i

            payload_object = {
                'macId': data['select_mac'],
                'data':payload_data,
                'otherSeries':otherSeries,
                'diasysSeries':diasysSeries
            }
            
            print(otherSeries) #, payload_object

            return payload_object
        else:
            return redirect(url_for("login"))
        
@app.route('/result', methods=["POST"])
@cross_origin()
def result():
    print(request.form)
    return render_template("result.html")

if __name__ == "__main__":
    app.run(port=5001, debug=True)