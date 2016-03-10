# Using SQLAlchemy to setup and configure th DB
#############################
# the configuration code used to import modules

# Provides functions and variables used to manipulate parts
# of the python environment
import sys
# Imports SQLAlchemy classes used for mapper code
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String

# used to create the foreign key relationships in the database.
from sqlalchemy.orm import relationship

# Import"declarative_base that will be used in the database configuration code
from sqlalchemy.ext.declarative import declarative_base

# Make an instance of the class
from sqlalchemy import create_engine
Base = declarative_base()


##### Create the tables in the database ######
class Restaurant(Base):
    #  __ underscore "something" __ underscore lets SQLAlchemy
    # know the variables we will use to refer to the tables in the database
    __tablename__ = 'restaurant'

# Parent "Relationship" to MenuItems.
    id = Column(Integer, primary_key=True)
# Setting "nullable = false" indicates that a value must be provided.
    name = Column(String(250), nullable=False)
# "cascade= "delete" will also delete all menu items when a "Restaurant" is deleted.
    menu_item = relationship("MenuItem", backref='restaurant', cascade="all, delete, delete-orphan")

# Setup a JSON friendly response format    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }

# Child "relationship" to Restaurants.
class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))

# Added a table called "picture" which will be used to store image URL's
    picture = Column(String(250))
    image = Column(String(250))
# "ForeignKey" used to associate with the restaurant class.
# Cascade on delete is placed on the parent table "restaurant". 
# Deleting a restaurant will delete any menu items associated.
    restaurant_id = Column(Integer, ForeignKey('restaurant.id' ))



    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
        }

# Create an instance of the "create_engine class and
# Point to a new database called "restaurant.db"
engine = create_engine('sqlite:///catalog.db')

# creates the tables in the database from
# the classes that were created above.
Base.metadata.create_all(engine)
