# Trademark Monitor

A tool to monitor specific keywords on social networks about trademarks.

Actually, only Twitter is monitored and more social networks will be added later.

## How to use Trademark Monitor

* Rename `config.ini.sample` to `config.ini` and configure your options with your mail informations and your Slack webhook if needed.
* Install the python requirements: `python3 -m pip install -r requirements.txt`
* Start the Flask application (web interface): `flask run`
* Add your trademarks and filters in the web application available: `http://127.0.0.1:5000/`
* Start the monitor script: `python3 trademark-python.py`
