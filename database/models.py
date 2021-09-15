from datetime import datetime
from re import I, L
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, String, Integer, Float, ForeignKey, CheckConstraint, create_engine, Table, tuple_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import update
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql import func
from sqlalchemy_utils import aggregated
from dotenv import load_dotenv

load_dotenv(
    dotenv_path=r'C:\Users\skolmar\Udacity\FNSD\FSND\projects\capstone\starter\credentials.env')

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

Base = declarative_base()


def setup_db(app, database_path=database_path):
    """Connects flask app to SQL database"""
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_drop_and_create_all():
    """Initializes a clean database"""
    db.drop_all()
    db.create_all()
    chem1 = Chemical(name='Acetone', smiles='CC=O', ld50=10.2)
    chem1.insert()
    chem2 = Chemical(name='Ether', smiles='COC', ld50=15)
    chem2.insert()
    chem3 = Chemical(name='Water', smiles='O', ld50=100)
    chem3.insert()
    inv = Inventory(location='NC', chemicals=[chem1, chem2, chem3])
    inv.insert()


association_table = db.Table(
    'association',
    Column(
        'chemical_id',
        Integer,
        ForeignKey('chemicals.id'),
        primary_key=True),
    Column(
        'inventory_id',
        Integer,
        ForeignKey('inventories.id'),
        primary_key=True))


class Chemical(db.Model):
    __tablename__ = 'chemicals'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    smiles = Column(String, nullable=False, unique=True)
    ld50 = Column(Float, nullable=False)
    hazard = Column(Float, nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(
        DateTime(),
        default=datetime.now,
        onupdate=datetime.now)
    # inventories = db.relationship("Inventory", secondary = association_table, backref=db.backref('association', lazy=True), cascade="all, delete")

    def __init__(self, name, smiles, ld50):
        self.name = name
        self.smiles = smiles
        self.ld50 = ld50
        self.hazard = (1 / ld50) / 0.5

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'smiles': self.smiles,
            'ld50': self.ld50,
        }

    def format_full(self):
        return {
            'id': self.id,
            'name': self.name,
            'smiles': self.smiles,
            'ld50': self.ld50,
            'hazard': self.hazard,
        }

    def __repr__(self):
        return f"<Chemical {self.name} {self.smiles} {self.ld50} {self.created_on} {self.updated_on}>"


class Inventory(db.Model):
    __tablename__ = 'inventories'

    id = Column(Integer, primary_key=True)
    location = Column(String, nullable=False)
    created_on = Column(DateTime(), nullable=False, default=datetime.now)
    updated_on = Column(
        DateTime(),
        default=datetime.now,
        onupdate=datetime.now)
    chemicals = db.relationship(
        'Chemical',
        secondary=association_table,
        backref=db.backref(
            'association',
            lazy=True),
        cascade='all,delete')

    @aggregated('chemicals', Column(Float))
    def average_hazard(self):
        return func.avg(Chemical.hazard)

    CheckConstraint('hazard >= 0', name='hazard_positive')

    def __init__(self, location, chemicals):
        self.location = location
        self.chemicals = chemicals

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'location': self.location,
            'hazard': self.average_hazard,
        }

    def format_full(self):
        return {
            'id': self.id,
            'location': self.location,
            'hazard': self.average_hazard,
            'chemicals': [chemical.format() for chemical in self.chemicals]
        }

    def __repr__(self):
        return f"<Inventory {self.location} {self.average_hazard} {self.created_on} {self.updated_on}>"
