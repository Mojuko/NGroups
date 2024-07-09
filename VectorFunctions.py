from . import Data, Functions, Operators

import bpy, gpu, blf, bmesh, bpy_extras, mathutils
import math

from bpy.types import Context, Operator
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, PointerProperty, IntProperty, \
                      StringProperty, FloatVectorProperty
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

def AddVectorData(mesh):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    activeGroup.IsVectorLayer = True
    
    attributeData = []
    attributeData.append(Data.VectorIndexAttribute[0] + f"{activeGroup.Index}")
    attributeData.append(Data.VectorIndexAttribute[1])
    attributeData.append(Data.VectorIndexAttribute[2])

    attribute = Functions.AddAttributeToMesh(mesh, attributeData)

def RemoveSelectedGroupVectorData(mesh):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    RemoveVectorAttributeByIndex(mesh, activeGroup.Index)
    
    activeGroup.VectorUniqueIndex = 0
    activeGroup.VectorIndex = 0
    activeGroup.IsVectorLayer = False
    activeGroup.VectorGroups.clear()

def GetVectorAttributeByIndex(mesh, index):
    name = Data.VectorIndexAttribute[0] + f"{index}"
    attribute = mesh.attributes.get(name)
    return attribute

def RemoveVectorAttributeByIndex(mesh, index):
    
    attribute = GetVectorAttributeByIndex(mesh, index)
    if attribute != None:
        mesh.attributes.remove(attribute)
        
    
def AddVectorGroup(mesh):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    newGroup = activeGroup.VectorGroups.add()
    activeGroup.VectorIndex = len(activeGroup.VectorGroups) - 1
    activeGroup.VectorUniqueIndex = activeGroup.VectorUniqueIndex + 1
    newGroup.name = f'New vector.{activeGroup.VectorUniqueIndex:03}'
    newGroup.Type = ''
    newGroup.Index = activeGroup.VectorUniqueIndex

def RemoveVectorSelectedGroup(mesh):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    
    if len(variables.NormalGroups) > 0:        
        
        activeGroup.VectorIndex = Functions.ui_item_remove(activeGroup.VectorGroups, activeGroup.VectorIndex)
        
def SetShapeForLayer(mesh, vectorShape):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    activeVectorGroup = activeGroup.VectorGroups[activeGroup.VectorIndex]
    activeVectorGroup.Type = vectorShape
    activeGroup.value = ''

def GetBmeshLoopIntVectorLayerFromIndex(bm, index):
    name = Data.VectorIndexAttribute[0] + f"{index}"
    layer = bm.loops.layers.int.get(name)
    return layer

def AssignSelectionToVector(mesh):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    activeVectorGroup = activeGroup.VectorGroups[activeGroup.VectorIndex]
    index = activeVectorGroup.Index
    
    bm = bmesh.from_edit_mesh(mesh)
    
    vectorLayer = GetBmeshLoopIntVectorLayerFromIndex(bm, activeGroup.Index)
    selectedLoops = Functions.GetSelectedLoops(bm)
    
    for loop in selectedLoops:
        loop[vectorLayer] = index

    bmesh.update_edit_mesh(mesh)
    bm.free()
    
def RemoveSelectionFromVector(mesh):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    activeVectorGroup = activeGroup.VectorGroups[activeGroup.VectorIndex]
    index = activeVectorGroup.Index
    
    bm = bmesh.from_edit_mesh(mesh)
    
    vectorLayer = GetBmeshLoopIntVectorLayerFromIndex(bm, activeGroup.Index)
    selectedLoops = Functions.GetSelectedLoops(bm)
    
    for loop in selectedLoops:
        loop[vectorLayer] = 0

    bmesh.update_edit_mesh(mesh)
    bm.free()
    
def GetLoopsFromVector(bm, index, layer):
    loops = Functions.GetAllLoops(bm)
    selectedLoops = [loop for loop in loops if loop[layer] == index]
    return selectedLoops

def SelectFromVector(mesh, select):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    activeVectorGroup = activeGroup.VectorGroups[activeGroup.VectorIndex]
    index = activeVectorGroup.Index
    
    bm = bmesh.from_edit_mesh(mesh)
    
    vectorLayer = GetBmeshLoopIntVectorLayerFromIndex(bm, activeGroup.Index)
    loops = GetLoopsFromVector(bm, index, vectorLayer)
    
    selectionMode = bpy.context.tool_settings.mesh_select_mode[:]
    if (selectionMode[2] == True):
        for loop in loops:
            loop.face.select = select
    
    if (selectionMode[0] == True or selectionMode[1] == True):
        for loop in loops:
            loop.vert.select = select

    bmesh.update_edit_mesh(mesh)
    bm.free()
    
