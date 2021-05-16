import requests
from bs4 import BeautifulSoup


list = [1]
list.append(None)
print(list)
list.remove(None)
print(list)


# try:
#   links = pagination.find_all('li')
#  pages = []
# for link in links[:-1]:
#    pages.append(int(link.string))
#max_page = pages[-1]
# except:
#   max_page = -1
##   max_page = 1
# print(max_page)
