from sqlalchemy.orm import sessionmaker
from model import getaitraderengine
from model import CotizacionMC
from globalutils import gettimestampfromfechatexto
engine = getaitraderengine()

"""
Archivo para rellenar el campo de derivedsourcetimestamp en la tabla cotizaciones_mc
"""

Session = sessionmaker(bind=engine)
session = Session()

cotizaciones = session.query(CotizacionMC).all()
tostore = []
for c in cotizaciones:
    if c.derivedsourcetimestamp == None:
        c.derivedsourcetimestamp = gettimestampfromfechatexto(c.source, c)
        tostore.append(c)


for c in tostore:
    session.add(c)
session.commit()
