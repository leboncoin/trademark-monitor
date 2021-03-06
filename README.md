# Trademark Monitor

A tool to monitor specific keywords on social networks about trademarks.

Actually, only Twitter is monitored and more social networks will be added later.

## How to use Trademark Monitor

* Rename `config.ini.sample` to `config.ini` and configure your options with your mail informations and your Slack webhook if needed.
* You can enable the `standalone` mode in the configuration file to avoid to use the web application (True or False option).
* Install the python requirements: `python3 -m pip install -r requirements.txt`
* Start the monitor script: `python3 trademark-python.py`

### To use the web application
* Disable the `standalone` mode in the `config.ini` file.
* Start the Flask application (web interface): `flask run`
* Add your trademarks and filters in the web application available: `http://127.0.0.1:5000/`

## Next features
* Add the possibility to remove a trademark / keyword
* Add the possibility to ignore spam tweets
* Add more filters options
* Add an authent method
* Clean the code for others developers
* Use an ORM for the database classes
* Edit the web interface to be more user friendly

## Screenshots

![alt text](https://i.ibb.co/DDkSBQW/capture1.png)
![alt text](https://i.ibb.co/B3wj8pD/capture2.png)
![alt text](https://i.ibb.co/PjcjVFB/capture3.png)
