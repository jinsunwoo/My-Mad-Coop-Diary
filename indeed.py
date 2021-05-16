import requests
from bs4 import BeautifulSoup

LIMIT = 50


def extract_indeed_pages(url):
    # start=99999 because we want to know max page
    result = requests.get(url)
    # indeed_result.text -> get the html of the requested url
    # soup: extract data (필요한 데이터로 편집해줌)
    soup = BeautifulSoup(result.text, 'html.parser')
    print("soup", soup)
    oocs = soup.find("p", {"class": "oocs"})
    if oocs is not None:
        redirect = oocs.find('a')['href']
        result = requests.get(redirect)
        soup = BeautifulSoup(result.text, 'html.parser')
    # find: 해당 클래스를 찾아라
    pagination = soup.find("div", {"class": "pagination"})
    # find_all: 다음에서 해당 되는 정보를 모두 찾아라 # list 형태로 주기 때문에 for page in pages 형태로 사용하면 됨
    try:
        links = pagination.find_all('li')
        pages = []
        for link in links[:-1]:
            pages.append(int(link.string))
        max_page = pages[-1]
    except:
        max_page = -1
    if max_page == -1 and soup.find("div", {"class": "bad_query"}) is None:
        max_page = 1
    return max_page


def extract_indeed_job(search_result):
    title = search_result.find("h2", {"class": "title"}).find('a')["title"]
    company = search_result.find("span", {"class": "company"})
    company_anchor = company.find("a")
    if company_anchor is not None:
        company = str(company_anchor.string)
    else:
        company = str(company.string)
    company = company.strip()
    location = search_result.find("div", {"class": "recJobLoc"})["data-rc-loc"]
    id = search_result["data-jk"]
    #result = requests.get(f"https://www.indeed.com/viewjob?jk={job_id}")
    #soup = BeautifulSoup(result.text, 'html.parser')
    #apply_btn = soup.find("div", {"id": "applyButtonLinkContainer"})
    # apply_link = apply_btn.find(
    #   "div", {"class": "icl-u-lg-hide"}).find("a")["href"]
    #description_html = soup.find("div", {"id": "jobDescriptionText"})
    return {'title': title, 'company': company, 'location': location, 'id': id}


def extract_indeed_jobs(max_page, url):
    jobs = []
    for page in range(max_page):
        #print(f"Scrapping page {page}")
        result = requests.get(f"{url}&start={LIMIT*page}")
        # print(f"{url}&start={LIMIT*page}")
        soup = BeautifulSoup(result.text, 'html.parser')
        # print(soup)
        oocs = soup.find("p", {"class": "oocs"})
        print("oocs", oocs)
        # print(oocs)
        if oocs is not None:
            redirect = oocs.find('a')['href']
            # print(redirect)
            result = requests.get(redirect)
            soup = BeautifulSoup(result.text, 'html.parser')
        search_results = soup.find_all(
            "div", {"class": "jobsearch-SerpJobCard"})
        print("search_result", search_results)
        # print(soup)
        for search_result in search_results:
            job = extract_indeed_job(search_result)
            jobs.append(job)
    return jobs


def get_indeed_jobs(title, location):
    if title == "":
        title = "Search"
    url = f"https://www.indeed.com/jobs?q={title}&l={location}&limit={LIMIT}"
    max_page = extract_indeed_pages(url)
    jobs = extract_indeed_jobs(max_page, url)
    return jobs


print(get_indeed_jobs("node developer", "korea"))
