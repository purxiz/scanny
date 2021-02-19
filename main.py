from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True)

class PantryItem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	item_id = db.Column(db.Integer, db.ForeignKey(Item.id))
	purchase_date = db.Column(db.DateTime, server_default=db.func.now())

class Barcode(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	item_id = db.Column(db.Integer, db.ForeignKey(Item.id))
	code = db.Column(db.String(30))

	
@app.route('/')
def index():
	pantry_items = Item.query.join(PantryItem, isouter=True)\
		.add_columns(Item.name, Item.id, db.func.count(PantryItem.item_id).label('count'))\
		.group_by(Item.id).all()
	return render_template('index.html', pantry_items=pantry_items)

@app.route('/add')
def add():
	pantry_items = PantryItem.query.join(Item)\
		.add_columns(Item.name, PantryItem.purchase_date, Item.id)\
		.order_by(PantryItem.purchase_date.desc())\
		.limit(20).all()
	return render_template('add.html', pantry_items=pantry_items)

@app.route('/rem')
def rem():
	return render_template('rem.html')

@app.route('/item')
def item():
	pantry_items = PantryItem.query.join(Item)\
	.add_columns(Item.name, PantryItem.purchase_date)\
	.order_by(PantryItem.purchase_date)\
	.filter_by(id=request.args.get('id')).all()
	name = Item.query.add_columns(Item.name).filter_by(id=request.args.get('id')).one()
	return render_template('item.html', pantry_items=pantry_items, item=request.args.get('id'), name=name[1])

@app.route('/item_most_likely')
def item_most_likely():
	item = Item.query.add_columns(Item.name).filter(Item.name.startswith(request.args.get('name'))).order_by(Item.name).offset(request.args.get('offset')).first()
	if item is None:
    		return jsonify({ "name": '' })
	return jsonify({ "name" : item[1] })

@app.route('/add_by_id')
def add_by_id():
	pantry_item = PantryItem(item_id=request.args.get('id'))
	db.session.add(pantry_item)
	db.session.commit()
	name = Item.query.add_columns(Item.name).filter_by(id=request.args.get('id')).one()
	return jsonify({ "name": name[1], "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

@app.route('/add_by_barcode')
def add_by_barcode():
	try:
		item = Barcode.query.add_columns(Item.id, Item.name).filter_by(code=request.args.get('code')).join(Item).one()
	except Exception as err:
		return jsonify({ "err": "not_found" })
	pantry_item = PantryItem(item_id=str(item[1]))
	db.session.add(pantry_item)
	db.session.commit()
	return jsonify({ "name" : item[2], "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

@app.route('/add_barcode_and_item')
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
	return jsonify({ "name": item.name, "purchase_date": pantry_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

@app.route('/remove_by_id')
def remove_by_id():
	try: 
		oldest_item = PantryItem.query.order_by(PantryItem.purchase_date).filter_by(item_id=request.args.get('id')).limit(1).one()
	except Exception as err:
		return jsonify({ "err": "none_exists" })
	db.session.delete(oldest_item)
	db.session.commit()
	return jsonify({ "msg": "success" })

@app.route('/remove_by_barcode')
def remove_by_barcode():
	try: 
		oldest_item = PantryItem.query.join(Barcode, PantryItem.item_id == Barcode.item_id).order_by(PantryItem.purchase_date).filter_by(code=request.args.get('code')).limit(1).one()
	except Exception as err:
		return jsonify({ "err": "none_exists" })
	db.session.delete(oldest_item)
	db.session.commit()
	name = Item.query.add_columns(Item.name, Item.id).filter_by(id=oldest_item.item_id).one()
	return jsonify({ "name": name[1], "id": name[2], "purchase_date": oldest_item.purchase_date.strftime('%m-%d-%y %H:%M:%S') })

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True, host='0.0.0.0')
