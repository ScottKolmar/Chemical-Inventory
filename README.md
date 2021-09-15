# Chemical Inventory API

## Capstone Project for Udacity's Full Stack Developer Nanodegree
Heroku Link: http://https://chem-inventory.herokuapp.com/

While running locally: http://localhost:5000

## Getting Started

### Installing Dependencies

#### Python 3.8

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python).

#### Virtual Enviornment

Recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM.

## Running the server

Before running the application locally, make the following changes in the `app.py` file in root directory:
- Replace the following import statements
  ```
    from database.models import ...
    from auth.auth import ...
  ```
  with
  ```
    from .database.models import ...
    from .auth.auth import ...
  ```

To run the server, execute:

```bash
export DATABASE_URL=<database-connection-url>
export FLASK_APP=app.py
flask run --reload
```

Setting the `FLASK_APP` variable to `app.py` directs flask to use the `app.py` file to find the application. 

Using the `--reload` flag will detect file changes and restart the server automatically.

## API Reference

## Getting Started
Base URL: This application can be run locally. The hosted version is at ...

Authentication: This application requires authentication to perform various actions. All the endpoints require
various permissions, except the index endpoint, that are passed via the `Bearer` token.

The application has three different types of roles:
- Chemist
  - can only view, patch, and delete chemicals, and can view inventories
  - has `get:chemicals, patch:chemicals, delete:chemicals, get:inventories` permissions
- Manager
  - can only view chemicals, and view, patch, and delete inventories
  - has `get:chemicals, get:inventories, patch:inventories, delete:inventories` permissions

## Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "error": 404,
    "message": "Resource Not Found.",
    "success": false
}
```

The API will return the following errors based on how the request fails:
 - 400: Bad Request
 - 401: Unauthorized
 - 404: Not Found
 - 422: Unprocessable Entity
 - 500: Internal Server Error

## Endpoints

#### GET /
 - General
   - Index
   - No authentication
 
 - Sample Request
   - `curl -L localhost:5000/`

<details>
<summary>Sample Response</summary>

```
{
    "success": true
}
```

</details>

#### GET /dhemicals
 - General
   - Gets all chemicals
   - Requires `get:chemicals` permission
 
 - Sample Request
   - `curl localhost:5000/chemicals -H "Authorization: Bearer $chemist_token"`

<details>
<summary>Sample Response</summary>

```
{
    "chemicals":[
        {
            "id":1,
            "ld50":10.2,
            "name":"Acetone",
            "smiles":"CCO"
            },
            {
                "id":2,
                "ld50":15.0,
                "name":"Ether",
                "smiles":"COC"
                },
            {
                "id":3,
                "ld50":100.0,
                "name":"Water",
                "smiles":"O"
                }],
    "success":true
    }
```

</details>

#### GET /chemicals/{chemical_id}
 - General
   - Gets full information for a chemical
   - Requires `get:chemicals` permission
 
 - Sample Request
   - `curl localhost:5000/chemicals/1 -H "Authorization: Bearer $chemist_token"`

<details>
<summary>Sample Response</summary>

```
{
    "chemical":{
        "hazard":0.19607843137254904,
        "id":1,
        "ld50":10.2,
        "name":"Acetone",
        "smiles":"CCO"
        },
    "success":true
    } 
```
  
</details>

#### POST /chemicals
 - General
   - Creates a new chemical
   - Requires `post:chemicals` permission
 
 - Request Body
   - name: string, required, unique
   - smiles: string, required, unique
   - ld50: float, required
 
 - Sample Request
   - `curl -X POST localhost:5000/chemicals -H "Content-Type: application/json" -H "Authorization: Bearer $chemist_token" -d '{"name": "Ethanol", "smiles":"CCO", "ld50": 15.2}'`
   - Request Body
     ```
        {
            "name": "Ethanol",
            "smiles": "CCO",
            "ld50": 15.2
        }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "chemical": {
        "id": 4,
        "ld50": 15.2,
        "name": "Ethanol",
        "smiles": "CCO"
    },
    "success": true
}
```
  
</details>

#### PATCH /chemicals/{chemical_id}
 - General
   - Updates information for a chemical
   - Requires `patch:chemical` permission
 
 - Request Body (at least one of the following fields required)
   - name: string, optional
   - smiles: string, optional
   - ld50: float, optional
 
 - Sample Request
   - `curl -X PATCH localhost:5000/chemicals/1 -H "Content-Type: application/json" -H "Authorization: Bearer $chemist_token" -d '{"ld50": 407.5}'`
   - Request Body
     ```
       {
            "ld50": 407.5
       }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "chemical":{
        "id":1,
        "ld50":407.5,
        "name":"Acetone",
        "smiles":"CC=O"
        },
    "success":true
    }
