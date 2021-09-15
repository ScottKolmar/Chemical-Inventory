import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from database.models import setup_db, Chemical, Inventory, db_drop_and_create_all


class ChemicalInventoryTestCase(unittest.TestCase):
    """ Test case class for the chemical inventory API"""

    def setUp(self):
        """ Define variables and setup app"""
        self.invalid_token = 'gkjalkbnlakdbhaiorhboi'
        self.chemist_token = os.environ['chemist_token']
        self.manager_token = os.environ['manager_token']
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)
        db_drop_and_create_all()

        # TEST CHEMICALS

        self.VALID_NEW_CHEMICAL = {
            "name": "Acetic Acid",
            "smiles": "CC=OOH",
            "ld50": 32.3
        }

        self.INVALID_NEW_CHEMICAL = {
            "name": "Acetic Acid"
        }

        self.VALID_PATCH_CHEMICAL = {
            "ld50": 40.1
        }

        self.INVALID_PATCH_CHEMICAL = {
            "name": ""
        }

        # TEST INVENTORIES

        self.VALID_INVENTORY = {
            "location": "Swaziland",
            "chemicals": [1, 2, 3]
        }

        self.INVALID_INVENTORY = {
            "chemicals": [1]
        }

        self.VALID_PATCH_INVENTORY = {
            "location": "The Realm of Gondor",
            "chemical_ids_to_remove": [1]
        }

        self.INVALID_PATCH_INVENTORY = {
            "location": ""
        }

        # Binds app to context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        """ Executed after each test"""
        pass

