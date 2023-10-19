from flask import Flask, json, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from flask_swagger_ui import get_swaggerui_blueprint
import os

app=Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///' + os.path.join(basedir, 'scooters.db')

# Making a blueprint for Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app-name': 'Electro Scooter API'
    }
)
app.register_blueprint(swagger_blueprint, url_prefix = SWAGGER_URL)

db=SQLAlchemy(app)

# Class for the table "electr_scooters"
class electro_scooters(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    battery_level=db.Column(db.Float(),nullable=False)

# Class for the corresponding schema
class electro_scootersSchema(Schema):
    id=fields.Integer()
    name=fields.String()
    battery_level=fields.Float()

# Informative default page
@app.route('/')
def landing_page():
    return '<!DOCTYPE html><head></head><body><h2>Main page</h2><p>Check out the Swagger UI @ localhost:5000/swagger/</p></body>'

# Route for accessing Swagger UI itself
@app.route('/swagger')
def swagger():
    with open('/static/swagger.json', 'r') as f:
        return jsonify(json.load(f))

# Defining the routes for each request
@app.route('/api/electro-scooters',methods=['POST'])
def create_scooter():
    data = request.get_json()

    new_scooter = electro_scooters(
        name = data.get('name'),
        battery_level = data.get('battery_level')
    )

    db.session.add(new_scooter)
    db.session.commit()

    data = electro_scootersSchema().dump(new_scooter)

    return jsonify(data),201

@app.route('/api/electro-scooters/<int:scooter_id>',methods=['GET'])
def get_scooter(scooter_id):
    scooter = electro_scooters.query.get_or_404(scooter_id)

    data = electro_scootersSchema().dump(scooter)

    return jsonify(data),200

@app.route('/api/electro-scooters/<int:scooter_id>',methods=['PUT'])
def update_scooter(scooter_id):
    scooter = electro_scooters.query.get_or_404(scooter_id)

    data = request.get_json()

    scooter.name = data.get('name')
    scooter.battery_level = data.get('battery_level')

    db.session.commit()

    scooter_data = electro_scootersSchema().dump(scooter)

    return jsonify(scooter_data),200

@app.route('/api/electro-scooters/<int:scooter_id>',methods=['DELETE'])
def delete_scooter(scooter_id):
    scooter = electro_scooters.query.get_or_404(scooter_id)

    db.session.delete(scooter)
    db.session.commit()

    return jsonify({"message":"Deletion Successful"}),200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"message":"Resource Not Found"}),404

@app.errorhandler(500)
def internal_server(error):
    return jsonify({"message":"Internal Server Error"}),500

if __name__ == '__main__':
    app.run()
