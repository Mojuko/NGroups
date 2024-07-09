from . import Data, Functions, Operators
import bpy, gpu, blf, bmesh, bpy_extras, mathutils
import math

from bpy.types import Context, Operator
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, PointerProperty, IntProperty, \
                      StringProperty, FloatVectorProperty
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

class NGroups_TOOL_Empty(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'
    bl_idname = 'ngroups.empty_tool'
    bl_label = 'Empty tool'
    bl_description = (
        'Used to prevent selection'
    )
    bl_icon = None
    bl_widget = None
    bl_keymap = (
        ('ngroups.op_empty', {'type': 'ESC', 'value': 'PRESS'}, None),
        ('ngroups.op_empty', {'type': 'LEFTMOUSE', 'value': 'CLICK'}, None),
        ('ngroups.op_empty', {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG'}, None),
        ('ngroups.op_empty', {'type': 'RIGHTMOUSE', 'value': 'PRESS'}, None),
        ('ngroups.op_empty', {'type': 'F', 'value': 'PRESS'}, None)
    )

class NGROUPS_OT_Empty(Operator):
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_idname = 'ngroups.op_empty'
    bl_label = 'Empty operator'
   
    def invoke(self, context, event):
        return {'FINISHED'}

class NGROUPS_OT_SmoothBrush(Operator):
    bl_idname = 'ngroups.smooth_brush'
    bl_label = 'Smooth brush operator'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    Stop = False
    
    PreviousToolName = None
    State = "STOP"
    RadiusChange = False
    Radius = 100

    MousePosition = (0,0)
    CirclePoints = []
    Handler = None
    
    ChangeHandler = None
    ChangePoints = []
    RadiusChange = False
    newRadius = 0
    
    bm = None

    def invoke(self, context, event):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        if NGROUPS_OT_SmoothBrush.State == "STOP" and NGROUPS_OT_SmoothBrush.Stop == False:
            NGROUPS_OT_SmoothBrush.State = "RUNNING"
            NGROUPS_OT_SmoothBrush.Stop == False
            context.window_manager.modal_handler_add(self)
            NGROUPS_OT_SmoothBrush.Handler = bpy.types.SpaceView3D.draw_handler_add(DrawCircle, (), 'WINDOW', 'POST_PIXEL')
            NGROUPS_OT_SmoothBrush.PreviousToolName = context.workspace.tools.from_space_view3d_mode("EDIT_MESH", create=False).idname
            bpy.ops.wm.tool_set_by_id(name = 'ngroups.empty_tool', space_type = "VIEW_3D")
            NGROUPS_OT_SmoothBrush.CirclePoints = GetCirclePoints(NGROUPS_OT_SmoothBrush.Radius, 30)
            
            return {"RUNNING_MODAL"}
        elif NGROUPS_OT_SmoothBrush.State == "RUNNING" and NGROUPS_OT_SmoothBrush.Stop == True:
            NGROUPS_OT_SmoothBrush.Stop = False
            NGROUPS_OT_SmoothBrush.State = "STOP"
        
        return {'FINISHED'}

  
    def modal(self, context, event):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        
        if context.active_object.mode != 'EDIT' or NGROUPS_OT_SmoothBrush.State == "STOP" or context.workspace.tools.from_space_view3d_mode("EDIT_MESH", create=False).idname != 'ngroups.empty_tool':
            NGROUPS_OT_SmoothBrush.State = "STOP"
            NGROUPS_OT_SmoothBrush.StopRunning(context)
            return {"FINISHED"}
        
        if event.type == "F" and event.value == "PRESS":
            NGROUPS_OT_SmoothBrush.RadiusChange = True
            NGROUPS_OT_SmoothBrush.ChangePoints = GetCirclePoints(NGROUPS_OT_SmoothBrush.Radius, 30)
            NGROUPS_OT_SmoothBrush.ChangeHandler = bpy.types.SpaceView3D.draw_handler_add(DrawChange, (), 'WINDOW', 'POST_PIXEL')

        if event.type == "LEFTMOUSE" and event.value == "PRESS" and NGROUPS_OT_SmoothBrush.RadiusChange == False and event.value != "CLICK":
            bpy.ops.ngroups.smooth_brush_draw('INVOKE_DEFAULT')

            
        elif event.type == "LEFTMOUSE" and event.value == "RELEASE" and NGROUPS_OT_SmoothBrush.RadiusChange == True:
            NGROUPS_OT_SmoothBrush.RadiusChange = False
            bpy.types.SpaceView3D.draw_handler_remove(NGROUPS_OT_SmoothBrush.ChangeHandler, 'WINDOW')
            NGROUPS_OT_SmoothBrush.Radius = NGROUPS_OT_SmoothBrush.NewRadius
            NGROUPS_OT_SmoothBrush.CirclePoints = NGROUPS_OT_SmoothBrush.ChangePoints.copy()
            
        elif (event.type == "ESC" or event.type == "RIGHTMOUSE") and event.value == "PRESS" and NGROUPS_OT_SmoothBrush.RadiusChange == True:
            NGROUPS_OT_SmoothBrush.RadiusChange = False
            bpy.types.SpaceView3D.draw_handler_remove(NGROUPS_OT_SmoothBrush.ChangeHandler, 'WINDOW')
            
        if (NGROUPS_OT_SmoothBrush.RadiusChange == False):
            NGROUPS_OT_SmoothBrush.MousePosition = (event.mouse_x - context.area.x, event.mouse_y - context.area.y)
        else:
            delta = NGROUPS_OT_SmoothBrush.MousePosition[0] - event.mouse_x
            NGROUPS_OT_SmoothBrush.NewRadius = max(1, NGROUPS_OT_SmoothBrush.Radius - delta)
            NGROUPS_OT_SmoothBrush.ChangePoints = GetCirclePoints(NGROUPS_OT_SmoothBrush.NewRadius, 30)

        context.area.tag_redraw()
        return {"PASS_THROUGH"}
    
    def StopRunning(context):
        if context.active_object.mode == 'EDIT':
            bpy.ops.wm.tool_set_by_id(name = NGROUPS_OT_SmoothBrush.PreviousToolName, space_type = "VIEW_3D")
            
        bpy.types.SpaceView3D.draw_handler_remove(NGROUPS_OT_SmoothBrush.Handler, 'WINDOW')
        if NGROUPS_OT_SmoothBrush.RadiusChange == True:
            bpy.types.SpaceView3D.draw_handler_remove(NGROUPS_OT_SmoothBrush.ChangeHandler, 'WINDOW')
        NGROUPS_OT_SmoothBrushDraw.Stop = True
        NGROUPS_OT_SmoothBrush.RadiusChange = False
        NGROUPS_OT_SmoothBrush.Stop = False
            


class NGROUPS_OT_SmoothBrushDraw(Operators.OPTemplate, Operator):
    bl_idname = 'ngroups.smooth_brush_draw'
    bl_label = 'Smooth brush draw'
    
    Running = False
    Stop = False

    def invoke(self, context, event):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        if NGROUPS_OT_SmoothBrushDraw.Running == False:
            context.window_manager.modal_handler_add(self)
            NGROUPS_OT_SmoothBrushDraw.Running = True
            
            bm  = bmesh.from_edit_mesh(mesh)
            verts = GetVertsFromRadius(bm, context, NGROUPS_OT_SmoothBrush.MousePosition, NGROUPS_OT_SmoothBrush.Radius)
                
            layer = Functions.GetActiveLayer(bm)
            Functions.SmoothFromNeighbourVertices(bm, verts, layer)
            bmesh.update_edit_mesh(mesh)
            bm.free()
            return {"RUNNING_MODAL"}
        else:
            return {"FINISHED"}

  
    def modal(self, context, event):
        
        if (event.type == "LEFTMOUSE" and event.value == "RELEASE" and NGROUPS_OT_SmoothBrushDraw.Running == True) or NGROUPS_OT_SmoothBrushDraw.Stop == True or event.type == "INBETWEEN_MOUSEMOVE":
            NGROUPS_OT_SmoothBrushDraw.Running = False
            NGROUPS_OT_SmoothBrushDraw.Stop = False
            return {"FINISHED"}
        
        mesh = bpy.props.NGroups_EditingMesh
        bm  = bmesh.from_edit_mesh(mesh)
        verts = GetVertsFromRadius(bm, context, NGROUPS_OT_SmoothBrush.MousePosition, NGROUPS_OT_SmoothBrush.Radius)
        
        layer = Functions.GetActiveLayer(bm)
        Functions.SmoothFromNeighbourVertices(bm, verts, layer)
        bmesh.update_edit_mesh(mesh)
        bm.free()
        return {"PASS_THROUGH"}
    
def GetVertsFromRadius(bm, context, mousePos, radius):
    obj = context.active_object
    objMatrix = obj.matrix_world
    mousePos = Vector(mousePos)
    viewVector = context.region_data.view_rotation @ Vector((0.0, 0.0, 1.0))
    selectedVerts = set([vert for vert in bm.verts if (bpy_extras.view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.space_data.region_3d,objMatrix @ vert.co) - mousePos).length <= radius and vert.normal.dot(viewVector) > 0])
    return selectedVerts

def DrawCircle():
    
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.0)
    points = [AddPositions(point, NGROUPS_OT_SmoothBrush.MousePosition) for point in NGROUPS_OT_SmoothBrush.CirclePoints]
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points})
    shader.uniform_float("color", (1, 0.3, 0.3, 0.5))
    batch.draw(shader)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')

