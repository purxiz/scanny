from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PantryItem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	purchase_date = db.Column(db.DateTime, server_default=db.func.now())

class Barcode(db.Model):
	code = db.Column(db.String(30), primary_key=True)
	name = db.Column(db.String(100), db.ForeignKey(PantryItem.name))
	
@app.route('/')
def index():
	names = Barcode.query.group_by(Barcode.name).subquery()
	pantry_items = PantryItem.query.join(names, PantryItem.name == names.c.name)\
		.add_columns(PantryItem.name, db.func.count().label('count'))\
		.group_by(PantryItem.name).all()
	return render_template('index.html', pantry_items=pantry_items)

@app.route('/add')
def add():
	pantry_items = PantryItem.query.order_by(PantryItem.purchase_date.desc()).limit(20)
	return render_template('add.html', pantry_items=pantry_items)

@app.route('/rem')
def rem():
	return render_template('rem.html')

@app.route('/item')
def item():
	pantry_items = PantryItem.query.order_by(PantryItem.purchase_date).filter_by(name=request.args.get('name')).all()
	return render_template('item.html', pantry_items=pantry_items, item=request.args.get('name'))

@app.route('/add_by_name')
def add_by_name():
	pantry_item = PantryItem(name=request.args.get('name'))
	db.session.add(pantry_item)
	db.session.commit()
	return jsonify({ "name": pantry_item.name, "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

@app.route('/add_by_barcode')
def add_by_barcode():
	name_code = Barcode.query.filter_by(code=request.args.get('code')).all()
	if(len(name_code) < 1):
		return jsonify({ "err": "not_found" })
	pantry_item = PantryItem(name=name_code[0].name)
	db.session.add(pantry_item)
	db.session.commit()
	return jsonify({ "name" : pantry_item.name, "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

@app.route('/add_barcode_and_item')
def add_barcode_and_item():
	barcode = Barcode(name=request.args.get('name'), code=request.args.get('code'))
	pantry_item = PantryItem(name=request.args.get('name'))
	db.session.add(barcode)
	db.session.add(pantry_item)
	try:
		db.session.commit()
	except Exception as err:
		return jsonify({ "err": "unique_violation" });
	return jsonify({ "name": pantry_item.name, "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

@app.route('/remove_by_name')
def remove_by_name():
	try: 
		oldest_item = PantryItem.query.order_by(PantryItem.purchase_date).filter_by(name=request.args.get('name')).limit(1).one()
	except Exception as err:
		return jsonify({ "err": "none_exists" })
	db.session.delete(oldest_item)
	db.session.commit()
	return jsonify({ "msg": "success" })

@app.route('/remove_by_barcode')
def remove_by_barcode():
	try: 
		oldest_item = PantryItem.query.join(Barcode).order_by(PantryItem.purchase_date).filter_by(code=request.args.get('code')).limit(1).one()
	except Exception as err:
		return jsonify({ "err": "none_exists" })
	db.session.delete(oldest_item)
	db.session.commit()
	return jsonify({ "name": oldest_item.name, "purchase_date": oldest_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True, host='0.0.0.0')
