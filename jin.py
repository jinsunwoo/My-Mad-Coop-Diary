import requests
from bs4 import BeautifulSoup

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    'referer': 'https://www.google.com/'
}

url = "https://www.indeed.com/jobs?q=react&l=canada"
r = requests.get(url, headers=header)

result = requests.get(url)
soup = BeautifulSoup(result.text, 'html.parser')
print(soup)


def extract_indeed_pages(url):
    # start=99999 because we want to know max page
    result = requests.get(url)
    # indeed_result.text -> get the html of the requested url
    # soup: extract data (필요한 데이터로 편집해줌)
    soup = BeautifulSoup(result.text, 'html.parser')
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
