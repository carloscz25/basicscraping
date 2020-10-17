from xbrl import XBRLParser
import xml.etree.ElementTree as ET
pathipps = "C:/Users/Carlos Conti/Desktop/ipp_2019-01-01/"
rootdefinition = ET.parse(pathipps + "ipp_ge_2019-01-01-definition.xml").getroot()
rootlabel = ET.parse(pathipps + "ipp_ge_2019-01-01-label.xml").getroot()
rootinstance = ET.parse("2020082198.xbrl").getroot()

namespaces = {"xsi":"http://www.w3.org/2001/XMLSchema-instance",
              "schemaLocation":"http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd",
              "ipp_ge":"http://www.cnmv.es/xbrl/ipp/ge/2019-01-01", "link":"http://www.xbrl.org/2003/linkbase" , "xlink":"http://www.w3.org/1999/xlink", "xbrli":"http://www.xbrl.org/2003/instance", "xbrldt":"http://xbrl.org/2005/xbrldt"}

ddll = rootdefinition.findall(".//link:definitionLink", namespaces=namespaces)
contadorseccion = 0
contenido = ""
for dl in ddll:
    if (contenido!=""):
        f = open("seccion " + str(contadorseccion) + ".txt", "a")
        f.write(contenido)
        f.close()
    contenido = ""
    print("SECCION="+str(contadorseccion))
    contadorseccion +=1
    print("==============")
    for el in dl:
        if el.tag.find("loc")!=-1:
            def_href = el.attrib["{"+namespaces["xlink"]+"}href"]
            label_loc = rootlabel.find(".//link:loc[@xlink:href='"+def_href+"']", namespaces=namespaces)
            if label_loc == None:
                continue
            titelattr = label_loc.attrib["{"+namespaces["xlink"]+"}title"]
            insthref = label_loc.attrib["{"+namespaces["xlink"]+"}href"]
            insthref = insthref.split("#")[1]
            locator = ""
            if insthref[0:len("ipp_ge_")]=="ipp_ge_":
                insthref = insthref[len("ipp_ge_"):]
                instvalues = rootinstance.findall("{"+namespaces["ipp_ge"]+"}"+insthref)
                if insthref[1:].isnumeric():
                    locator = "("+insthref+")"
                y = 2
            labelattr = label_loc.attrib["{"+namespaces["xlink"]+"}label"]
            label = rootlabel.find(".//link:label[@xlink:label='"+"label_" + labelattr+"']", namespaces=namespaces)
            title = label.text

            linea = ""
            linea = locator + title
            for j in range(len(instvalues)):
                linea += "    " + instvalues[j].text
            contenido += linea + "\n"
            print(linea)

            # if len(instvalues)==1:
            #     print(locator + title + "    " + instvalues[0].text)
            #     contenido += locator + title + "    " + instvalues[0].text + "\n"
            # elif len(instvalues)==2:
            #     print(locator +title + "    " + instvalues[0].text + "    " + instvalues[1].text)
            #     contenido += locator + title + "    " + instvalues[0].text + "    " + instvalues[1].text + "\n"
            # else:
            #     print(locator + title)
            #     contenido += locator + title + "\n"
        elif el.tag.find("definitionArc")!=-1:
            pass
    y=2
y=2






