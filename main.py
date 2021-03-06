from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from dotenv import load_dotenv
from hashlib import sha256
from uuid import uuid4
import config
import sys
import os

load_dotenv()

app = Flask(__name__)
app.config['LOGIN_DISABLED'] = not config.require_login
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login_manager = LoginManager()
login_manager.init_app(app)

#########################
# 	 Template Config	#
#########################

@app.context_processor
def inject_config():
	return dict(config=config)

#########################
#	Utility Functions	#
#########################

def hash_password(password):
	salt = uuid4().hex
	return sha256(salt.encode() + password.encode()).hexdigest() + '-' + salt

def check_hashed_password(password, stored_password):
	hash, salt = stored_password.split('-')
	return hash == sha256(salt.encode() + password.encode()).hexdigest()


#########################
#	Database Classes 	#
#########################

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), unique=True)
	password = db.Column(db.String(100))

class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True)
	user_id = db.Column(db.String(30), db.ForeignKey(User.id))

class PantryItem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	item_id = db.Column(db.Integer, db.ForeignKey(Item.id))
	purchase_date = db.Column(db.DateTime, server_default=db.func.now())
	user_id = db.Column(db.String(30), db.ForeignKey(User.id))

class Barcode(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	item_id = db.Column(db.Integer, db.ForeignKey(Item.id))
	code = db.Column(db.String(30))
	user_id = db.Column(db.String(30), db.ForeignKey(User.id))

#########################
#	 Login Handlers	    #
#########################

@login_manager.user_loader
def load_user(user_id):
	return User.query.filter_by(id=user_id).first()

@login_manager.unauthorized_handler
def unauthorized_handler():
	message = 'Login/Register' if config.allow_registration else 'Login'
	return render_template('login.html', message=message)

@app.route('/login_or_register')
def login_or_register():
	user = User.query.filter_by(username=request.args.get('username')).first()
	if user is None and config.allow_registration:
		user = User(username=request.args.get('username'), password=hash_password(request.args.get('password')))
		db.session.add(user)
		db.session.commit()
		login_user(user)
		return jsonify({ "redirect": "/" })
	elif user:
		if check_hashed_password(request.args.get('password'), user.password):
			login_user(user)
			return jsonify({ "redirect": "/" })
		else:
			return jsonify({ "err": "password" })
	return jsonify({ "err": "username" })

@app.route('/logout')
def logout():
	logout_user();
	return redirect(url_for('index'))



#########################
#	 Rendered Routes	#
#########################

@app.route('/')
@login_required
def index():
	pantry_items = Item.query.join(PantryItem, isouter=True)\
		.add_columns(Item.name, Item.id, db.func.count(PantryItem.item_id).label('count'))\
		.group_by(Item.id).order_by(Item.name).all()
	return render_template('index.html', user=getattr(current_user, 'username', ''), pantry_items=pantry_items)

@app.route('/rename')
@login_required
def rename():
	item = Item.query.filter_by(id=request.args.get('item_id')).one()
	return render_template('rename.html', user=getattr(current_user, 'username', ''), name=item.name, id=request.args.get('item_id'))

@app.route('/add')
@login_required
def add():
	pantry_items = PantryItem.query.join(Item)\
		.add_columns(Item.name, PantryItem.purchase_date, Item.id)\
		.order_by(PantryItem.purchase_date.desc())\
		.limit(20).all()
	return render_template('add.html', user=getattr(current_user, 'username', ''), pantry_items=pantry_items)

@app.route('/rem')
@login_required
def rem():
	return render_template('rem.html', user=getattr(current_user, 'username', ''))

@app.route('/item')
@login_required
def item():
	pantry_items = PantryItem.query.join(Item)\
	.add_columns(Item.name, PantryItem.purchase_date)\
	.order_by(PantryItem.purchase_date)\
	.filter_by(id=request.args.get('id')).all()
	name = Item.query.add_columns(Item.name).filter_by(id=request.args.get('id')).one()
	return render_template('item.html', user=getattr(current_user, 'username', ''), pantry_items=pantry_items, item=request.args.get('id'), name=name[1])

#########################
#	    Add Routes	    #
#########################

@app.route('/add_by_id')
@login_required
def add_by_id():
	pantry_item = PantryItem(item_id=request.args.get('id'))
	db.session.add(pantry_item)
	db.session.commit()
	name = Item.query.add_columns(Item.name).filter_by(id=request.args.get('id')).one()
	return jsonify({ "name": name[1], "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

@app.route('/add_by_barcode')
@login_required
def add_by_barcode():
	try:
		item = Barcode.query.add_columns(Item.id, Item.name).filter_by(code=request.args.get('code')).join(Item).one()
	except Exception as err:
		return jsonify({ "err": "not_found" })
	pantry_item = PantryItem(item_id=str(item[1]))
	db.session.add(pantry_item)
	db.session.commit()
	return jsonify({ "name" : item[2], "id": item.id, "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

@app.route('/add_barcode_and_item')
@login_required
def add_barcode_and_item():
	name = request.args.get('name').strip('\n')
	item = Item.query.filter_by(name=name).first();
	if item is None:
		item = Item(name=name)
		db.session.add(item)
		db.session.commit()
	barcode = Barcode(item_id=item.id, code=request.args.get('code'))
	pantry_item = PantryItem(item_id=item.id)
	db.session.add(barcode)
	db.session.add(pantry_item)
	db.session.commit()
	return jsonify({ "name": item.name, "id": item.id, "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

#########################
#	  Rename Routes		#
#########################

@app.route('/rename_by_id')
@login_required
def rename_by_id():
	item = Item.query.filter_by(id=request.args.get('id')).one()
	item.name = request.args.get('name').strip('\n')
	try:
		db.session.commit()
	except Exception as err:
		return jsonify({ "err": "unique_violation" })
	return jsonify({ "name": item.name })

@app.route('/rename_by_name')
@login_required
def rename_by_name():
	barcodes = Barcode.query.filter_by(item_id=request.args.get('id')).all()
	pantry_items = PantryItem.query.filter_by(item_id=request.args.get('id')).all()
	item = Item.query.filter_by(name=request.args.get('name').strip('\n')).one()
	for barcode in barcodes:
		barcode.item_id = item.id
	for pantry_item in pantry_items:
		pantry_item.item_id = item.id
	item_to_remove = Item.query.filter_by(id=request.args.get('id')).one()
	db.session.delete(item_to_remove)
	db.session.commit()
	return jsonify({"redirect": "/item?id=" + str(item.id)})

#########################
#	  Remove Routes		#
#########################

@app.route('/remove_by_id')
@login_required
def remove_by_id():
	try: 
		oldest_item = PantryItem.query.order_by(PantryItem.purchase_date).filter_by(item_id=request.args.get('id')).limit(1).one()
	except Exception as err:
		return jsonify({ "err": "none_exists" })
	db.session.delete(oldest_item)
	db.session.commit()
	return jsonify({ "msg": "success" })

@app.route('/remove_by_barcode')
@login_required
def remove_by_barcode():
	try: 
		oldest_item = PantryItem.query.join(Barcode, PantryItem.item_id == Barcode.item_id).order_by(PantryItem.purchase_date).filter_by(code=request.args.get('code')).limit(1).one()
	except Exception as err:
		return jsonify({ "err": "none_exists" })
	db.session.delete(oldest_item)
	db.session.commit()
	name = Item.query.add_columns(Item.name, Item.id).filter_by(id=oldest_item.item_id).one()
	return jsonify({ "name": name[1], "id": name[2], "purchase_date": oldest_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

#########################
#	  Utility Routes	#
#########################

@app.route('/item_most_likely')
@login_required
def item_most_likely():
	item = Item.query.add_columns(Item.name).filter(Item.name.startswith(request.args.get('name'))).order_by(Item.name).offset(request.args.get('offset')).first()
	if item is None:
    		return jsonify({ "name": '' })
	return jsonify({ "name" : item[1] })

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True, host='0.0.0.0')
