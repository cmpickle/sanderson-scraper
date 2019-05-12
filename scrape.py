import requests
from bs4 import BeautifulSoup

# specify the url
url = 'https://brandonsanderson.com/'

# query the website and return the html to the variable 'page'
page = requests.get(url)

# parse the html using beautiful soup and store in variable `soup`
soup = BeautifulSoup(page.text, 'html.parser')

# get progress bar div to limit the page
progress_bar = soup.find('div', attrs={'class': 'progress-titles'})

# get list of book titles
name_box = soup.find_all('span', attrs={'class': 'book-title'})

# get progress of the books
status_box = soup.find_all('div', attrs={'class': 'progress'})

if len(name_box) != len(status_box) or len(name_box) == 0 or len(status_box) == 0: 
    raise RuntimeError("Titles and Status arrays don't match.")
else:
    final_output = ""
    index = 0
    while index < len(name_box):
        final_output += (name_box[index].text + ": " + status_box[index].find('div', attrs={'class': 'after'}).text + "\n")
        index += 1

    print(final_output)