
#from codegen.argtypes import ArgType, matcher
#from codegen import reversewrapper
from argtypes import ArgType, matcher
import reversewrapper


class AccountFilterDialog(ArgType):

    # punt - just use a PyGPointer
    before = ('    %(name)s = (AccountFilterDialog*)(((PyGPointer *)(py_%(name)s))->pointer);\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('AccountFilterDialog', '*'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('AccountFilterDialog', '*ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('AccountFilterDialog*', AccountFilterDialog())

class GncTreeViewAccountColumnSource(ArgType):

    before = ('    %(name)s = (GncTreeViewAccountColumnSource)py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GncTreeViewAccountColumnSource', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GncTreeViewAccountColumnSource', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GncTreeViewAccountColumnSource', GncTreeViewAccountColumnSource())

class GncTreeViewAccountColumnTextEdited(ArgType):

    before = ('    %(name)s = (GncTreeViewAccountColumnTextEdited)py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GncTreeViewAccountColumnTextEdited', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GncTreeViewAccountColumnTextEdited', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GncTreeViewAccountColumnTextEdited', GncTreeViewAccountColumnTextEdited())

class GKeyFile(ArgType):

    before = ('    %(name)s = (GKeyFile*)PyObject_GetAttrString(py_%(name)s,"keyfile");\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GKeyFile', '*'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('gpointer', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pygkeyfile_new(ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GKeyFile*', GKeyFile())

class Account(ArgType):

    # // this is interdependent with how we are accessing gnucash

    # // we could assume passing swig-wrapped Account object,
    # // a ctype wrap or a gobject wrap - as I hadnt noticed before
    # // but the Account is GType object - looks like all gnucash typed structures
    # // structures are also GTypes

    # // return a PyCObject - still need ctypes to extract
    # //PyObject *data_obj = PyCObject_FromVoidPtr((void *)data, NULL);
    # // another option - return a LongLong with address
    # // and again use ctypes to extract
    # //PyObject *data_obj = PyLong_FromUnsignedLongLong((unsigned PY_LONG_LONG)data);

    before = ('    if (strcmp(PyString_AsString(PyObject_GetAttrString(py_%(name)s,"__name__")),"Account") == 0)\n'
              '        %(name)s = (Account*)PyObject_CallMethod(py_%(name)s,"__long__",NULL);\n'
              '    else\n'
              '        %(name)s = (Account*)PyCObject_AsVoidPtr(py_%(name)s);\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('Account', '*'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('gpointer', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return PyCObject_FromVoidPtr(ret, NULL);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('Account*', Account())

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
                              '    }');

matcher.register('gpointer', gpointer())

class GList(ArgType):

    before = ('    %(name)s = (GList *)(((PyGPointer *)(py_%(name)s))->pointer);\n')

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
                              '    }');

matcher.register('GList*', GList())
