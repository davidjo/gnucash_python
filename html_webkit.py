
import pdb


from function_class import \
     ClassFromFunctions, extract_attributes_with_prefix, \
     default_arguments_decorator, method_function_returns_instance, \
     methods_return_instance, process_list_convert_to_instance, \
     method_function_returns_instance_list, methods_return_instance_lists

from gnucash_core import GnuCashCoreClass


import html_webkit_c


class GncHtml(GnuCashCoreClass):
    # the main window instance
    # must re-define _module
    _module = html_webkit_c
    #_new_instance = 'xaccMallocAccount'
    pass

# GncHtmlWebkit
pdb.set_trace()
# crap - this will add gnc_html_webkit_... methods
GncHtml.add_constructor_and_methods_with_prefix('gnc_html_', 'new')


class GncHtmlWebkit(GnuCashCoreClass):
    # the main window instance
    # must re-define _module
    _module = html_webkit_c
    #_new_instance = 'xaccMallocAccount'
    pass

# GncHtmlWebkit
pdb.set_trace()
GncHtmlWebkit.add_constructor_and_methods_with_prefix('gnc_html_webkit_', 'new')

#GncHtmlWebkit.get_book = method_function_returns_instance(
#    Session.get_book, Book )

#GncHtmlWebkit.get_book = method_function_returns_instance(
#    GncHtmlWebkit.get_book, Book )

#GncHtmlWebkit.book = property( GncHtmlWebkit.get_book )

# we cannot instatiate until we have a screen!!

pdb.set_trace()
print "junk"

