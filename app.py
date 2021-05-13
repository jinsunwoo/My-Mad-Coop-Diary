from flask import Flask, render_template, request, redirect, jsonify
from indeed import get_indeed_jobs
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import hashlib
import datetime
import jwt

SECRET_KEY = "cherry"

app = Flask("MyMadCoopDiary")

client = MongoClient('localhost', 27017)
db = client.mymadcoopdiary


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/create")
def create():
    return render_template("create.html")


@app.route('/api/log', methods=['POST'])
def api_log():
    title = request.form['potato1']
    company = request.form['potato2']
    mmcdID = request.form['potato3']
    location = request.form['potato4']
    #date = request.form['potato5']
   # id = request.form['potato6']

    db.rabbit.insert_one(
        {'potato1': title, 'potato2': company, 'potato3': mmcdID, 'potato4': location})
    return jsonify({'result': 'success'})


@app.route('/api/register', methods=['POST'])
def api_register():
    # Receive new user information
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']
    email_receive = request.form['email_give']
    # Check if received id is already taken
    user_list = list(db.user.find({}))
    for user in user_list:
        if user['id'] == id_receive:
            return jsonify({'result': 'try again', 'msg': 'The ID is already taken. Please use another ID.'})
    # If received id is unique, hash received password
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    # Insert new user information to DB
    db.user.insert_one(
        {'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive, 'email': email_receive})
    return jsonify({'result': 'success', 'msg': 'You are successfully registered!'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    # Hash the entered password
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    # Find the user with the entered id and pw
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
    # If the user is found, make a token using jwt
    if result is not None:
        # token with 3 hours time expiration
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    # If there is no such id and pw pair
    else:
        result = db.user.find_one({'id': id_receive})
        if result is None:
            return jsonify({'result': 'fail', 'msg': 'There is no such ID'})
        else:
            return jsonify({'result': 'fail', 'msg': 'Wrong password'})


@app.route('/api/validtoken', methods=['GET'])
def valid_token():
    token_receive = request.headers['token_give']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'userinfo': userinfo})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': 'Log in time is expired. Please log in again.'})


@app.route('/api/logapplication', methods=['POST'])
def log_application():
    userid_receive = request.form['userid_give']
    title_receive = request.form['title_give']
    company_receive = request.form['company_give']
    location_receive = request.form['location_give']
    date_receive = request.form['date_give']
    id_receive = request.form['id_give']
    print(userid_receive)
    db.coops.insert_one(
        {'userid': userid_receive, 'title': title_receive, 'company': company_receive, 'location': location_receive, 'date': date_receive, 'jobid': id_receive, 'status': "a"})
    return jsonify({'result': 'success'})


@app.route("/main")
def main():
    return render_template("main.html")


@app.route("/applied")
def applied():
    return render_template("applied.html")


@app.route("/phone")
def phone():
    return render_template("phone.html")


@app.route("/interview")
def interview():
    return render_template("interview.html")


@app.route("/job")
def job():
    return render_template("job.html")


@app.route("/declined")
def declined():
    return render_template("declined.html")


@app.route("/ghosted")
def ghosted():
    return render_template("ghosted.html")


@app.route("/report")
def report():
    title = request.args.get('title')
    location = request.args.get('location')
    if title == "" and location == "":
        return redirect("/")
    if request.args.get('action') == "i":
        site = "Indeed"
    elif request.args.get('action') == "s":
        site = "Stackoverflow"
    jobs = get_indeed_jobs(title, location)

    return render_template("view.html", job_title=title, job_location=location, job_site=site, jobs=jobs)


@app.route("/forward", methods=['GET'])
def move_forward():
    # Moving forward code
    if request.args.get('id_link') is not None:
        job_id = request.args.get('id_link')
        result = requests.get(f"https://www.indeed.com/viewjob?jk={job_id}")
        soup = BeautifulSoup(result.text, 'html.parser')
        link = soup.find("div", {"id": "applyButtonLinkContainer"}).find(
            "div", {"class": "icl-u-lg-hide"}).find("a")["href"]
        return redirect(link)
    if request.args.get('id_desc') is not None:
        job_id = request.args.get('id_desc')
        result = requests.get(f"https://www.indeed.com/viewjob?jk={job_id}")
        soup = BeautifulSoup(result.text, 'html.parser')
        description_html = soup.find("div", {"id": "jobDescriptionText"})
        return f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta http-equiv='X-UA-Compatible' content='IE = edge'><meta name='viewport' content='width = device-width, initial-scale = 1.0'><title>Job Description</title><style>body{{background-color: #c0d6df;padding: 20px;}}</style></head><body><h2>Job Description</h2>{description_html}</body></html>"

    #job_id = request.args.get('id_link')
    #result = requests.get(f"https://www.indeed.com/viewjob?jk={job_id}")
    #soup = BeautifulSoup(result.text, 'html.parser')
    # link = soup.find("div", {"id": "applyButtonLinkContainer"}).find(
    #   "div", {"class": "icl-u-lg-hide"}).find("a")["href"]
    # return redirect(link)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
