ColorAttrbitue = ["NGroups_Colors",'BYTE_COLOR', 'CORNER']
BaseNormalsAttribute = ["NGroup_BaseNormals", 'FLOAT_VECTOR', 'CORNER']
ResultNormalsAttribute = ["NGroup_Result", 'FLOAT_VECTOR', 'CORNER']

MirrorAttributeX = ["NGroups_MirrorX", 'INT', 'CORNER']
MirrorAttributeY = ["NGroups_MirrorY", 'INT', 'CORNER']

AttributesArray = [ColorAttrbitue, BaseNormalsAttribute, ResultNormalsAttribute,
                   MirrorAttributeX, MirrorAttributeY]

GroupAttributes = ["NGroup_",'FLOAT', 'CORNER']

VectorIndexAttribute = ["NGroup_Vector_",'INT', 'CORNER']

CheckerMaterialName = "LayerChecker"


Shapes = [("PLANE", "Plane", "", "MESH_PLANE", 0),
          ("SPHERE", "Sphere", "", "SPHERE", 1),
         ]