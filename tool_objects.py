

# 

import traceback

import pdb


class ToolTemplate(object):

    # object new Tools should be subclassed from

    def __init__ (self):

        self.tool_guid = None
        self.name = None
        self.menu_name = None
        self.menu_tip = None
        self.menu_path = None
        self.stock_id = None

    def run (self):
        raise NotImplementedError("The run method MUST be defined in the subclass!!")



# we need these dicts to lookup the tool object on callback

python_tools_by_name = {}
python_tools_by_guid = {}

def load_python_tools ():
    # yes we need the global to write into these objects
    global python_tools_by_name
    global python_tools_by_guid

    #pdb.set_trace()

    python_tools_by_name = {}
    python_tools_by_gui = {}

    if False:

        try:
            from tools.hello_world import HelloWorld
            python_tools_by_name['HelloWorld'] = HelloWorld()
        except Exception, errexc:
            traceback.print_exc()
            pdb.set_trace()

    if True:

        # code to try for autoimporting - so can just add new tools
        # only works assuming always use class name as tools name in python_tools

        try:
            import tools
        except Exception, errexc:
            traceback.print_exc()
            pdb.set_trace()

        # if we want to find all new classes another way is to use introspection
        # and find all classes whose __module__ attribute is the module name it was imported
        # under

        # this is a very sneaky way to find new classes if all classes you want
        # are guaranteed to be subclasses of a specific class
        __all__classes = [ cls for cls in ToolTemplate.__subclasses__() ]

        # instantiate all tool objects and save in the lookup dicts

        for tool_cls in __all__classes:
            python_tools_by_name[tool_cls.__name__] = tool_cls()
            python_tools_by_guid[python_tools_by_name[tool_cls.__name__].tool_guid] = python_tools_by_name[tool_cls.__name__]

