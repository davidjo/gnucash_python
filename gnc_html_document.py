
import xml.etree.ElementTree as ET

import pdb
import traceback


class HtmlDoc(object):

    def __init__ (self):
        self.docobj = None
        self.dtdstr = None

    def dtd (self, dtdstr):
        self.dtdstr = dtdstr

    def tostring (self, encoding):
        if self.dtdstr != None:
            return self.dtdstr + ET.tostring(self.docobj, encoding=encoding)
        else:
            return ET.tostring(self.docobj, encoding=encoding)

    def Element (self, tag, attrib={}, **extra):
        if self.docobj == None:
            self.docobj = ET.Element(tag, attrib, **extra)
            return self.docobj
        else:
            subobj = ET.SubElement(self.docobj,tag, attrib, **extra)
            return subobj

    def SubElement (self, parent, tag, attrib={}, **extra):
        subobj = ET.SubElement(parent,tag, attrib, **extra)
        return subobj


class HtmlDocument(object):

    # very junky - so far this just creates a list of strings that is the document

    def __init__ (self):
        self.doc = HtmlDoc()
        self.title = None

    def get_doc (self):
        return self.doc

    def get_xml (self):
        return self.doc.docobj

    # this only works in python 2.7
    #def tostring (self, encoding, xmlmethod):
    #    return ET.tostring(self.doc.docobj, encoding=encoding, method=xmlmethod)

    def tostring (self, encoding):
        if self.doc.dtdstr != None:
            return self.doc.dtdstr + ET.tostring(self.doc.docobj, encoding=encoding)
        else:
            return ET.tostring(self.doc.docobj, encoding=encoding)
