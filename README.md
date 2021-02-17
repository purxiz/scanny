#### Scanny
Scanny is a tool for keeping track of grocery lists using a barcode scanner. It runs as a flask server, and is primarily designed for use with a raspberry pi and small touch screen. The only required hardware however is a barcode scanner that types the barcode as standard input and then presses enter afterwards.   
The data is stored in a file called db.sqlite, using SQLAlchemy with SQLITE (obviously).  
The server should ideally be run somewhere that it can be publically accessed, since the css handles mobile devices as well as I can be bothered to make it.  
Buttons prefixed with '>' represent links, and take you to another page. Buttons with some other name represent some action.  
The program should be pretty self explanatory.

To run in a development environment for testing, simply
```bash
cd scanny
export FLASK_APP=main.py
flask run -h 0.0.0.0
```
I recommend using -h 0.0.0.0 so you can access the webpage from across your LAN during development, especially if you are running the server on a raspberry pi.

#### Basic Usage
To add grocery items:
	- From the home page, press add
	- Scan items using your scanner, follow the prompts.

#### Important Notes
At some points, the program will prompt you to press "Up" to continue. That actually means you have to press the escape key. I am using a very small keyboard for this project and only had an "up" keycap available. In the future I might make these warning messages configurable.

#### Deploying to production
I'll figure this out when I deploy
