
import xml.etree.ElementTree as ET

import pdb
import traceback


from stylesheets import StyleTable


class HtmlDoc(object):

    def __init__ (self):
        self.docobj = None
        self.dtdstr = None
        self.engine_supports_css = True

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

    # this emulates some of scheme but Ive chose an xml DOM model
    # for the python document model

    def __init__ (self,stylesheet=None):
        # this emulates the scheme html-document record
        # note that objects is now the doc variable
        # (style-sheet style-stack style style-text title headline objects)
        # whats the different between style-sheet and style-text??
        self.style_sheet = stylesheet
        self.style_stack = None
        self.style = None
        self.style_text = None
        self.title = None
        self.headline = None
        self.doc = HtmlDoc()

        # for the moment adding the style table here
        self.style_table = StyleTable()

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

    # new idea - use this function to add the body object with style
    def add_body_style (self, attr_dict=None):
        #pdb.set_trace()
        if self.doc.docobj:
            bodyobj = self.doc.docobj.find("body")
            if bodyobj == None:
                htmlobj = self.doc.docobj.find("html")
                if htmlobj:
                    bodyobj = self.doc.SubElement(htmlobj,"body")
                else:
                    # we have elements but no body - nor html
                    # make an outer body object
                    pdb.set_trace()
                    bodyobj = ET.Element("body")
                    bodyobj.append(self.docobj)
                    self.docobj = bodyobj
        else:
            bodyobj = self.doc.Element("body")

        for key,val in attr_dict['body'].items():
            if key == "attribute":
                for key1,val1 in val.items():
                    bodyobj.attrib[key1] = val1
            else:
                subobj = self.doc.SubElement(bodyobj,key)
                for key1,val1 in val.items():
                    subobj.attrib[key1] = val1

    def set_stylesheet (self, stylesheet):
        self.style_sheet = stylesheet

    def render (self, report, headers=None):

        #pdb.set_trace()

        # now going using a python xml dom model - currently ElementTree
        docxml = self.doc

        # so thats how this works - the scheme does a first call to the stylesheet
        # render which then creates a new HtmlDocument object where this render
        # function is called with an undefined style_sheet - but a defined style!!
        if self.style_sheet:
            docstr = self.style_sheet.render(report,self,headers)
        else:
            # do trivial render

            if headers:

                # how do we implement this
                # where is this written out
                # do we make a list of strings and join - as concatenating strings would be very slow
                # we dont add this I think - will be added at string generation
                docxml.dtd('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" \n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
                htmlobj = docxml.Element('html', attrib={'xmlns' : "http://www.w3.org/1999/xhtml"})
                htmlobj.text = "\n"
                headobj = docxml.SubElement(htmlobj,"head")
                headobj.text = "\n"
                headobj.tail = "\n"
                metaobj = docxml.SubElement(headobj,'meta', attrib={'http-equiv' : "content-type", 'content' : "text/html; charset=utf-8"})
                metaobj.text = "\n"
                metaobj.tail = "\n"

                #pdb.set_trace()

                if self.doc.engine_supports_css:
                    if self.style_text:
                        cssobj = docxml.SubElement(headobj,'style', attrib={'type' : "text/css", })
                        cssobj.text = self.style_text
                        cssobj.tail = "\n"

                # the report title is stored in the document title
                # because we are doing things differently in python
                # we dont have the report title yet
                # set a title object which will update when have the document title
                #if title:
                #    titlobj = docxml.SubElement(headobj,"title")
                #    titlobj.text = title
                titlobj = docxml.SubElement(headobj,"title")

                # ;; this lovely little number just makes sure that <body>
                # ;; attributes like bgcolor get included
                # (push ((gnc:html-markup/open-tag-only "body") doc))))

                # we now let the report add the body with attributes
                # leave this in as dummy if not replaced
                bodyobj = docxml.SubElement(htmlobj,"body")
                bodyobj.text = "\n"
                bodyobj.tail = "\n"

            renderer = report.report_type.renderer

            try:
                subdoc = renderer(report)
            except Exception, errexc:
                traceback.print_exc()
                pdb.set_trace()

            if subdoc == None:
                pdb.set_trace()
                docstr = None
                raise RuntimeError("Invalid Html subdoc")

            pdb.set_trace()

            try:
                # copy in the report title
                titlobj.text = subdoc.title
                # assume body not added if not first element
                if subdoc.doc.docobj.tag == "body":
                    htmlobj.remove(bodyobj)
                htmlobj.append(subdoc.doc.docobj)
            except Exception, errexc:
                traceback.print_exc()
                pdb.set_trace()

            try:
                # only in python 2.7
                #docstr = ET.tostring(htmlobj, encoding="utf-8", method="html")
                docstr = docxml.tostring(encoding="utf-8")
            except Exception, errexc:
                traceback.print_exc()
                pdb.set_trace()


            # debugging dump
            if docstr != None:
                fds = open("junk.html","w")
                fds.write(docstr)
                fds.close()

            if docstr == None:
                raise RuntimeError("Invalid Html doc")

        return docstr


