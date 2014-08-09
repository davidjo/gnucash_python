

#from codegen.argtypes import ArgType, matcher
#from codegen import reversewrapper
from argtypes import ArgType, matcher
import reversewrapper


# these are callbacks
# in pygtk itself callbacks handled by wrapping PyCObjects
# so for the moment take these as PyCObjects
# unfortunately as we cant link to the pygtk code we need to replicate the code
# in gnctreeview somewhere

class GtkTreeIterCompareFunc(ArgType):

    before = ('    %(name)s = (GtkTreeIterCompareFunc)py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GtkTreeIterCompareFunc', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GtkTreeIterCompareFunc', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GtkTreeIterCompareFunc', GtkTreeIterCompareFunc())


class GtkTreeCellDataFunc(ArgType):

    before = ('    %(name)s = (GtkTreeCellDataFunc)py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GtkTreeCellDataFunc', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GtkTreeCellDataFunc', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GtkTreeCellDataFunc', GtkTreeCellDataFunc())


class GtkTreeViewColumn(ArgType):

    before = ('    %(name)s = (GtkTreeViewColumn)py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('GtkTreeViewColumn', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('GtkTreeViewColumn', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('GtkTreeViewColumn**', GtkTreeViewColumn())


class renderer_toggled(ArgType):

    before = ('    %(name)s = (renderer_toggled)py_%(name)s;\n')

    def write_param(self, ptype, pname, pdflt, pnull, info):
        info.varlist.add('PyObject', '*py_' + pname)
        info.varlist.add('renderer_toggled', pname)
        info.add_parselist('O', ['&py_'+pname], [pname])
        info.arglist.append(pname)
        info.codebefore.append (self.before % { 'name' : pname, 'namecopy' : 'NULL' })


    def write_return(self, ptype, ownsreturn, info):
        info.varlist.add('renderer_toggled', 'ret')
        info.codeafter.append('    if (ret)\n'
                              '        return pyg_pointer_new(G_TYPE_POINTER,ret);\n'
                              '    else {\n'
                              '        Py_INCREF(Py_None);\n'
                              '        return Py_None;\n'
                              '    }');

matcher.register('renderer_toggled', renderer_toggled())

