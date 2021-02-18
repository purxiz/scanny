#### Scanny
Scanny is a tool for keeping track of grocery lists using a barcode scanner. It runs as a flask server, and is primarily designed for use with a raspberry pi and small touch screen. The only required hardware however is a barcode scanner that types the barcode as standard input and then presses enter afterwards.   
The data is stored in a file called db.sqlite, using SQLAlchemy with SQLITE (obviously).  
The server should ideally be run somewhere that it can be publically accessed, since the css handles mobile devices as well as I can be bothered to make it.  
Buttons prefixed with '>' represent links, and take you to another page. Buttons with some other name represent some action.  
The program should be pretty self explanatory.

#### Dependencies and running
The current dependencies are  
* flask
* flask_sqlalchemy

To run in a development environment for testing, simply
```bash
cd scanny
export FLASK_APP=main.py
flask run -h 0.0.0.0
```
I recommend using -h 0.0.0.0 so you can access the webpage from across your LAN during development, especially if you are running the server on a raspberry pi.

If you get an error regarding tables not existing, open a python3 shell with `python3` or just `python` if you're in a virtualenv, then:

```python
from main import db
db.create_all()
exit()
```

This will create the database and tables so you can run the app.

#### Basic Usage
To add grocery items:  
- From the home page, press add
- Scan items using your scanner, follow the prompts.

Removing grocery items is pretty much the same. The oldest item will always be removed first.

You can click on a grocery item on the home page to manually add/remove it.


#### Important Notes
At some points, the program will prompt you to press "Up" to continue. That actually means you have to press the escape key. I am using a very small keyboard for this project and only had an "up" keycap available. In the future I might make these warning messages configurable.

#### Deploying to production
You can deploy however you'd like to deploy a flask app, but the simplest way I've found is to use uWSGI. I've included an ini file, and a sample systemd file. The additional dependencies are uwsgi, venv, and wheel (install via pip in a virtualenv)

I suppose if you're just self hosting on a dedicated raspberry pi, you could also install globally, but you'd have to modify the service file.

Speaking of, you can put scanny.service whereever systemd service files live on your system, for me I'm hosting on Ubuntu, and it's located in `/etc/systemd/system/scanny.service`

after that, running the "production" version of the app should be as simple as 

```bash
sudo systemctl enable scanny.service
sudo systemctl start scanny.service
```
