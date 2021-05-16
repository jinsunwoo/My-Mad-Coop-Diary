from flask import Flask, render_template, request, redirect, jsonify
from indeed import get_indeed_jobs
from stack import get_stack_jobs
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import hashlib
import datetime
import jwt
from bson.objectid import ObjectId
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

SECRET_KEY = "cherry"

app = Flask("MyMadCoopDiary")

client = MongoClient('localhost', 27017)
db = client.mymadcoopdiary


@app.route("/")
def login():
    return render_template("index.html")


@app.route("/create")
def create():
    return render_template("create.html")


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
        nickname = userinfo['nick'].capitalize()
        applied_list = list(db.jobs.find(
            {'userid': payload['id'], 'status': 'a'}))
        phone_list = list(db.jobs.find(
            {'userid': payload['id'], 'status': 'p'}))
        interview_list = list(db.jobs.find(
            {'userid': payload['id'], 'status': 'i'}))
        job_list = list(db.jobs.find({'userid': payload['id'], 'status': 'j'}))
        declined_list = list(db.jobs.find(
            {'userid': payload['id'], 'status': 'd'}))

        ghosted_list = list(db.jobs.find(
            {'userid': payload['id'], 'status': 'g'}))
        statistics = {'nickname': nickname, 'a_num': len(applied_list), 'p_num': len(phone_list), 'i_num': len(
            interview_list), 'j_num': len(job_list), 'd_num': len(declined_list), 'g_num': len(ghosted_list)}

        return jsonify({'result': 'success', 'userinfo': userinfo, 'statistics': statistics})
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

    db.jobs.insert_one(
        {'userid': userid_receive, 'title': title_receive, 'company': company_receive, 'location': location_receive, 'date': date_receive, 'jobid': id_receive, 'status': "a"})
    return jsonify({'result': 'success'})


@app.route('/api/phone', methods=['POST'])
def api_phone():
    checkedlist = request.form.getlist('checkedlist[]')
    for checked in checkedlist:
        db.jobs.update({"_id": ObjectId(checked)}, {"$set": {"status": "p"}})
    return jsonify({'result': 'success'})


@app.route('/api/interview', methods=['POST'])
def api_interview():
    checkedlist = request.form.getlist('checkedlist[]')
    for checked in checkedlist:
        db.jobs.update({"_id": ObjectId(checked)}, {"$set": {"status": "i"}})
    return jsonify({'result': 'success'})


@app.route('/api/job', methods=['POST'])
def api_job():
    checkedlist = request.form.getlist('checkedlist[]')
    for checked in checkedlist:
        db.jobs.update({"_id": ObjectId(checked)}, {"$set": {"status": "j"}})
    return jsonify({'result': 'success'})


@app.route('/api/declined', methods=['POST'])
def api_declined():
    checkedlist = request.form.getlist('checkedlist[]')
    for checked in checkedlist:
        db.jobs.update({"_id": ObjectId(checked)}, {"$set": {"status": "d"}})
    return jsonify({'result': 'success'})


@app.route('/api/ghosted', methods=['POST'])
def api_ghosted():
    checkedlist = request.form.getlist('checkedlist[]')
    for checked in checkedlist:
        db.jobs.update({"_id": ObjectId(checked)}, {"$set": {"status": "g"}})
    return jsonify({'result': 'success'})


@app.route('/api/deleted', methods=['POST'])
def api_deleted():
    checkedlist = request.form.getlist('checkedlist[]')
    for checked in checkedlist:
        db.jobs.remove({"_id": ObjectId(checked)})
    return jsonify({'result': 'success'})

    # print(type(checkedlist[0]))
    # print(list(db.jobs.find({"_id": ObjectId(checkedlist[0])})))
    # yay = db.jobs.find({'_id': checkedlist[0]})
    # print(yay['title'])
    return jsonify({'result': 'success'})


@ app.route("/main")
def main():
    return render_template("main.html")


@ app.route("/forgotpw")
def forgotpw():
    return render_template("forgotpw.html")


@ app.route("/forgotid")
def forgotid():
    return render_template("forgotid.html")


@app.route('/forgotid2', methods=['POST'])
def forgotid2():
    email_receive = request.form['email_give']
    result = db.user.find_one({'email': email_receive})
    if result is not None:
        user_id = result['id']
        me = "personalspace.2020.08@gmail.com"
        my_password = "ps1025ps"
        you = email_receive
        # here code starts
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "This is your ID of My Mad Coop Diary"
        msg['From'] = me
        msg['To'] = you

        html = '<html><body><p>Your My Mad Coop Diary ID is ' + \
            user_id + '</p></body></html>'
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
        s = smtplib.SMTP_SSL('smtp.gmail.com')
        s.login(me, my_password)
        s.sendmail(me, you, msg.as_string())
        s.quit()
        return jsonify({'result': 'success', 'msg': 'Your ID is sent to your email. Please check your email'})
    else:
        return jsonify({'result': 'fail', 'msg': 'Email you entered is not found'})


@app.route('/forgotpw2', methods=['POST'])
def forgotpw2():
    id_receive = request.form['id_give']
    email_receive = request.form['email_give']
    result = db.user.find_one({'id': id_receive, 'email': email_receive})
    if result is not None:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', 'msg': 'No such ID or Email. Try again.'})


@app.route('/resetpw')
def resetpw():
    return render_template("resetpw.html")


