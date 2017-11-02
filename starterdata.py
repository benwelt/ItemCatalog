from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Category, Bike

engine = create_engine('sqlite:///bikecatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

category1 = Category(name="Downhill")
session.add(category1)
session.commit()

bike1 = Bike(
        name="Tues",
        brand="YT",
        description="""The TUES is an absolute killer of a bike and embodies our motto Good Times in its purest form. The stiffness of the frame, the low center of gravity and the dynamic suspension system make it the perfect partner for bike parks, rough trails and high speed descents. The slack head angle, the generous reach and the 650B wheels keep you in control on any track while the progressiveness of its suspension will get you hooked on airtime in a hurry. Not only did our team riders take wins at the FEST Series and Rampage aboard the TUES, but also the 2016 overall World Cup title - the TUES packs quite the punch and handles the biggest jumps in the world with ease. Carbon or aluminum? The choice is yours. Beginners, park-rats, and pro racers will all be stoked with the various spec options on offer.""",
        imageUrl="https://ytmedia.azureedge.net/image/Tues_CF_PRO_RACE_silver_front_b1.jpg",
        category=category1
        )
session.add(bike1)
session.commit()

category2 = Category(name="Trail")
session.add(category2)
session.commit()

bike1 = Bike(
        name="Strive",
        brand="Canyon",
        description="""It's rare that anything able to scramble up slopes this easily can rip so hard on the way back down. Thanks to Shapeshifter, the Strive makes the impossible possible - it is the ultimate enduro bike. The revolutionary on-the-fly system provides two distinctly different settings for geometry, suspension kinematics and travel. As a result, the Strive climbs with absolute efficiency in XC mode and bombs down the rowdiest descents in DH mode. That's why it's the ride of choice for the Canyon Factory Enduro Team. Give every trail a new dimension!""",
        imageUrl="https://static.canyon.com/_Resources/Website/Images/f1/9/e3364e6d51bfa78eb24c1cdcb0546.jpg",
        category=category2
        )
session.add(bike1)
session.commit()

bike2 = Bike(
        name="The Follwing MB",
        brand="Evil",
        description="""Everybody's favorite 120mm of fun just got a little better'er. We picked up right where the original Following left off and decided to make the party between your legs a little longer and stiffer, but not slacker or lower. The Following is back and more better'er with a trunnion mounted metric piggy-back shock, boost and an integrated chain guide. Now you can have all that big bike fun in a shorter travel package. Sometimes less really is more. Now you can tell everyone your 120mm rides way bigger than it looks and rarely bottoms out.""",
        imageUrl="https://cdn.shopify.com/s/files/1/0903/4494/products/EVL-PA-FLW-MB-2017-Drunken-Olive-X01-Eagle-complete-front-three-quarter.jpg?v=1504820983",
        category=category2
        )
session.add(bike2)
session.commit()

category3 = Category(name="XC")
session.add(category3)
session.commit()

bike1 = Bike(
        name="Anthem",
        brand="Giant",
        description="""Featuring an updated platform with 110mm of rear suspension travel and 130mm up front, this light and lively off-road machine is ultra-versatile. With geometry designed specifically for its 27.5 wheels and smooth Maestro suspension to soak up the bumps, it's the perfect blend of efficiency and control. The rear suspension features a trunnion-mount shock and Advanced Forged composite rocker arm for added strength and stiffness. And Boost hub spacing (110 front/148 rear) means stiffer wheels for added control. It's a perfect choice for riders seeking a lightweight, quick-handling ripper.""",
        imageUrl="https://images.giant-bicycles.com/b_white,c_pad,h_1000,q_80/Anthem-Advanced-0-Color-A-Electric-Blue/Anthem-Advanced-0-Color-A-Electric-Blue.jpg",
        category=category3
        )
session.add(bike1)
session.commit()

print ("NEW ITEMS HAVE BEEN ADDED")
