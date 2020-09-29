import model
import argparse
import defaults

parser = argparse.ArgumentParser(description="Check if requirements are there to run the scraper routine: database, libraries, ...")
parser.add_argument("-server", help="Server name or IP", type=str, default=defaults.server)
parser.add_argument("-port", help="Port value : int", type=int, default=defaults.port)
parser.add_argument("-dbname", help="Port value : int", type=str, default=defaults.databasename)
parser.add_argument("-user", help="User to login to the database", type=str, default=defaults.user)
parser.add_argument("-pwd", help="Password to login to the database", type=str, default=defaults.pwd)
parser.add_argument("-driver", help="Driver to be used by SQLAlchemy to connect the database", default=defaults.databasedriver)

args = parser.parse_args()

b = model.checkdatabaseexists(args.server, args.port, args.dbname, args.user, args.pwd)
if not b:
    print("Database not found!Want to run the database creation routine at server '" + args.server + "'?")
    i = input("Yes=y/No=n")
    if i == "y":
        from sqlalchemy import create_engine
        provisionalengine = create_engine("mysql+"+args.driver+"://" + args.user + ":" + args.pwd + "@" + args.server + ":" + str(args.port))
        model.setupdatabase(provisionalengine, args.dbname)
        provisionalengine.dispose()
    else:
        print("Run database creation to proceed!")
        quit(0)
else:
    print("GOOD!: Database with name '" + args.dbname + "' was found on server '" + args.server)

print("Checking if database tables are there...")
b, errors = model.checkdatabaseok(args.server, args.port, args.dbname, args.user, args.pwd)
if (b):
    print("Database contains necessary tables to run the scraping routine")
else:
    print("The following errors were found:")
    for e in errors:
        print(e)
    print("Want me to re-run the database creation routine at server '" + args.server + "'?")
    i = input("yes=y/no=n")
    if i == "y":
        print("Re-running database creation at server '" + args.server)
        from sqlalchemy import create_engine
        provisionalengine = create_engine("mysql+mysqlconnector://"+args.user+":"+args.pwd+"@"+args.server+":"+str(args.port))
        model.setupdatabase(provisionalengine, args.dbname)
        provisionalengine.dispose()
    else:
        print("Database checks are necessary to be fullfilled before running the scraping routine")


