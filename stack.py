import requests
from bs4 import BeautifulSoup


def extract_stack_pages(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    no_result = soup.find("div", {"class": "s-empty-state"})
    if no_result is not None:
        max_page = -1  # No result
    else:
        pagination = soup.find("div", {"class": "s-pagination"})
        if pagination is None:
            max_page = 1
        else:
            pages = soup.find("div", {"class": "s-pagination"}).find_all('a')
            if pages[-1].find('span').get_text() == "next":
                max_page = int(pages[-2].find('span').get_text())
            else:
                max_page = int(pages[-1].find('span').get_text())
    return max_page


def extract_job(html):
    title = html.find("h2", {"class": "mb4"}).find("a")["title"]
    company, location = html.find("h3", {
        "class": "mb4"
    }).find_all("span", recursive=False)
    company = company.get_text(strip=True).strip("-")
    location = location.get_text(strip=True)
    jobID = html['data-jobid']
    return {'title': title, 'company': company, 'location': location, 'id': jobID}


def extract_stack_jobs(last_page, url):
    jobs = []
    for page in range(last_page):
        result = requests.get(f"{url}&pg={page+1}")
        soup = BeautifulSoup(result.text, "html.parser")
        results = soup.find_all("div", {"class": "-job"})
        for result in results:
            job = extract_job(result)
            jobs.append(job)
    return jobs


def get_stack_jobs(title, location):
    url = f"https://stackoverflow.com/jobs?q={title}&l={location}"
    max_page = extract_stack_pages(url)
    print(max_page)
    jobs = extract_stack_jobs(max_page, url)
    if len(jobs) > 500:
        jobs = jobs[0:500]
    return jobs
