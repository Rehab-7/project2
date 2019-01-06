from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_serise import Series, Base, CatalogItem, User

engine = create_engine('sqlite:///seriescatalogwithuseress.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Create dummy user
User1 = User(name="Rehab Aldosry", email="rehab.cs@gmail.com",
             picture='https://lh3.googleusercontent.com/-c-rLp\
             97-7Ns/XB8EE8c0OKI/AAAAAAAAACk/2WghHW \
             jWf-EAidrLBDY-edXdKMy2DOx5g\
             CEwYBhgL/w139-h140-p/DXgDq_RXcAE-i62.jpg')
session.add(User1)
session.commit()


series1 = Series(user_id=1, name="series Action ")

session.add(series1)
session.commit()

catalogItem1 = CatalogItem(user_id=1, name="Game of Thrones", description="Nine noble families fight for control \
                           over the mythical lands of \
                           Westeros, while an ancient enemy \
                           returns after being dormant\
                           for thousands of years.",
                           rating="9.5",
                           seasons="1,2,3,4,5,6,7,8", series=series1)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Peaky Blinders", description="A gangster family epic set in\
                           1919 Birmingham, England;\
                           centered on a gang who sew \
                           razor blades in the peaks of their caps, and \
                           their fierce boss Tommy Shelby.",
                           rating="8.8", seasons="1,2,3,4,5", series=series1)

session.add(catalogItem2)
session.commit()

catalogItem3 = CatalogItem(user_id=1, name="Vikings", description="Vikings transports us to\
                           the brutal and mysterious world \
                           of Ragnar Lothbrok, a Viking\
                           warrior and farmer who yearns\
                           to explore - and raid - the \
                           distant shores across the ocean.",
                           rating="8.6", seasons="1,2,3,4,5,6", series=series1)

session.add(catalogItem3)
session.commit()

series2 = Series(user_id=1, name="Series Drama")

session.add(series2)
session.commit()

catalogItem1 = CatalogItem(user_id=1, name="The Good Doctor", description="Shaun Murphy, a young surgeon\
                           with autism and Savant syndrome, is\
                           recruited into the surgical unit\
                           of a prestigious hospital.",
                           rating="8.3", seasons="1,2", series=series2)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="The Handmaid's Tale", description="Set in a dystopian future,\
                           a woman is forced to live as a concubine under\
                           a fundamentalist theocratic dictatorship.",
                           rating="8.6", seasons="1,2,3", series=series2)

session.add(catalogItem2)
session.commit()

catalogItem3 = CatalogItem(user_id=1, name="The Crown", description="Follows the political rivalries and\
                           romance of Queen Elizabeth II's reign \
                           and the events that shaped the\
                           second half of the 20th century.",
                           rating="8.7", seasons="1,2,3,4", series=series2)

session.add(catalogItem3)
session.commit()

series3 = Series(user_id=1, name="Series Horror")

session.add(series3)
session.commit()

catalogItem1 = CatalogItem(user_id=1, name="Hannibal", description="Explores the early relationship\
                           between the renowned psychiatrist and his\
                           patient, a young FBI criminal profiler, who is\
                           haunted by his ability to \
                           empathize with serial killers.",
                           rating="8.5", seasons="1,2,3", series=series3)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="The Walking Dead", description="Sheriff Deputy Rick Grimes\
                           wakes up from a coma to learn the world\
                           is in ruins, and must lead a group \
                           of survivors to stay alive.",
                           rating="8.4",
                           seasons="1,2,3,4,5,6,7,8,9,10", series=series3)

session.add(catalogItem2)
session.commit()

catalogItem3 = CatalogItem(user_id=1, name="The Haunting of Hill House", description="Flashing between past and\
                           present, a fractured family confronts haunting\
                           memories of their old home and the\
                           terrifying events that drove them from it.",
                           rating="8.9", seasons="1", series=series3)

session.add(catalogItem3)
session.commit()


series4 = Series(user_id=1, name="Series Mystery")

session.add(series4)
session.commit()

catalogItem1 = CatalogItem(user_id=1, name="Dark", description="A family saga with a supernatural\
                           twist, set in a German town,\
                           where the disappearance \
                           of two young children exposes the\
                           relationships among four families.",
                           rating="8.6", seasons="1,2", series=series4)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Stranger Things",
                           description="Nine noble families fight for control over the mythical lands\
                           of Westeros, while an ancient enemy returns after\
                           being dormant for thousands of years.",
                           rating="8.9", seasons="1,2,3", series=series4)

session.add(catalogItem2)
session.commit()

catalogItem3 = CatalogItem(user_id=1, name="Sherlock",
                           description="A modern update finds the famous sleuthand his doctor\
                           partner solving crime in 21st century London.",
                           rating="9.2", seasons="1,2,3,4", series=series4)

session.add(catalogItem3)
session.commit()

print "added menu items!"