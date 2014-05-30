
#from codegen.argtypes import ArgType, matcher
#from codegen import reversewrapper
from argtypes import ArgType, matcher
import reversewrapper


# oohh - this is sneaky - this is how we define a partial type

class GtkActionEntry(ArgType):

    before = ('    %(name)s = (GtkActionEntry*)py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GtkActionEntry', '*'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GtkActionEntry', '*ret')
        info.codeafter.append('    if (ret)\n'
                              '        return PyGtkActionEntry_FromActionEntry(ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GtkActionEntry*', GtkActionEntry())

class GtkToggleActionEntry(ArgType):

    before = ('    %(name)s = (GtkToggleActionEntry*)py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GtkToggleActionEntry', '*'+pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GtkToggleActionEntry', '*ret')
        info.codeafter.append('    if (ret)\n'
                              '        return PyGtkToggleActionEntry_FromActionToggleEntry(ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GtkToggleActionEntry*', GtkToggleActionEntry())


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