def DrawChange():
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.0)
    points = [AddPositions(point, NGROUPS_OT_SmoothBrush.MousePosition) for point in NGROUPS_OT_SmoothBrush.ChangePoints]
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points})
    shader.uniform_float("color", (1, 0.3, 0.3, 0.5))
    batch.draw(shader)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')

def GetCirclePoints(radius, resolution):
    positions = []
    deltaAngle = 2 * math.pi / resolution
    for i in range(0, resolution + 1, 1):
        angle = deltaAngle * i
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions.append((x,y))
    return positions

def AddPositions(point, offset):
    return (point[0] + offset[0], point[1] + offset[1])



def unregister_tool(idname, space_type, context_mode):
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    tools = cls._tools[context_mode]
            
    for i, tool_group in enumerate(tools):        
        if isinstance(tool_group, tuple):
            for t in tool_group:
                if 'ToolDef' in str(type(t)) and t.idname == idname:
                    if len(tools[i]) == 1:
                        # it's a group with a single item, just remove it from the tools list.
                        tools.pop(i)
                    else:
                        tools[i] = tuple(x for x in tool_group if x.idname != idname)
                    break
        elif tool_group is not None:
            if tool_group.idname == idname:
                tools.pop(i)
                break
    
    # cleanup any doubled up separators left over after removing a tool
    for i, p in enumerate(reversed(tools)):
        if i < len(tools)-2 and tools[i] is None and tools[i+1] is None:
            tools.pop(i)

classes = [
    NGROUPS_OT_Empty,
    NGROUPS_OT_SmoothBrushDraw,
    NGROUPS_OT_SmoothBrush,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    unregister_tool('ngroups.empty_tool', 'VIEW_3D', 'EDIT_MESH')
    bpy.utils.register_tool(NGroups_TOOL_Empty, after={"builtin.rip_region"}, separator=True, group=True)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    unregister_tool('ngroups.empty_tool', 'VIEW_3D', 'EDIT_MESH')
    