```
  
</details>

#### DELETE /chemicals/{chemical_id}
 - General
   - Deletes a chemical
   - Requires `delete:chemical` permission
   - Deletes mapping to an inventory but does not delete that inventory
 
 - Sample Request
   - `curl -X DELETE localhost:5000/chemicals/4 -H "Authorization: Bearer $chemist_token"`

<details>
<summary>Sample Response</summary>

```
{
    "deleted chemical id":4,
    "success":true
    }
```
  
</details>

#### GET /inventories
 - General
   - Gets all inventories
   - Requires `get:inventories` permission
 
 - Sample Request
   - `curl localhost:5000/inventories -H "Authorization: Bearer $manager_token"`

<details>
<summary>Sample Response</summary>

```
{
    "inventories":[
        {
            "hazard":0.11647058823529415,
            "id":1,
            "location":"NC"
            }],
    "success":true}
```

</details>

#### GET /inventories/{inventory_id}
 - General
   - Gets information for a single inventory
   - Requires `get:inventories` permission
 
 - Sample Request
   - `curl localhost:5000/inventories/1 -H "Authorization: Bearer $manager_token"`

<details>
<summary>Sample Response</summary>

```
{
    "inventory":{
        "chemicals":
        [
            {
                "id":1,
                "ld50":10.2,
                "name":"Acetone",
                "smiles":"CC=O"
                },
                {
                "id":2,
                "ld50":15.0,
                "name":"Ether",
                "ssmiles":"COC"
                },
                {
                "id":3,
                "ld50":100.0,
                "name":"Water",
                "smiles":"O"
                }],
        "hazard":0.11647058823529415,
        "id":1,
        "location":"NC",
        },
    "success":true
    }
```
  
</details>

#### POST /inventories
 - General
   - Creates a new inventory
   - Requires `post:inventories` permission
 
 - Request Body
   - location: string, required
   - chemicals: list of chemical IDs, optional
 
 - Sample Request
   - `curl -X POST localhost:5000/inventories -H "Content-Type: application/json" -H "Authorization: Bearer $manager_token" -d '{"location": "Swaziland", "chemicals": [1,2]}'`
   - Request Body
     ```
        {
            "location": "Swaziland",
            "chemicals": [1,2]
        }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "inventory":{
        "chemicals":
        [
            {
                "id":1,
                "ld50":10.2,
                "name":"Acetone",
                "smiles":"CC=O"
                },
            {
                "id":2,
                "ld50":15.0,
                "name":"Ether",
                "smiles":"COC"
                }],
        "hazard":0.1647058823529412,
        "id":2,
        "location":"Swaziland"
        },
    "success":true
    }
```
  
</details>

#### PATCH /inventory/{inventory_id}
 - General
   - Updates an inventory
   - Requires `patch:inventory` permission
 
 - Request Body (at least one of the following fields required)
   - location: string, optional
   - chemical_ids_to_add: list of chemical IDs, optional
   - chemical_ids_to_remove: list of chemical IDs, optional
 
 - Sample Request
   - `curl -X PATCH localhost:5000/inventories/1 -H "Content-Type: application/json" -H "Authorization: Bearer $manager_token" -d '{"location": "The Moon", "chemicals_to_remove": [2,3]}'`
   - Request Body
     ```
       {
           "location": "The Moon",
           "chemicals_to_remove": [2,3]
           }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "inventory":{
        "chemicals":[
            {
                "id":1,
                "ld50":10.2,
                "name":"Acetone",
                "smiles":"CC=O"
                },
            {
                "id":2,
                "ld50":15.0,
                "name":"Ether",
                "smiles":"COC"
                },
            {
                "id":3,
                "ld50":100.0,
                "name":"Water",
                "smiles":"O"
                }],
        "hazard":0.11647058823529415,
        "id":1,
        "location":"The Moon"
        },
    "success":true}
```
  
</details>

#### DELETE /inventories/{inventory_id}
 - General
   - Deletes an inventory
   - Requires `delete:inventory` permission
 
 - Sample Request
   - `curl -X DELETE localhost:5000/inventories/1 -H "Authorization: Bearer $manager_token"`

<details>
<summary>Sample Response</summary>

```
{
    "deleted inventory id":1,
    "success":true
    }
```
  
</details>

## Testing
For testing the backend, run the following commands (in the exact order):

```
python test.py
```
