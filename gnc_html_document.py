
import xml.etree.ElementTree as ET

import pdb
import traceback


from stylesheets import StyleTable


class HtmlDoc(object):

    def __init__ (self):
        self.dtdstr = None
        self.engine_supports_css = True
        self.header = None
        self.docobj = None

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
            subobj = ET.Element(tag, attrib, **extra)
            self.docobj.append(subobj)
            return subobj

    def SubElement (self, parent, tag, attrib={}, **extra):
        subobj = ET.SubElement(parent,tag, attrib, **extra)
        return subobj

    def HeaderElement (self, tag, attrib={}, **extra):
        # this identifies the header element in the style sheet
        # to update the text
        subobj = self.Element(tag, attrib, **extra)
        self.header = subobj
        return subobj


class HtmlDocument(object):

    # this emulates some of scheme but Ive chose an xml DOM model
    # for the python document model

    def __init__ (self,stylesheet=None):
        # this emulates the scheme html-document record
        # note that objects is now the doc variable
        # (style-sheet style-stack style style-text title headline objects)
        # style-text seems to be where the html CSS text is stored
        self.style_sheet = stylesheet
        self.style_stack = None
        self.style = StyleTable()
        self.style_text = None
        self.title = None
        self.headline = None
        self.doc = HtmlDoc()
        tmpobj = self.doc.Element("body")
        tmpobj.text = "\n"
        tmpobj.tail = "\n"

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
        if self.doc.docobj != None:
            bodyobj = self.doc.docobj.find("body")
            if bodyobj == None:
                htmlobj = self.doc.docobj.find("html")
                if htmlobj != None:
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

    def StyleElement (self, tag, attrib={}, parent=None):
        newelm = self.style.make_html(tag,attrib)
        if self.doc.docobj != None:
            if parent != None:
                parent.append(newelm)
            else:
                self.doc.docobj.append(newelm)
        else:
            self.doc.docobj = newelm
        return newelm

    def StyleSubElement (self, parent, tag, attrib={}):
        # this simply makes report writing more consistent with Elementtree
        newelm = self.StyleElement(tag, attrib=attrib, parent=parent)
        return newelm


    def render (self, report, headers=None):

        #pdb.set_trace()

        # need to deal with fact this is called sort of recusively
        # - if have stylesheet we go through here and call self.style_sheet.render
        # which calls this function again
        # need to ensure we have a fresh docxml object here
        parent_docobj = None
        if self.doc.docobj != None:
           parent_docobj = self.doc
           self.doc = HtmlDoc()

        # now going using a python xml dom model - currently ElementTree
        docxml = self.doc

        # make sure this is defined
        report.stylesheet_document = None

        # so thats how this works - the scheme does a first call to the stylesheet
        # render which then creates a new HtmlDocument object where this render
        # function is called with an undefined style_sheet - but a defined style!!
        if self.style_sheet != None:
            # this is weird but as self.style_sheet.render calls this function
            # recursively which returns the document string the return here
            # is also the document string
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


                # now added in HtmlDoc
                ## we now let the report add the body with attributes
                ## leave this in as dummy if not replaced
                bodyobj = ET.Element("body")
                bodyobj.text = "\n"
                bodyobj.tail = "\n"

            renderer = report.report_type.renderer

            # we need to pass the style table (unlike scheme way)
            # do it through the report for the moment
            report.style = self.style

            try:
                subdoc = renderer(report)
            except Exception, errexc:
                traceback.print_exc()
                # ensure GUI reactivated
                report.report_type.cleanup_gui()
                pdb.set_trace()
                subdoc = None

            if subdoc == None:
                pdb.set_trace()
                docstr = None
                raise RuntimeError("Invalid Html subdoc")

            #pdb.set_trace()

            # copy in the report title
            if hasattr(subdoc,"title"):
                if subdoc.title != None:
                    titlobj.text = subdoc.title
                else:
                    titlobj.text = "\n"
            else:
                titlobj.text = "\n"

            # figure the headline
            # always default to title??
            headline = ""
            if hasattr(subdoc,"headline"):
                if subdoc.headline != None:
                    headline = subdoc.headline
                elif hasattr(subdoc,"title"):
                    if subdoc.title != None:
                        headline = subdoc.title
            elif hasattr(subdoc,"title"):
                if subdoc.title != None:
                    headline = subdoc.title

            # add header from ssdoc and update text
            # note this assumes the only thing in parent_docobj is the header
            hdrobj = None
            if parent_docobj != None:
                if parent_docobj.header != None:
                    if headline != None and headline != "":
                        parent_docobj.header.text = headline
                        hdrobj = parent_docobj.header
                        if subdoc.doc.docobj.tag == "body":
                            subdoc.doc.docobj.insert(0,hdrobj)
                            # bit weird but only way I can see to do this
                            # we move the bodyobj text to the tail of the header
                            # as header needs to come first
                            if subdoc.doc.docobj.text != None:
                                hdrobj.tail = "\n"+subdoc.doc.docobj.text
                                subdoc.doc.docobj.text = None
                        else:
                            bodyobj.append(hdrobj)
                            bodyobj.append(subdoc.doc.docobj)

            try:
                # assume body not added if not first element
                if subdoc.doc.docobj.tag == "body":
                    #htmlobj.remove(bodyobj)
                    htmlobj.append(subdoc.doc.docobj)
                else:
                    htmlobj.append(bodyobj)
                    #bodyobj.append(subdoc.doc.docobj)
            except Exception, errexc:
                traceback.print_exc()
                pdb.set_trace()

            #pdb.set_trace()

            try:
                # only in python 2.7
                #docstr = ET.tostring(htmlobj, encoding="utf-8", method="html")
                docstr = docxml.tostring(encoding="utf-8")
            except Exception, errexc:
                traceback.print_exc()
                try:
                    ET.dump(htmlobj)
                except Exception, errexc1:
                    pass
                pdb.set_trace()


            # debugging dump
            if docstr != None:
                fds = open("junk.html","w")
                fds.write(docstr)
                fds.close()

            if docstr == None:
                raise RuntimeError("Invalid Html doc")

        return docstr


