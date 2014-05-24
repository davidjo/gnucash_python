
#from codegen.argtypes import ArgType, matcher
#from codegen import reversewrapper
from argtypes import ArgType, matcher
import reversewrapper


# oohh - this is sneaky - this is how we define a partial type

class gpointer(ArgType):

    before = ('    %(name)s = (gpointer)(((PyGPointer *)(py_%(name)s))->pointer);\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('gpointer', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('gpointer', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }')

matcher.register('gpointer', gpointer())

class StringList(ArgType):

    before = ('    if (!PyList_Check(py_%(name)s)) {\n'
              '        PyErr_Print();\n'
              '        return NULL;\n'
              '    }\n'
              '    for (indx_%(name)s=0; indx_%(name)s<PyList_Size(py_%(name)s); indx_%(name)s++)\n'
              '        {\n'
              '        PyObject *pstr = PyList_GetItem(py_%(name)s,indx_%(name)s);\n'
              '        if (!PyString_Check(pstr)) {\n'
              '            PyErr_Print();\n'
              '            return NULL;\n'
              '        }\n'
              '        gchar *gstr = PyString_AsString(pstr);\n'
              '        *%(name)s++ = gstr;\n'
              '        }\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('gchar ', '**'+pname)
        info.varlist.add('int ', 'indx_'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('gpointer', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }')

matcher.register('gchar**', StringList())


class URLType(ArgType):

    before = ('    %(name)s = (URLType)PyString_AsString(py_%(name)s);\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('URLType', pname)
        info.add_parselist('s', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('URLType', '*ret')
        info.codeafter.append('    if (ret)\n'
                              '        return PyString_FromString(ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('URLType', URLType())

class gnc_html_history_pointer(ArgType):

    # junk type just to have definition

    before = ('    %(name)s = (gnc_html_history *)(((PyGPointer *)(py_%(name)s))->pointer);\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('gnc_html_history', '*'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('gnc_html_history', '*ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }')

matcher.register('gnc_html_history*', gnc_html_history_pointer())

#typedef gboolean (* GncHTMLObjectCB)(GncHtml* html, gpointer eb,
#                                     gpointer data);
#typedef gboolean (* GncHTMLStreamCB)(const gchar* location, gchar** data, int* datalen);
#typedef gboolean (* GncHTMLUrlCB)(const gchar* location, const gchar* label,
#                                  gboolean new_window, GNCURLResult* result);

class GncHTMLObjectCB(ArgType):

    before = ('    %(name)s = py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GncHTMLObjectCB', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GncHTMLObjectCB', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return py_gpointer_new(ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GncHTMLObjectCB', GncHTMLObjectCB())


class GncHTMLUrltypeCB(ArgType):

    before = ('    %(name)s = py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GncHTMLUrltypeCB', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GncHTMLUrltypeCB', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return py_gpointer_new(ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GncHTMLUrltypeCB', GncHTMLUrltypeCB())

class GncHTMLFlyoverCB(ArgType):

    before = ('    %(name)s = py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GncHTMLFlyoverCB', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GncHTMLFlyoverCB', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return py_gpointer_new(ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GncHTMLFlyoverCB', GncHTMLFlyoverCB())

