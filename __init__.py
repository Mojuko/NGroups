import importlib

bl_info = {
    "name": "NGroups",
    "author": "Mojuko",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "description": "Normal groups for faces",
    "category": "3D View"
}


from . import Functions, Operators, UI, Properties, Data, MaterialFunctions, Brushes, VectorFunctions

importlib.reload(Data)
importlib.reload(Functions)
importlib.reload(VectorFunctions)
importlib.reload(Operators)
importlib.reload(UI)
importlib.reload(Properties)
importlib.reload(MaterialFunctions)
importlib.reload(Brushes)

def register():
    Properties.register()
    VectorFunctions.register()
    Operators.register()
    Brushes.register()
    UI.register()

def unregister():
    UI.unregister()
    Brushes.unregister()
    Operators.unregister()
    VectorFunctions.unregister()
    Properties.unregister()


if __name__ == "__main__":
    register()