def DrawNormals():
    
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.0)
    points = NGROUPS_OT_DrawNormals.Points
    batch = batch_for_shader(shader, 'LINES', {"pos": points})
    shader.uniform_float("color", (1, 0.3, 0.3, 0.5))
    batch.draw(shader)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')
    
def GetSpherizeNormalPoints(obj, bm, position, index, distance, flip):
    points = []
    mesh = bpy.props.NGroups_EditingMesh
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    vectorLayer = GetBmeshLoopIntVectorLayerFromIndex(bm, activeGroup.Index)
    loops = GetLoopsFromVector(bm, index, vectorLayer)
    verts = set([loop.vert for loop in loops])
    objMatrix = obj.matrix_world
    mulFactor = 1
    if flip:
        mulFactor = -1
    for vert in verts:
        startPoint = objMatrix @ vert.co
        endPoint = -(position - startPoint).normalized() * distance * mulFactor + startPoint
        points.append(startPoint.to_tuple())
        points.append(endPoint.to_tuple())
    return points
def GetPlaneNormalPoints(obj, bm, direction, index, distance, flip):
    points = []
    mesh = bpy.props.NGroups_EditingMesh
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    vectorLayer = GetBmeshLoopIntVectorLayerFromIndex(bm, activeGroup.Index)
    loops = GetLoopsFromVector(bm, index, vectorLayer)
    verts = set([loop.vert for loop in loops])
    objMatrix = obj.matrix_world
    mulFactor = 1
    if flip:
        mulFactor = -1
    for vert in verts:
        startPoint = objMatrix @ vert.co
        endPoint = direction.normalized() * distance * mulFactor + startPoint
        points.append(startPoint.to_tuple())
        points.append(endPoint.to_tuple())
    return points

def SetValue(vectorType, obj, flip):
    if vectorType == 'SPHERE':
        return f'{obj.location.x:.4f},{obj.location.y:.4f},{obj.location.z:.4f};{int(flip)}'
    elif vectorType == 'PLANE':
        return f'{obj.rotation_euler.x:.4f},{obj.rotation_euler.y:.4f},{obj.rotation_euler.z:.4f};{int(flip)}'


