import sys
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
failed_numbers_file_path = project_path + "/failednumbers"
config_file = project_path + "/config.json"

# specify the url
scrape_url = 'https://brandonsanderson.com/'

# what type is of parser to use
soup_parser_type = 'html.parser'

class SandersonStatus:
    work_status_map = {}
    def add_work(self, work_name, work_progress):
        self.work_status_map[work_name] = work_progress

    def get_work_status_map(self) -> dict:
        return self.work_status_map

    def set_work_status_map(self, new_work_status_map):
        self.work_status_map = new_work_status_map

    def __eq__(self, other): 
        if not isinstance(other, SandersonStatus):
            # don't attempt to compare against unrelated types
            return False
        return self.work_status_map == other.get_work_status_map()

    #TODO: add a json encoder and decoder for this object and use that for saving

def send_texts(message, config_file) -> dict:
    success = False
    failed_numbers = []
    headers = {
        'Content-Type': 'application/json',
    }
    with open(config_file) as json_file:
        config = json.load(json_file)
        url_base = config['url']
        failed_numbers_file = open(failed_numbers_file_path, "w")
        for user in config['all_users']:
            payload = {
                'number': user['number'],
                'message': message,
                'carrier': user['carrier'],
            }
            text_url = url_base + user['location_path']
            response = requests.post(text_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            response_log_str = str(user['number']) + " - " + response.text
            if response.json()['success'] is False:
                failed_numbers.append(response_log_str)
                failed_numbers_file.write(response_log_str + "\n")
            else:
                success = True
            # print for logging
            print(response_log_str)
        failed_numbers_file.close()
    print()
    if not success:
        raise RuntimeError("Could not send any text messages, please check the config.json file and textbelt setup")
    return failed_numbers

def get_values():
    # class to hold the current status information
    current_status = SandersonStatus()

    try:
        # query the website and return the html to the variable 'page'
        page = requests.get(scrape_url)
        # parse the html using beautiful soup and store in variable `soup`
        soup = BeautifulSoup(page.text, soup_parser_type)        
        # get list of book titles and check name (NOTE: this is where to update if the website elements' format is updated again)
        name_boxs = soup.find_all(attrs={'class': name_boxs_html_name})
        if name_boxs is None:
            raise RuntimeError("Could not find name box with html name " + name_boxs_html_name)
        # extract the status from the name box and add them to the return object
        for name in name_boxs:
            status = name.find(attrs={'class': status_boxs_html_name}).extract()
            if status is None:
                raise RuntimeError("Could not find status boxs with html name " + status_boxs_html_name + " for the work " + name.text.strip())
            current_status.add_work(name.text.strip(), status.text.strip())
    except RuntimeError as err: 
        print("Error: " + str(err))
        traceback.print_exc() 
        sys.exit()
    except Exception as err: 
        print("Error: " + str(err))
        traceback.print_exc() 
        sys.exit()

    return current_status

def is_update(current_status):
    try:
        saved_file = open(last_update_file, "r")
        saved_work_status_map_json = saved_file.read()
        if saved_work_status_map_json == "":
            saved_file.close()
            return True
        last_update_work_status_map = json.loads(saved_work_status_map_json)
        saved_file.close()
            
        return not current_status.get_work_status_map() == last_update_work_status_map
    except IOError:
        # this usually means it cannot find the file so this will be an update
        return True
    except Exception as err: 
        print("Error: " + str(err))
        traceback.print_exc() 
        sys.exit()


def create_update_message(update):
    # handle the data scrapped
    output = "Brandon Sanderson Status Update:"
    # create data string to be sent
    for work in status.get_work_status_map():
        output += ("\n" + work + " - " +  status.get_work_status_map()[work])
    return output
    
def save_update(update):
    save_file = open(last_update_file, "w")
    save_file.write(json.dumps(update.get_work_status_map()))

# output for logging            
print("------------------------------------------------------------------------")
print(datetime.datetime.now())
print()

status = get_values()

if is_update(status):
    update_message = create_update_message(status)
    # output for logging
    print(update_message.strip())
    print()
    # send text messages
    try:
        failed_messages = send_texts(update_message, config_file)
    except FileNotFoundError:
        print("Error: Could not find the config file please make sure it is created and correct")
        sys.exit()
    except RuntimeError as err:
        print("Error: " + str(err))
        sys.exit()
    # save the new update
    save_update(status)
else:
    print("No change to the progress")