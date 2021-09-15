import json
import os
import re
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql.type_api import INDEXABLE
from database.models import setup_db, db_drop_and_create_all, Chemical, Inventory, association_table
from auth.auth import AuthError, requires_auth

# -----------------
# APP SETUP
# ----------------


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Create clean database
    db_drop_and_create_all()

    # Set up CORS
    cors = CORS(app, resources={
        r"localhost:/5000*": {
            "origins": "*"
        }
    })

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS'
        )
        return response

    # -------------------
    # ROUTES
    # -------------------

    @app.route('/')
    def index():
        return jsonify({
            "success": True,
        })

    # -------------------
    # CHEMICALS
    # -------------------

    @app.route('/chemicals', methods=['GET'])
    @requires_auth("get:chemicals")
    def retrieve_chemicals(permission):

        try:
            chemicals = Chemical.query.order_by(Chemical.id).all()
            chemicals = [chemical.format() for chemical in chemicals]

            if chemicals is None:
                abort(404)

            return jsonify({
                'success': True,
                'chemicals': chemicals
            })

        except BaseException:
            abort(400)

    @app.route('/chemicals', methods=['POST'])
    @requires_auth('post:chemicals')
    def create_chemical(permission):
        body = request.get_json()

        if 'name' not in body or 'smiles' not in body or 'ld50' not in body:
            abort(422)

        name = body.get('name', None)
        smiles = body.get('smiles', None)
        ld50 = body.get('ld50', None)

        try:
            chemical = Chemical(name=name, smiles=smiles, ld50=ld50)
            chemical.insert()

            return jsonify({
                'success': True,
                'chemical': chemical.format()
            })

        except BaseException:
            abort(422)

    @app.route('/chemicals/<int:chemical_id>', methods=['GET'])
    @requires_auth('get:chemicals')
    def retrieve_chemical(permission, chemical_id):

        chemical = Chemical.query.get_or_404(chemical_id)

        return jsonify({
            'success': True,
            'chemical': chemical.format_full()
        })

    @app.route('/chemicals/<int:chemical_id>', methods=['PATCH'])
    @requires_auth('patch:chemicals')
    def patch_chemical(permission, chemical_id):

        chemical = Chemical.query.filter(
            Chemical.id == chemical_id).one_or_none()
        if chemical is None:
            abort(404)

        body = request.get_json()

        if 'name' in body:
            chemical.body = body['name']

        if 'smiles' in body:
            chemical.smiles = body['smiles']

        if 'ld50' in body:
            chemical.ld50 = body['ld50']

        try:
            chemical.update()

            return jsonify({
                'success': True,
                'chemical': chemical.format()
            })

        except BaseException:
            abort(422)

    @app.route('/chemicals/<int:chemical_id>', methods=['DELETE'])
    @requires_auth('delete:chemicals')
    def delete_chemical(permission, chemical_id):

        chemical = Chemical.query.filter(
            Chemical.id == chemical_id).one_or_none()
        if chemical is None:
            abort(404)

        try:
            chemical.delete()

            return jsonify({
                'success': True,
                'deleted chemical id': chemical_id
            })

        except BaseException:
            abort(422)

    # ---------------------
    # INVENTORIES
    # ---------------------

    @app.route('/inventories', methods=['GET'])
    @requires_auth('get:inventories')
    def retrieve_inventories(permission):
        try:
            inventories = Inventory.query.order_by(Inventory.id).all()
            inventories = [inventory.format() for inventory in inventories]

            if inventories is None:
                abort(404)

            return jsonify({
                'success': True,
                'inventories': inventories
            })

        except BaseException:
            abort(400)

    @app.route('/inventories', methods=['POST'])
    @requires_auth('post:inventories')
    def create_inventory(permission):
        body = request.get_json()

        if 'location' not in body:
            abort(422)

        location = body.get('location', None)
        chemical_ids = body.get('chemicals')
        chemicals = []
        for id in chemical_ids:
            chemical = Chemical.query.filter(Chemical.id == id).one_or_none()
            if chemical is None:
                abort(400)
            chemicals.append(chemical)

        try:
            inventory = Inventory(location=location, chemicals=chemicals)
            inventory.insert()

            return jsonify({
                'success': True,
                'inventory': inventory.format_full()
            })

        except BaseException:
            abort(400)

    @app.route('/inventories/<int:inventory_id>', methods=['GET'])
    @requires_auth('get:inventories')
    def retrieve_inventory(permission, inventory_id):

        inventory = Inventory.query.get_or_404(inventory_id)

        # inventory_chemicals = inventory.chemicals

        return jsonify({
            'success': True,
            'inventory': inventory.format_full()
        })

    @app.route('/inventories/<int:inventory_id>', methods=['PATCH'])
    @requires_auth('patch:inventories')
    def patch_inventory(permission, inventory_id):

        inventory = Inventory.query.filter(
            Inventory.id == inventory_id).one_or_none()
        if inventory is None:
            abort(404)

        body = request.get_json()

        if 'location' in body:
            inventory.location = body['location']

        if 'chemical_ids_to_add' in body:
            chemical_ids_to_add = body['chemical_ids_to_add']
            for id in chemical_ids_to_add:
                chemical = Chemical.query.filter(
                    Chemical.id == id).one_or_none()
                if chemical is None:
                    abort(400)
                inventory.chemicals.append(chemical)

        if 'chemical_ids_to_remove' in body:
            chemical_ids_to_remove = body['chemical_ids_to_remove']
            for id in chemical_ids_to_remove:
                chemical = Chemical.query.filter(
                    Chemical.id == id).one_or_none()
                if chemical is None:
                    abort(400)
                inventory.chemicals.remove(chemical)
        try:
            inventory.update()

            return jsonify({
                'success': True,
                'inventory': inventory.format_full()
            })

        except BaseException:
            abort(400)

    @app.route('/inventories/<int:inventory_id>', methods=['DELETE'])
    @requires_auth('delete:inventories')
    def delete_inventory(permission, inventory_id):
        inventory = Inventory.query.filter(
            Inventory.id == inventory_id).one_or_none()
        if inventory is None:
            abort(404)

        try:
            inventory.delete()

            return jsonify({
                'success': True,
                'deleted inventory id': inventory.id
            })

        except BaseException:
            abort(400)

    # -----------------------
    # ERROR HANDLERS
    # -----------------------

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": error.code,
            "message": error.description
        }), error.code

    @app.errorhandler(401)
    def unauthorized_request(error):
        return jsonify({
            "success": False,
            "error": error.code,
            "message": error.description
        }), error.code

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            "error": error.code,
            "message": error.description
        }), error.code

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": error.code,
            "message": error.description
        }), error.code

    @app.errorhandler(422)
    def unprocessable_request(error):
        return jsonify({
            "success": False,
            "error": error.code,
            "message": error.description
        }), error.code

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": error.code,
            "message": error.description
        }), error.code

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
