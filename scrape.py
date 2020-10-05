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
last_update_file = project_path + os.path.sep + "lastupdate"
failed_numbers_file_path = project_path + os.path.sep + "failednumbers"
config_file = project_path + os.path.sep + "config.json"

# specify the url
scrape_url = 'https://brandonsanderson.com/'

# what type is of parser to use
soup_parser_type = 'html.parser'

class SandersonStatus:
    # map to store the status (dict here becasue python wants to be special)
    work_status_map = {}

    # add a work to the map
    def add_work(self, work_name, work_progress):
        self.work_status_map[work_name] = work_progress

    # get the whole status map
    def get_work_status_map(self) -> dict:
        return self.work_status_map

    # overwrite the map saved in this object
    def set_work_status_map(self, new_work_status_map):
        self.work_status_map = new_work_status_map

    # comparitor so to compare SandersonStatus objects, for now it just compares the maps
    def __eq__(self, other): 
        if not isinstance(other, SandersonStatus):
            # don't attempt to compare against unrelated types
            return False
        # compare maps
        return self.work_status_map == other.get_work_status_map()

    #TODO: add a json encoder and decoder for this object and use that for saving

# TODO: add the possibility to use paied for textbelt
def send_texts(message, config_file) -> dict:
    # this value is to check if every number errors which means there is a problem with the system
    success = False

    # map to keep track of failed numbers if you want it (not doing anything with that information as of now)
    failed_numbers = {}

    headers = {
        'Content-Type': 'application/json',
    }
    # open config file
    with open(config_file) as json_file:
        # get json from the file
        config = json.load(json_file)
        # get the based url to the textbelt server
        url_base = config['url']
        # create/overwrite the failed numbers
        failed_numbers_file = open(failed_numbers_file_path, "w")

        # loop though all the numbers and send tests
        for user in config['all_users']:
            # creating a var for the number because it gets used a few times
            number = user['number']

            # create teh payload to sent off to textbelt
            payload = {
                'number': number,
                'message': message,
                'carrier': user['carrier'],
            }

            # use the base url for text belt and the location (text is for usa, canada for canada, intl for everyone else) to make sure the api is sent to the correct handler
            text_url = url_base + user['location_path']
            # send the api call that we created as a POST
            response = requests.post(text_url, headers=headers, data=json.dumps(payload))
            # get the status to see if it failed
            response.raise_for_status()
            # create a logging message so it is easier to read
            response_log_str = str(number) + " - " + response.text

            # if it failes
            if response.json()['success'] is False:
                # add failed numbers to file and return dict
                failed_numbers[number] = response.text
                # add failed numeber to the failed name files 
                # TODO: probably want to use the failed_numbers map at the end and jsut apply pretty printing if you want to use the info later, as of now it is this way for easier reading 
                failed_numbers_file.write(response_log_str + "\n")
            # if it succeeds then we know textbelt is working so we can update the success var
            else:
                success = True

            # print for logging
            print(response_log_str)

        # close the file
        failed_numbers_file.close()
        
    # add blank line for logging
    print()

    if not success:
        # if all the text messages failed then there seems to be an error with the textbelt server or the config file
        raise RuntimeError("Could not send any text messages, please check the config.json file, textbelt setup and messages in " + failed_numbers_file_path)

    # return the failed numbers
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
            # use the status_boxs_html_name var to find the status in the name_boxs and take it out and save it separatly as status
            status = name.find(attrs={'class': status_boxs_html_name}).extract()

            # if it cannot find this value then there seems to be a change/issue with the formating, probably invetigate the site to find the issue
            if status is None:
                raise RuntimeError("Could not find status boxs with html name " + status_boxs_html_name + " for the work " + name.text.strip())

            # add the work name and status strings to the return object
            current_status.add_work(name.text.strip(), status.text.strip())
    # if there is a RuntimeError handle it here to fail "gracefully"
    except RuntimeError as err: 
        print("Error: " + str(err))
        traceback.print_exc() 
        sys.exit()
    # probably dont need this but might as well (TODO: try to remove)
    except Exception as err: 
        print("Error: " + str(err))
        traceback.print_exc() 
        sys.exit()
    # return the object that was created
    return current_status

def is_update(current_status):
    try:
        # open file that has the last update and get the json value
        saved_file = open(last_update_file, "r")
        saved_work_status_map_json = saved_file.read()

        # if the file is empty presume this is an update
        if saved_work_status_map_json == "":
            saved_file.close()
            return True

        # get the saved map value
        last_update_work_status_map = json.loads(saved_work_status_map_json)
        
        # don't forget to close the file (TODO: maybe use with open(last_update_file) as saved_file but not sure how that will handle returns in the middle of it so using close())
        saved_file.close()

        # compare the new map and the stored map
        return not current_status.get_work_status_map() == last_update_work_status_map
    except IOError:
        # this usually means it cannot find the file so this will be an update
        return True
    except Exception as err: 
        # probably dont need this but might as well (TODO: try to remove)
        print("Error: " + str(err))
        traceback.print_exc() 
        sys.exit()

def create_update_message(update):
    # handle the data scrapped
    output = "Brandon Sanderson Status Update:"

    # create data string to be sent
    for work in status.get_work_status_map():
        output += ("\n" + work + " - " +  status.get_work_status_map()[work])

    # add url to the end as a source and to link to the site
    output += ("\n" + scrape_url)
    return output
    
def save_update(update):
    # overwrite the last saved value
    save_file = open(last_update_file, "w")
    save_file.write(json.dumps(update.get_work_status_map()))
    save_file.close()

# output for logging            
print("------------------------------------------------------------------------")
print(datetime.datetime.now())
print()

# get values from the site and save in SandersonStatus object
status = get_values()

# check if this new status is an update from the last time this script ran
if is_update(status):
    # create the message that will be sent
    update_message = create_update_message(status)

    # output for logging
    print(update_message.strip())
    print()

    # send text messages
    try:
        # this is a map of failed numbers if you want to do somthing with it
        failed_messages = send_texts(update_message, config_file)
    except FileNotFoundError:
        print("Error: Could not find the config file please make sure it is created and correct")
        sys.exit()
    except RuntimeError as err:
        print("Error: " + str(err))
        sys.exit()

    # save the new update if all is successful
    save_update(status)
else:
    # TODO: retry numbers that failed stored in failednumbers file
    print("No change to the progress")