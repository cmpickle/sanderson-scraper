# import libraries
import urllib.request
# import ssl
from bs4 import BeautifulSoup

# TODO: this should be removed later
# ssl._create_default_https_context = ssl._create_unverified_context

print("Hello, World!")

# specify the url
url = 'https://brandonsanderson.com/'

# query the website and return the html to the variable 'page'
request = urllib.request.Request(url)
response = urllib.request.urlopen(request)

# parse the html using beautiful soup and store in variable `soup`
soup = BeautifulSoup(response, 'html.parser')

# Take out the <div> of name and get its value
name_box = soup.find('span', attrs={'class': 'book-title'})

print(name_box)