# ------------------
# PERMISSION TESTS
# ------------------

    def test_index(self):
        """ Test for GET / """
        res = self.client().get('/')
        data = json.loads(res.data)

        self.assertTrue(data['success'])

    def test_fail_401_api_call_without_token(self):
        """ Test for failure without token"""
        res = self.client().get('/chemicals')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Authorization header is required.")

    def test_fail_403_post_chemicals_with_manager_permissions(self):
        """ Test for failure to post chemicals with manager permissions """
        res = self.client().post('/chemicals', headers={
            'Authorization': f"Bearer {self.manager_token}"
        }, json=self.VALID_NEW_CHEMICAL)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'],
            "Permission not in Permissions header.")

    def test_fail_403_delete_chemicals_with_manager_permissions(self):
        """ Test for failure to post chemicals with manager permissions """
        res = self.client().delete('/chemicals/1', headers={
            'Authorization': f"Bearer {self.manager_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'],
            "Permission not in Permissions header.")

    def test_fail_403_post_inventories_with_chemist_permissions(self):
        """ Test for failure to post inventories with chemist permissions """
        res = self.client().post('/inventories', headers={
            'Authorization': f"Bearer {self.chemist_token}"
        }, json=self.VALID_INVENTORY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'],
            "Permission not in Permissions header.")

    def test_fail_403_delete_inventories_with_chemist_permissions(self):
        """ Test for failure to delete inventories with chemist permissions """
        res = self.client().delete('/inventories/1', headers={
            "Authorization": f'Bearer {self.chemist_token}'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'],
            "Permission not in Permissions header.")

# ---------------
# CHEMICAL TESTS
# ---------------

    def test_get_chemicals(self):
        """ Pass test for GET /chemicals """
        res = self.client().get('/chemicals', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('chemicals', data)
        self.assertTrue(len(data['chemicals']))

    def test_get_chemical_by_id(self):
        """ Pass test for GET /chemicals/<chemical_id> """
        res = self.client().get('/chemicals/1', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('chemical', data)

    def test_fail_404_get_chemical_invalid_id(self):
        """ Test for failure to GET /chemicals/<chemical_id> with invalid id"""
        res = self.client().get('/chemicals/99', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_post_chemical(self):
        """ Pass test for POST /chemicals """
        res = self.client().post('/chemicals', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        }, json=self.VALID_NEW_CHEMICAL)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('chemical', data)
        self.assertEqual(data['chemical']['name'], "Acetic Acid")

    def test_fail_422_post_invalid_chemical(self):
        """ Test for failure to POST invalid chemical to /chemicals"""
        res = self.client().post('/chemicals', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        }, json=self.INVALID_NEW_CHEMICAL)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_patch_chemical(self):
        """ Pass test for PATCH /chemicals/<chemical_id> """
        res = self.client().patch('/chemicals/1', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        }, json=self.VALID_PATCH_CHEMICAL)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('chemical', data)
        self.assertEqual(
            data['chemical']['ld50'],
            self.VALID_PATCH_CHEMICAL['ld50'])

    def test_fail_404_patch_chemical_with_invalid_id(self):
        """ Test for failure to patch a chemical with invalid id"""
        res = self.client().patch('/chemicals/99', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        }, json=self.VALID_PATCH_CHEMICAL)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_delete_chemical(self):
        """ Pass test for DELETE /chemicals/<chemical_id>"""
        res = self.client().delete('/chemicals/1', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('deleted chemical id', data)
        self.assertEqual(data['deleted chemical id'], 1)

    def test_fail_404_delete_chemical_invalid_id(self):
        """ Test for failure to DELETE /chemicals/<chemical_id> with invalid id"""
        res = self.client().delete('/chemicals/99', headers={
            "Authorization": f"Bearer {self.chemist_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

# --------------------
# INVENTORY TESTS
# --------------------

    def test_get_inventories(self):
        """ Pass test for GET /inventories"""
        res = self.client().get('/inventories', headers={
            "Authorization": f"Bearer {self.manager_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('inventories', data)

    def test_get_inventories_by_id(self):
        """ Pass test for GET /inventories/<inventory_id>"""
        res = self.client().get('/inventories/1', headers={
            "Authorization": f"Bearer {self.manager_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('inventory', data)
        self.assertEqual(data['inventory']['id'], 1)

    def test_fail_404_get_inventories_invalid_id(self):
        """ Test failure to GET /inventories/<inventory_id> with invalid id"""
        res = self.client().get('/inventories/99', headers={
            "Authorization": f"Bearer {self.manager_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_post_inventory(self):
        """ Pass test for POST /inventories"""
        res = self.client().post('/inventories', headers={
            "Authorization": f"Bearer {self.manager_token}"
        }, json=self.VALID_INVENTORY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('inventory', data)
        self.assertEqual(data['inventory']['location'], 'Swaziland')
        self.assertEqual(len(data['inventory']['chemicals']), 3)

    def test_fail_422_post_invalid_inventory(self):
        """ Test for failure to POST invalid inventory to /inventories"""
        res = self.client().post('/inventories', headers={
            "Authorization": f"Bearer {self.manager_token}"
        }, json=self.INVALID_INVENTORY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_patch_inventory(self):
        """ Test for PATCH /inventory/<inventory_id>"""
        res = self.client().patch('/inventories/1', headers={
            "Authorization": f"Bearer {self.manager_token}"
        }, json=self.VALID_PATCH_INVENTORY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertEqual(
            data['inventory']['location'],
            self.VALID_PATCH_INVENTORY['location'])

    def test_fail_404_patch_inventory_with_invalid_id(self):
        """ Test for failure to patch an inventory with invalid id"""
        res = self.client().patch('/inventories/99', headers={
            "Authorization": f"Bearer {self.manager_token}"
        }, json=self.VALID_PATCH_INVENTORY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_delete_inventory(self):
        """ Test for DELETE /inventory/<inventory_id>"""
        res = self.client().delete('/inventories/1', headers={
            "Authorization": f"Bearer {self.manager_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data['success'])
        self.assertIn('deleted inventory id', data)
        self.assertEqual(data['deleted inventory id'], 1)

    def test_fail_404_delete_inventory_with_invalid_id(self):
        """ Test for failure to DELETE /inventories/<inventory_id> with invalid id"""
        res = self.client().delete('/inventories/99', headers={
            "Authorization": f"Bearer {self.manager_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

# -------------
# END TESTS
# -------------


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
