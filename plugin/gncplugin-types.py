
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
              '    %(name)s = (gchar **) g_malloc(sizeof(gchar*)*(PyList_Size(py_%(name)s)+1));\n'
              '    gchar **%(name)s_ptr = %(name)s;\n'
              '    for (indx_%(name)s=0; indx_%(name)s<PyList_Size(py_%(name)s); indx_%(name)s++)\n'
              '        {\n'
              '        PyObject *pstr = PyList_GetItem(py_%(name)s,indx_%(name)s);\n'
              '        if (!PyString_Check(pstr)) {\n'
              '            PyErr_Print();\n'
              '            return NULL;\n'
              '        }\n'
              '        gchar *gstr = PyString_AsString(pstr);\n'
              '        *%(name)s_ptr++ = gstr;\n'
              '        }\n')

    after = ('    g_free(%(name)s);\n\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('gchar ', '**'+pname)
        info.varlist.add('int ', 'indx_'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })
        info.codeafter.append (self.after % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('gpointer', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }')

matcher.register('const-gchar**', StringList())



class GncMainWindow(ArgType):

    # punt - just use a PyGPointer
    before = ('    %(name)s = (GncMainWindow*)(((PyGPointer *)(py_%(name)s))->pointer);\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GncMainWindow', '*'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GncMainWindow', '*ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GncMainWindow*', GncMainWindow())


class action_toolbar_labels(ArgType):

    # punt - just use a PyGPointer
    before = ('    %(name)s = (action_toolbar_labels*)(((PyGPointer *)(py_%(name)s))->pointer);\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('action_toolbar_labels', '*'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('action_toolbar_labels', '*ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('action_toolbar_labels*', action_toolbar_labels())


class GQuark(ArgType):
    dflt = ('    if (py_%(name)s) {\n'
            '        if (PyLong_Check(py_%(name)s))\n'
            '            %(name)s = PyLong_AsUnsignedLong(py_%(name)s);\n'
            '        else if (PyInt_Check(py_%(name)s))\n'
            '            %(name)s = PyInt_AsLong(py_%(name)s);\n'
            '        else\n'
            '            PyErr_SetString(PyExc_TypeError, "Parameter \'%(name)s\' must be an int or a long");\n'
            '        if (PyErr_Occurred())\n'
            '            return NULL;\n'
            '    }\n')
    before = ('    if (PyLong_Check(py_%(name)s))\n'
              '        %(name)s = PyLong_AsUnsignedLong(py_%(name)s);\n'
              '    else if (PyInt_Check(py_%(name)s))\n'
              '        %(name)s = PyInt_AsLong(py_%(name)s);\n'
              '    else\n'
              '        PyErr_SetString(PyExc_TypeError, "Parameter \'%(name)s\' must be an int or a long");\n'
              '    if (PyErr_Occurred())\n'
              '        return NULL;\n')
    def write_param(self, ptype, pname, pdflt, pnull, info):
        if not pdflt:
            pdflt = '0';

        info.varlist.add(ptype, pname + ' = ' + pdflt)
        info.codebefore.append(self.dflt % {'name':pname})
        info.varlist.add('PyObject', "*py_" + pname + ' = NULL')
        info.arglist.append(pname)
        info.add_parselist('O', ['&py_' + pname], [pname])
    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add(ptype, 'ret')
        info.codeafter.append('    return PyLong_FromUnsignedLong(ret);')


matcher.register('GQuark', GQuark())