@app.route('/resetpw2', methods=['POST'])
def resetpw2():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    db.user.update_one({'id': id_receive}, {"$set": {'pw': pw_hash}})
    return jsonify({'result': 'success'})


@app.route("/report")
def report():
    title = request.args.get('title')
    location = request.args.get('location')
    if title == "" and location == "":
        return redirect("/main")
    if request.args.get('action') == "i":
        site = "Indeed"
        jobs = get_indeed_jobs(title, location)
        if len(jobs) == 0:
            jobs = get_indeed_jobs(title, location)
        if len(jobs) == 0:
            jobs = get_indeed_jobs(title, location)
    elif request.args.get('action') == "s":
        site = "Stackoverflow"
        jobs = get_stack_jobs(title, location)
        if len(jobs) == 0:
            jobs = get_stack_jobs(title, location)
        if len(jobs) == 0:
            jobs = get_stack_jobs(title, location)
    return render_template("view.html", job_title=title, job_location=location, job_site=site, jobs=jobs)


@ app.route("/senduserid")
def senduserid():
    if request.args.get('applied') is not None:
        userid = request.args.get('applied')
        applied_jobs = list(db.jobs.find(
            {"status": "a", "userid": userid}).sort("date", -1))
        print("This is checking point")
        print(applied_jobs)
        return render_template("applied.html", applied_jobs=applied_jobs)
    elif request.args.get('phone') is not None:
        userid = request.args.get('phone')
        phone_jobs = list(db.jobs.find(
            {"status": "p", "userid": userid}).sort("date", -1))
        return render_template("phone.html", phone_jobs=phone_jobs)
    elif request.args.get('interview') is not None:
        userid = request.args.get('interview')
        interview_jobs = list(db.jobs.find(
            {"status": "i", "userid": userid}).sort("date", -1))
        return render_template("interview.html", interview_jobs=interview_jobs)
    elif request.args.get('job') is not None:
        userid = request.args.get('job')
        job_jobs = list(db.jobs.find(
            {"status": "j", "userid": userid}).sort("date", -1))
        return render_template("job.html", job_jobs=job_jobs)
    elif request.args.get('declined') is not None:
        userid = request.args.get('declined')
        declined_jobs = list(db.jobs.find(
            {"status": "d", "userid": userid}).sort("date", -1))
        return render_template("declined.html", declined_jobs=declined_jobs)
    elif request.args.get('ghosted') is not None:
        userid = request.args.get('ghosted')
        ghosted_jobs = list(db.jobs.find(
            {"status": "g", "userid": userid}).sort("date", -1))
        return render_template("ghosted.html", ghosted_jobs=ghosted_jobs)


# @app.route("/api/applied")
# def api_applied():
#    user_id = request.headers['mmcdid_give']
 #   applied_jobs = list(db.jobs.find({"status": "a", "userid": user_id}))
  #  return render_template("applied.html", applied_jobs=applied_jobs)


@ app.route("/forward", methods=['GET'])
def move_forward():
    # Moving forward code

    if request.args.get("'Indeed'+'link'") is not None:
        job_id = request.args.get("'Indeed'+'link'")
        result = requests.get(f"https://www.indeed.com/viewjob?jk={job_id}")
        soup = BeautifulSoup(result.text, 'html.parser')
        link = soup.find("div", {"id": "applyButtonLinkContainer"}).find(
            "div", {"class": "icl-u-lg-hide"}).find("a")["href"]
        return redirect(link)
    if request.args.get("'Indeed'+'desc'") is not None:
        job_id = request.args.get("'Indeed'+'desc'")
        result = requests.get(f"https://www.indeed.com/viewjob?jk={job_id}")
        soup = BeautifulSoup(result.text, 'html.parser')
        description_html = soup.find("div", {"id": "jobDescriptionText"})
        return f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta http-equiv='X-UA-Compatible' content='IE = edge'><meta name='viewport' content='width = device-width, initial-scale = 1.0'><title>Job Description</title><style>body{{background-color: #c0d6df;padding: 20px;}}</style></head><body><h2>Job Description</h2>{description_html}</body></html>"
    if request.args.get("'Stackoverflow'+'link'") is not None:
        job_id = request.args.get("'Stackoverflow'+'link'")
        link = f"https://stackoverflow.com/jobs/{job_id}/"
        return redirect(link)
    if request.args.get("'Stackoverflow'+'desc'") is not None:
        job_id = request.args.get("'Stackoverflow'+'desc'")
        result = requests.get(f"https://stackoverflow.com/jobs/{job_id}/")
        soup = BeautifulSoup(result.text, 'html.parser')
        description_html = soup.find(
            "section", {"class": "mb32 fs-body2 fc-medium"})
        return f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta http-equiv='X-UA-Compatible' content='IE = edge'><meta name='viewport' content='width = device-width, initial-scale = 1.0'><title>Job Description</title><style>body{{background-color: #c0d6df;padding: 20px;}}</style></head><body>{description_html}</body></html>"

    # job_id = request.args.get('id_link')
    # result = requests.get(f"https://www.indeed.com/viewjob?jk={job_id}")
    # soup = BeautifulSoup(result.text, 'html.parser')
    # link = soup.find("div", {"id": "applyButtonLinkContainer"}).find(
    #   "div", {"class": "icl-u-lg-hide"}).find("a")["href"]
    # return redirect(link)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
