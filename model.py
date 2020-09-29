from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Table, MetaData
import datetime
import defaults



Base = declarative_base()
meta = MetaData()

class TickerMC(Base):
    def __init__(self):
        self.create_ts = datetime.datetime.now()

    __tablename__ = "tickers_mc"
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10))
    infobolsa = Column(String(100))
    bolsademadrid = Column(String(100))
    bsmarkets = Column(String(100))
    avoid_consolidation = Column(Boolean)
    create_ts = Column(DateTime)

table_TickerMC = Table('tickers_mc', meta,Column('id', Integer, primary_key=True),
    Column('ticker', String(10)),
    Column('infobolsa', String(100)),
    Column('bolsademadrid',String(100)),
    Column('bsmarkets', String(100)),
    Column('avoid_consolidation', Boolean),
    Column('create_ts', DateTime))

class CotizacionMC(Base):
    __tablename__ = 'cotizaciones_mc'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    ticker = Column(String(15))
    ultimo = Column(Float)
    percdiff = Column(Float)
    max = Column(Float)
    min = Column(Float)
    vol = Column(Float)
    efectivo = Column(Float)
    ts = Column(DateTime)
    source = Column(String(50))
    fechaTexto = Column(String(50))
    iteracion = Column(Integer)
    derivedsourcetimestamp = Column(DateTime)

    def __repr__(self):
       return "<CotizacionMC(nombre='%s', ultimo='%s', ts='%s', source='%s')>" % (
                            self.nombre, self.ultimo, self.ts, self.source)

table_CotizacionMC = Table('cotizaciones_mc', meta, Column('id', Integer, primary_key=True),
    Column('nombre', String(100)),
    Column('ticker', String(15)),
    Column('ultimo', Float),
    Column('percdiff', Float),
    Column('max', Float),
    Column('min', Float),
    Column('vol',Float),
    Column('efectivo', Float),
    Column('ts',DateTime),
    Column('source', String(50)),
    Column('fechaTexto', String(50)),
    Column('iteracion', Integer),
    Column('derivedsourcetimestamp',DateTime))


class CotizazionHistMC(Base):
    __tablename__ = 'cotizaciones_hist_mc'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    fechatexto = Column(String(25))
    ticker = Column(String(25))
    valorcierre = Column(Float)
    percdiff = Column(Float)

table_CotizazionHistMC = Table('cotizaciones_hist_mc', meta,Column('id',Integer, primary_key=True),
    Column('nombre',String(100)),
    Column('fechatexto', String(25)),
    Column('ticker',String(25)),
    Column('valorcierre',Float),
    Column('percdiff',Float))

class CotizacionConsolidadaMC(Base):
    __tablename__ = 'cotizacionesconsolidadas_mc'
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10))
    ultimo = Column(Float)
    volumen = Column(Float)
    efectivo = Column(Float)
    ts = Column(DateTime)
    cotizacioneslastid = Column(Integer)

table_CotizacionConsolidadaMC = Table('cotizacionesconsolidadas_mc', meta,Column('id', Integer, primary_key=True),
    Column('ticker',String(10)),
    Column('ultimo',Float),
    Column('volumen',Float),
    Column('efectivo', Float),
    Column('ts',DateTime),
    Column('cotizacioneslastid',Integer))


def checktablesexists(engine, tablename):
    hastable = engine.dialect.has_table(engine, tablename)
    return hastable

def checkdatabaseexists(servernameorip=defaults.server,intport=defaults.port,dbname=defaults.databasename,
                        dbuser=defaults.user,dbpwd=defaults.pwd, driver=defaults.databasedriver):
    try:
        engine = getaitraderengine(servernameorip, intport, dbname, dbuser, dbpwd, driver)
        engine.connect()
        engine.dispose()
        return True
    except BaseException as err:
        return False

def getaitraderengine(servernameorip=defaults.server,intport=defaults.port,dbname=defaults.databasename,
                        dbuser=defaults.user,dbpwd=defaults.pwd, driver=defaults.databasedriver):
    engine = create_engine("mysql+"+driver+"://"+dbuser+":"+dbpwd+"@"+servernameorip+":"+str(intport)+"/"+dbname)
    return engine

def checkdatabaseok(servernameorip=defaults.server,port=defaults.port,databasename=defaults.databasename, user=defaults.user,pwd=defaults.pwd):
    errors = []
    if checkdatabaseexists(servernameorip, port, databasename, user, pwd):
        engine = getaitraderengine(servernameorip, port, databasename, user, pwd)
        classes = [CotizacionMC, CotizacionConsolidadaMC, CotizazionHistMC, TickerMC]
        for c in classes:
            if not checktablesexists(engine, c.__tablename__):
                errors.append("A Table with name '" + c.__tablename__ + "' was not found! Re-run database setup!")
    else:
        errors.append("A Database with name " + databasename + " doesn't exist in the MySQL Server, or the MySQL Server was not found")

    if len(errors)==0:
        return True, None
    else:
        return False, errors

def setupdatabase(engine, databasename):
    #if database exists will be dropped first. Be careful!
    with engine.connect() as conn:
        conn.execute("drop database if exists " + databasename)
        print("Database " + databasename + " was dropped!")
        print("New Database " + databasename + " will be created...")
        conn.execute("create database " + databasename)
        conn.execute("use " + databasename)

    server = engine.url.host
    port = engine.url.port
    database = databasename
    user = engine.url.username
    pwd = engine.url.password
    nengine = getaitraderengine(server, port, database, user, pwd)
    table_CotizacionMC.create(nengine)
    table_TickerMC.create(nengine)
    table_CotizacionConsolidadaMC.create(engine)
    table_CotizazionHistMC.create(engine)
    nengine.dispose()
    print("New Database '" + databasename + "' created successfully with all tables in it!")





