import requests
import json
import datetime
import os
import traceback
from bs4 import BeautifulSoup

# name of the html elements to scrape
progress_bar_html_name = 'vc_progress_bar'
name_boxs_html_name = 'vc_label'
status_boxs_html_name = 'vc_label_units'

# get path for project (this is needed to use crontab in linux)
project_path = os.path.dirname(os.path.abspath(__file__))

# set file names
last_update_file = project_path + "/lastupdate"
config_file = project_path + "/config.json"

# specify the url
scrape_url = 'https://brandonsanderson.com/'

def send_texts(message, config_file):
    headers = {
        'Content-Type': 'application/json',
    }
    with open(config_file) as json_file:
        config = json.load(json_file)
        url_base = config['url']
        for user in config['all_users']:
            print(user)
            payload = {
                'number': user['number'],
                'message': message,
                'carrier': user['carrier'],
            }
            text_url = url_base + user['location_path']
            response = requests.post(text_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            print(user['number'], " - ", response.json())

# output for logging            
print("------------------------------------------------------------------------")
print(datetime.datetime.now())

try:
    # query the website and return the html to the variable 'page'
    page = requests.get(scrape_url)

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(page.text, 'html.parser')

    # get progress bar div to limit the page and check
    progress_bar = soup.find(attrs={'class': progress_bar_html_name})
    if progress_bar is None:
        raise RuntimeError("Could not find progress bar with html name " + progress_bar_html_name)
    print("progress_bar:")
    print(progress_bar.prettify())
    print()

    status_boxs = []
    
    # get list of book titles and check name
    name_boxs = progress_bar.find_all(attrs={'class': name_boxs_html_name})
    if name_boxs is None:
        raise RuntimeError("Could not find name box with html name " + name_boxs_html_name)
    # extract the status from the name box for better formatting later
    for name in name_boxs:
        status = name.find(attrs={'class': status_boxs_html_name})
        status_boxs.append(status.extract())

    # if problem with scrapping
    if len(name_boxs) != len(status_boxs) or len(name_boxs) == 0 or len(status_boxs) == 0: 
        raise RuntimeError("NUmber of Titles and Status arrays don't match.")

    # handle the data scrapped
    else:
        final_output = "Brandon Sanderson Status Update:"
        index = 0
        # create data string to be sent
        for name in name_boxs:
            final_output += ("<br>  " + name.text.strip() + " - " + status_boxs[index].text)
            index += 1
        try:
            print()
            save_file = open(last_update_file, "r")
            last_update = save_file.read()
            save_file.close()
        except IOError:
            last_update = ""

        # new update so update and send message(s)
        if last_update != final_output:
            print(final_output)
            send_texts(final_output, config_file)
            save_file = open(last_update_file, "w")
            save_file.write(final_output)
            save_file.close()
except RuntimeError as err: 
    print("Error: " + str(err))
except Exception as err: 
    print("Error: " + str(err))
    traceback.print_exc() 