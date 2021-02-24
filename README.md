#### Scanny
Scanny is a tool for keeping track of grocery lists using a barcode scanner. It runs as a flask server, and is primarily designed for use with a raspberry pi and small touch screen. The only required hardware however is a barcode scanner that types the barcode as standard input and then presses enter afterwards.   
The data is stored in a file called db.sqlite, using SQLAlchemy with SQLITE (obviously).  
The server should ideally be run somewhere that it can be publically accessed, since the css handles mobile devices as well as I can be bothered to make it.  
(Please note I'm using some really ugly css tricks to detect mobile devices (and keep them working with the on-screen keyboard changin the screen orientation to landscape). You may want to look into the media tags I use in `static/main.css` to get the display working correctly with your device. I'm using pixel ratio. There's a website called cssmediaqueries.com you can access to help differentiate between your devices.)  
Buttons prefixed with '>' represent links, and take you to another page. Buttons with some other name represent some action.  
The program should be pretty self explanatory.

#### Dependencies and running
The current dependencies are  
* flask
* flask_sqlalchemy
* flask_migrate
* flask_login
* python-dotenv

First you will need to create a .env file. it simply needs to have `SECRET_KEY="some_key"` in it. For development, you can use whatever value you like for `some_key`. For production, you should generate a random secret key in whatever manner is preferable to you. I am partial to python's `os.urandom(24)`.

To run in a development environment for testing, simply
```bash
cd scanny
export FLASK_APP=main.py
flask run -h 0.0.0.0
```
I recommend using -h 0.0.0.0 so you can access the webpage from across your LAN during development, especially if you are running the server on a raspberry pi.

If you get an error regarding tables not existing then open a python shell with `python3` or `python` depending on your system, and do

```python
from main import db
db.create_all()
```

This will create the database and tables so you can run the app.

#### Basic Usage
To add grocery items:  
- From the home page, press add
- Scan items using your scanner, follow the prompts.

Removing grocery items is pretty much the same. The oldest item will always be removed first.

You can click on a grocery item on the home page to manually add/remove it.

#### Configuration
Check the config file as I'll probably forget to update this section of the readme, but at the moment only two options are supported. 

require-login: if true, the app will require users to login to view the grocery list. Turn off for local hosted applications unless you've got nosy housemates on your LAN...  
allow-registration: if true, the login screen doubles as a registration screen. If you enter a username that doesn't already have an account, an account will be created with the entered password. It is recommended that you enable this when someone wants to make an account, and then disable it afterwards. For safety, you can make all relevant accounts before exposing your app to the internet. You can also manually make accounts by entering some data into the sqlite3 db.sqlite.

To manually add an account, just insert a new user with whatever username and a hashed and salted password. The password must of the format sha256(salt.encode() + password.encode()) + '-' + salt. I use hashlib for the sha256 function, and uuid.uuid4() for the salt. 

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

this will start the server on a unix socket, then I recommend using nginx or apache to deliver it.
A simple nginx server block might look like:

```
server {
	server_name url.com www.url.com;
	
	location / {
		include uwsgi_params;
		uwsgi_pass unix:/var/www/scanny/scanny.sock;
	}
	
	listen 80;
}
```

This is a minimal working configuration, ideally you'd want to cache the jinja templates and serve them cached, or use a different templating engine that can build to static files. 

However, given the extremely small scope of this project and the expected value of 1-10 users/instance, I don't think that's necessary, so I'm going to call it out of scope.


#### Roadmap
~~The only feature I have planned is to add some very simple sort of login / session handling.~~ (done) 

I don't intend for the data in this app to ever be truly secret, since it's a glorified grocery list, but it would be nice to be minimally protected from people stumbling across your URL and editing your grocery inventory.

Of course, since I'm running this only on my LAN at the moment, this feature will probably not be coming in the immediate future.

I now have 2 more planned features, ~~the ability to edit the names of items~~ (done), ~~and the ability to add items without scanning a barcode... I'd like to keep the 3 fields on every screen and list on the left UI though, so I'll have to figure out how to do that exactly...~~ (done)

~~I think I'll add a third table to associate a pantry_item_id with a name~~ (done)

#### Wishlist
I'll get around to these eventually

- show total added on each item as it's added in current add session on add screen
- Add a 'create grocery list' button or something that lists everything that has gone to 0 in the past configurable amount of time.
