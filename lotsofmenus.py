# CRUD operations with SQLAlchemy on an SQLite
################################
# import SQLAlchemy functions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Import the classes from the database.
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine


# Establishes communication between our
# python code executions and the database we just created.
DBSession = sessionmaker(bind=engine)


# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Table for Quadcopter Frames within the  class "Restaurant" in the database.
restaurant1 = Restaurant(name="Quadcopter Frames")
# "session.add" adds the object "restaurant1" to a staging zone.
session.add(restaurant1)
# "session.commit" will add the object to the database.
session.commit()


# Create a object in the MenuItem table associated with "restaurant1".


menuItem2 = MenuItem(name="Quadcopter",
                     description="Very stable drone air frame.",
                     price="$7.50",
                     picture="http://www.firstquadcopter.com/wp-content/uploads/2014/12/JJRC-H8C-quadcopter.jpg",
                     restaurant=restaurant1)
session.add(menuItem2)
session.commit()


# Create more objects in the MenuItem table associated with "restaurant1".


menuItem1 = MenuItem(name="Tricopter",
                     description="Agile drone with servos for smooth turning",
                     price="$2.99", picture="http://www.suasnews.com/wp-content/uploads/2011/02/scorpion-complete-1.jpg",  restaurant=restaurant1)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(name="Hexacopter",
                     description="Six motors allowing for more gear",
                     price="$5.50", picture="http://i.ebayimg.com/images/i/261446520413-0-1/s-l1000.jpg", restaurant=restaurant1)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(name="Bi-copter",
                     description="Nice design but the least stable of all drone designs",
                     price="$3.99", picture="http://www.multiwii.be/sites/default/files/bimultirotor.png", restaurant=restaurant1)

session.add(menuItem3)
session.commit()


# Create a new column in the "restaurant" table called "restuarant2"

restaurant2 = Restaurant(name="Flight Controllers")

session.add(restaurant2)
session.commit()


menuItem1 = MenuItem(name="Pix Hawk",
                     description="Used with 5 inch props and 2300 kv motors",
                     price="$7.99", picture="http://hobbyking.com/hobbyking/store/catalog/D2836-11750.gif", restaurant=restaurant2)

session.add(menuItem1)
session.commit()


menuItem3 = MenuItem(name="Arduino",
                     description="used for 450 class frames. Used with 980kv motors and 10 inch props",
                     price="15", picture="http://www.multirotormania.com/1859-thickbox_default/mrm-titan-2212-980kv-brushless-motor.jpg", restaurant=restaurant2)

session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(name="CC3D ",
                     description="Larger speed controllers used for large drones. ",
                     price="12", picture="http://img.dxcdn.com/productimages/sku_219554_1.jpg", restaurant=restaurant2)

session.add(menuItem4)
session.commit()

menuItem5 = MenuItem(name="Open Pilot",
                     description="Open source flight controller. Cheap but gets the job done.",
                     price="14", picture="https://upload.wikimedia.org/wikipedia/commons/3/38/Arduino_Uno_-_R3.jpg", restaurant=restaurant2)

session.add(menuItem5)
session.commit()


# Create a new column in the Restaurant" table called "restaurant3"
restaurant3 = Restaurant(name="Electronic Speed Controllers")

session.add(restaurant3)
session.commit()


menuItem1 = MenuItem(name="12 amp ESC",
                     description="Used for 250 frames and racing drones.",
                     price="$8.99", picture="http://www.readytoflyquads.com/media/catalog/product/cache/1/image/1200x/040ec09b1e35df139433887a97daa66f/8/-/8-7-2014_5-05-42_pm_1.jpg", restaurant=restaurant1)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(name="25 amp ESC",
                     description="speed controllers used for 450 class frames.",
                     price="$6.99", picture="http://hobbyking.com/hobbyking/store/catalog/55241.jpg", restaurant=restaurant3)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(name="30 amp ESC",
                     description="updated 10/30/2015 with new information",
                     price="$9.95", picture="http://i.ebayimg.com/images/i/141093410595-0-1/s-l1000.jpg", restaurant=restaurant3)

session.add(menuItem3)
session.commit()


print "Data has been added to the database!"
