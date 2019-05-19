# Sanderson-Scraper
This [Python 3.0](https://www.python.org/) script is a basic web scraper that will scrape [Brandon Sanderson's webpage](https://brandonsanderson.com/) to check for updates to the status of his current work and send a text message. This code is setup to use [Textbelt](https://textbelt.com/) format, both the paid version and the [self hosted open source version](https://github.com/typpo/textbelt), for other texting services changes will have to be made to the formatting. 

## Getting Started

### Prerequisites

* [Textbelt](https://textbelt.com/)
* [Python 3.0](https://www.python.org/)
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

### Installing

A step by step series of examples that explains how to get the code running.

1. Install all prerequisites listed above. 
	* Create a [Textbelt](https://textbelt.com/) key if using the paid version of otherwise the [open source version](https://github.com/typpo/textbelt) will need to be created, configured and run before the code can send any texts.
2. Create a `config.json` file in the project home directory to have the correct information for the your application.
	* The `config.json` file will be slightly different depending on the version of Textbelt you are using. Below are two example files that show the and example for each. *Note: These example `config.json` files can be found in project repository `example_config_remote.json` and `example_config_self.json`.*
		1. Example `config.json` of paid version of Textbelt:
			```json
			{
				"all_users": [
					{
						"number": 8395555013,
						"location_path": "text"
					},
					{
						"number": 7295558392,
						"location_path": "canada"
					}
				],
				"url": "https://textbelt.com/",
				"selfhost": false,
				"key": "899cfadc90560f185e6f6da20d812790f0348af84Nuu9nvYMeDMzZfsAnXhRUbHz"
			}
			```
		2. Example `config.json` of self hosted version of Textbelt:
			```json
			{
				"all_users": [
					{
						"number": 8395555013,
						"carrier": "tmobile",
						"location_path": "text"
					},
					{
						"number": 7295558392,
						"carrier": "bellmobilitycanada",
						"location_path": "canada"
					}
				],
				"url": "http://192.168.0.1:9090/",
				"selfhost": true
			}
				```
	* More numbers can be added by including them in the `"all_users"` array in the json.
	* The `"carrier"` field is only needed for the self hosted version of Textbelt.
	* The `"key"` field is only needed for the paid version of Textbelt.
	* The `"url"` field is the url to Textbelt for the paid version and the url and the port of the application used for the self hosted version.
	* This file must be in the project folder for the script to function without modifications.
4. The setup should now be complete the script can be run with the following make command from the project home directory.
	```
	python3 scrape.py
	```

	If correctly setup you should see no error messages when run.

## Running the tests

The tests are run using the make command `python3 test.py` in the project home directory.

## Deployment

How to get this up with the crontab

## Built With


## Contributing

Please read [CONTRIBUTING.md](https://github.com/crabbymonkey/nerf-contorller/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/crabbymonkey/nerf-contorller/tags). 

## Authors

* **Ryan Dufrene** - *Initial work* - [crabbymonkey](https://github.com/crabbymonkey)

See also the list of [contributors](https://github.com/crabbymonkey/nerf-contorller/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* *Billie Thompson* ([PurpleBooth](https://github.com/PurpleBooth)) - README.md and CONTRIBUTING.md templates used
