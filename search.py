# imports
import sqlite3
import urllib2
import tempfile
import os.path
import json
import requests
from contextlib import closing
from flask import Flask, request, render_template, session, g, redirect, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy

api_key = os.environ['API_KEY']
app_id = os.environ['APP_ID']


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    tempfile.gettempdir(), 'search.db')


db = SQLAlchemy(app)
results = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', app_id=app_id)
    else:
        if request.form['button-type'] == 'auth':
            return auth()
        elif request.form['button-type'] == 'search':
            return search()

def search():
    # get all the account_ids
    accounts = []
    for a in Account.query.all():
        accounts.append(str(a.account_id))
    accounts = ','.join(accounts)

    # make search api request
    get_req_url = 'https://api.kloudless.com:443/v0/accounts/' + accounts + '/search/?q=' + request.form['text']
    resp = requests.get(get_req_url, headers={'Authorization': 'ApiKey ' + api_key})
    content = resp.json()

    return show_search(content, request.form['text'])

def show_search(content, text):
    # list the results of the search
    for o in content['objects']:
        results[o['name']] = (o['id'], o['account'])
    return render_template('results.html', results=results, text=text)

def auth():
    account = Account(request.form['account_id'])
    db.session.add(account)
    db.session.commit()
    return redirect('/')

@app.route('/get_link/', methods=['GET', 'POST'])
def get_link():
    # import pdb; pdb.set_trace()
    file_name = request.form['file_name']

    file_id = str(results[file_name][0])
    account = str(results[file_name][1])
    post_req_url = 'https://api.kloudless.com/v0/accounts/' + account + '/links/'
    headers = {'Authorization': 'ApiKey ' + api_key, 'Content-Type': 'application/json'}
    data = {'file_id': file_id}
    resp = requests.post(post_req_url, headers=headers, data=json.dumps(data))
    # import pdb; pdb.set_trace()
    return redirect(resp.json()['url'])


# models
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, unique=False)

    def __init__(self, account_id):
        self.account_id = account_id

    def __repr__(self):
        return '<Account %r>' % self.account_id


if __name__ == '__main__':
    # set up db
    db.drop_all()
    db.create_all()
    db.session.commit()

    # clear results
    results = {}

    # run the app
    app.run(debug=True)