class NGROUPS_OT_DrawNormals(Operator):
    bl_idname = 'ngroups.draw_normals'
    bl_label = 'Draw normals'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    Mesh = None
    Running = False
    Stop = False
    Points = []
    Index = 0
    Handler = None
    CenterObject = None    
    Object = None
    Set = False
    HasHandler = False
    FlipNormals = False
    def invoke(self, context, event):
        if NGROUPS_OT_DrawNormals.Running == False:
            NGROUPS_OT_DrawNormals.Object = context.active_object
            
            mesh = bpy.props.NGroups_EditingMesh
            variables = mesh.NGroups
            activeGroup = variables.NormalGroups[variables.GroupIndex]
            activeVectorGroup = activeGroup.VectorGroups[activeGroup.VectorIndex]
            index = activeVectorGroup.Index
            variables.HoldObject = True
            context.window_manager.modal_handler_add(self)
            NGROUPS_OT_DrawNormals.Running = True
            NGROUPS_OT_DrawNormals.Index = index
            
            bm  = bmesh.from_edit_mesh(mesh)
            
            obj = bpy.data.objects.new( "empty", None )
            NGROUPS_OT_DrawNormals.CenterObject = obj
            context.scene.collection.objects.link( obj )
            obj.empty_display_size = 0.5
            obj.show_in_front = True
            flip = False
            if activeVectorGroup.Type == 'SPHERE':
                obj.empty_display_type = 'SPHERE'
                
                if activeVectorGroup.Value != '':
                    pos = activeVectorGroup.Value.split(';')[0].split(',')
                    flip = bool(int(activeVectorGroup.Value.split(';')[1]))
                    obj.location = Vector((float(pos[0]),float(pos[1]),float(pos[2])))
                NGROUPS_OT_DrawNormals.Points = GetSpherizeNormalPoints(NGROUPS_OT_DrawNormals.Object, bm, obj.location, index, variables.NormalDistance, flip)
            elif activeVectorGroup.Type == 'PLANE':
                obj.empty_display_size = 1
                obj.empty_display_type = 'SINGLE_ARROW'
                if activeVectorGroup.Value != '':
                    
                    eulerRot = activeVectorGroup.Value.split(';')[0].split(',')
                    flip = bool(int(activeVectorGroup.Value.split(';')[1]))
                    obj.rotation_euler = Vector((float(eulerRot[0]),float(eulerRot[1]),float(eulerRot[2])))
                vec = Vector((0,0,1))
                direction = obj.rotation_euler.to_matrix() @ vec
                NGROUPS_OT_DrawNormals.Points = GetPlaneNormalPoints(NGROUPS_OT_DrawNormals.Object, bm, direction, index, variables.NormalDistance, flip)
            NGROUPS_OT_DrawNormals.FlipNormals = flip
            NGROUPS_OT_DrawNormals.Handler = bpy.types.SpaceView3D.draw_handler_add(DrawNormals, (), 'WINDOW', 'POST_VIEW')
            NGROUPS_OT_DrawNormals.HasHandler = True                   

            bmesh.update_edit_mesh(mesh)
            bm.free()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            obj.select_set(True)
            NGROUPS_OT_DrawNormals.Object.select_set(False)
            return {"RUNNING_MODAL"}
        else:
            return {"FINISHED"}
    
    def modal(self, context, event):
        if len(context.selected_objects) <= 0 or context.selected_objects[0] != NGROUPS_OT_DrawNormals.CenterObject or context.active_object.mode != "OBJECT":
            NGROUPS_OT_DrawNormals.StopRunning()
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        activeGroup = variables.NormalGroups[variables.GroupIndex]
        activeVectorGroup = activeGroup.VectorGroups[activeGroup.VectorIndex]
        index = activeVectorGroup.Index
        
        if NGROUPS_OT_DrawNormals.Stop == True:
            if NGROUPS_OT_DrawNormals.Set:
                activeVectorGroup.Value = SetValue(activeVectorGroup.Type, NGROUPS_OT_DrawNormals.CenterObject, NGROUPS_OT_DrawNormals.FlipNormals)
                NGROUPS_OT_DrawNormals.Set = False
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            NGROUPS_OT_DrawNormals.Running = False
            NGROUPS_OT_DrawNormals.Stop = False
            if NGROUPS_OT_DrawNormals.HasHandler == True:
                bpy.types.SpaceView3D.draw_handler_remove(NGROUPS_OT_DrawNormals.Handler, 'WINDOW')
                NGROUPS_OT_DrawNormals.HasHandler = False
            variables.HoldObject = False
            bpy.data.objects.remove(NGROUPS_OT_DrawNormals.CenterObject, do_unlink=True)
            NGROUPS_OT_DrawNormals.Object.select_set(True)
            NGROUPS_OT_DrawNormals.Object = None
            NGROUPS_OT_DrawNormals.FlipNormals = False
            return {"FINISHED"}
        
        if event.type != 'MOUSEMOVE':
            bm = bmesh.new()
            bm.from_mesh(mesh)
            if activeVectorGroup.Type == 'SPHERE':
                NGROUPS_OT_DrawNormals.Points = GetSpherizeNormalPoints(NGROUPS_OT_DrawNormals.Object, bm, NGROUPS_OT_DrawNormals.CenterObject.location, index, variables.NormalDistance, NGROUPS_OT_DrawNormals.FlipNormals)
            elif activeVectorGroup.Type == 'PLANE':
                vec = Vector((0,0,1))
                direction = NGROUPS_OT_DrawNormals.CenterObject.rotation_euler.to_matrix() @ vec
                NGROUPS_OT_DrawNormals.Points = GetPlaneNormalPoints(NGROUPS_OT_DrawNormals.Object, bm, direction, index, variables.NormalDistance, NGROUPS_OT_DrawNormals.FlipNormals)
            bm.free()
            context.area.tag_redraw()
            
        return {"PASS_THROUGH"}
    
    def StopRunning():
        NGROUPS_OT_DrawNormals.Stop = True
        
    def Apply():
        NGROUPS_OT_DrawNormals.Set = True
        

class NGROUPS_OT_ApplyVector(Operators.OPTemplate, Operator):
    bl_idname = 'ngroups.apply_vector'
    bl_label = 'Apply vector'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        activeGroup = variables.NormalGroups[variables.GroupIndex]
        activeVectorGroup = activeGroup.VectorGroups[activeGroup.VectorIndex]
        NGROUPS_OT_DrawNormals.Apply()
        NGROUPS_OT_DrawNormals.StopRunning()
        return {'FINISHED'}
    
class NGROUPS_OT_CancelVector(Operator):
    bl_idname = 'ngroups.cancel_vector'
    bl_label = 'Cancel vector'
    bl_options = {'REGISTER', 'INTERNAL'}    

    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        activeGroup = variables.NormalGroups[variables.GroupIndex]
        activeVectorGroup = activeGroup.VectorGroups[activeGroup.VectorIndex]
        
        NGROUPS_OT_DrawNormals.StopRunning()
        return {'FINISHED'}

class NGROUPS_OT_FlipNormals(Operator):
    bl_idname = 'ngroups.flip_normals'
    bl_label = 'Flip noramls'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        NGROUPS_OT_DrawNormals.FlipNormals = not NGROUPS_OT_DrawNormals.FlipNormals
        
        return {'FINISHED'}


classes = [
    NGROUPS_OT_DrawNormals,
    NGROUPS_OT_ApplyVector,
    NGROUPS_OT_CancelVector,
    NGROUPS_OT_FlipNormals
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)