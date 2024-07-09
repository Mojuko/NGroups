from . import Data

import bpy
import math
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, PointerProperty, IntProperty, \
                      StringProperty, FloatVectorProperty, EnumProperty
from bpy.types import PropertyGroup

class NGROUPS_VectorLayer(PropertyGroup):
    Index: IntProperty(default = 0)
    Type: StringProperty(default = '')
    Value: StringProperty(default = '')
    
class NGROUPS_NormalGroupProperties(PropertyGroup):
    Angle: FloatProperty(name = 'Angle', subtype = 'ANGLE', soft_min = -math.pi, soft_max = math.pi)
    Color: FloatVectorProperty(name = '', subtype = 'COLOR', soft_min = 0, soft_max = 1)
    Index: IntProperty(default = 0)
    Visible: BoolProperty(default = True)
    XMirror: BoolProperty(default = False)
    YMirror: BoolProperty(default = False)
    
    IsVectorLayer: BoolProperty(default = False)
    VectorIndex: IntProperty(default = 0)
    VectorGroups: CollectionProperty(type = NGROUPS_VectorLayer)
    VectorUniqueIndex: IntProperty(default = 0)

    
class NGROUPS_NormalEditingVariables(PropertyGroup):
    HasData: BoolProperty(default = False)
    NormalGroups: CollectionProperty(type = NGROUPS_NormalGroupProperties)
    GroupIndex: IntProperty(default = 0)
    UniqueIndex: IntProperty(default = 0)
    AutoUpdateGroups: BoolProperty(default = True)
    UpdateNormalsWithCompute: BoolProperty(default = True)

    Factor: FloatProperty(name = 'Corner weight', default = 1, soft_min = 0, soft_max = 1, step = 1)
    
    DefaultColor: FloatVectorProperty(name = '', subtype = 'COLOR', soft_min = 0, soft_max = 1)
    
    GeneralOffsetAngle: FloatProperty(default = 0, subtype = 'ANGLE',  soft_min = -math.pi, soft_max = math.pi)
    
    HasCheckerMaterial: BoolProperty(default = False)
    OriginalMaterials: StringProperty(default = '')

    HoldObject: BoolProperty(default = False)
    
    Shape: EnumProperty(items=Data.Shapes)
    
    VectorFactor: FloatProperty(name = 'Weight', default = 1, soft_min = 0, soft_max = 1, step = 1)
    NormalDistance: FloatProperty(name = 'Normal distance', default = 1, soft_min = 0, soft_max = 1, step = 1)
    
    SmoothFactor: FloatProperty(default = 1, soft_min = 0, soft_max = 1, step = 1)
    
    
classes = [
    NGROUPS_VectorLayer,
    NGROUPS_NormalGroupProperties,
    NGROUPS_NormalEditingVariables
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.props.NGroups_EditingMesh = PointerProperty(type = bpy.types.Mesh)
    bpy.types.Mesh.NGroups = PointerProperty(type = NGROUPS_NormalEditingVariables)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.props.NGroups_EditingMesh
    del bpy.types.Mesh.NGroups