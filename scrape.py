import requests
from bs4 import BeautifulSoup

# specify the url
url = 'https://brandonsanderson.com/'

# query the website and return the html to the variable 'page'
page = requests.get(url)

# parse the html using beautiful soup and store in variable `soup`
soup = BeautifulSoup(page.text, 'html.parser')

# get progress bar div to limit the page
progress_bar = soup.find(attrs={'class': 'progress-titles'})

# get list of book titles
name_box = progress_bar.find_all(attrs={'class': 'book-title'})

# get progress of the books
status_box = progress_bar.find_all(attrs={'class': 'progress'})

# if problem with scrapping
if len(name_box) != len(status_box) or len(name_box) == 0 or len(status_box) == 0: 
    raise RuntimeError("Titles and Status arrays don't match.")
    
# handle the data scrapped
else:
    final_output = "Brandon Sanderson Status Update:"
    index = 0
    # create data string to be sent
    while index < len(name_box):
        final_output += ("\n   " + name_box[index].text + " - " + status_box[index].find('div', attrs={'class': 'after'}).text)
        index += 1

    try:
        save_file = open("lastupdate", "r")
        last_update = save_file.read()
        save_file.close()
    except IOError:
        last_update = ""

    # new update so update and send message(s)
    if last_update != final_output:
        save_file = open("lastupdate", "w")
        save_file.write(final_output)
        save_file.close()
        print(final_output)