from flask import Flask, render_template, request, redirect
from indeed import get_indeed_jobs
import requests
from bs4 import BeautifulSoup

app = Flask("MyMadCoopDiary")


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/create")
def create():
    return render_template("create.html")


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

    return render_template("result.html", job_title=title, job_location=location, job_site=site, jobs=jobs)


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


@ app.route("/<username>")
def potato(username):
    return f"Hello, {username}"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
