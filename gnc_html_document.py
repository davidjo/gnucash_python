

import pdb
import traceback


class HtmlDoc(list):

    def __init__ (self):
        super(HtmlDoc,self).__init__()

    def push (self, strarg):
        self.append(strarg)


class HtmlDocument(object):

    # very junky - so far this just creates a list of strings that is the document

    def __init__ (self):
        self.doc = HtmlDoc()
        self.title = None

    def get_doc (self):
        return self.doc

    def add_object (self, newobj):
        self.doc.push(newobj)


