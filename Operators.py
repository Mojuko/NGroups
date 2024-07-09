from . import Functions, MaterialFunctions, VectorFunctions
import bpy

from bpy.types import Context, Mesh, Operator, Panel, UIList, Menu, PropertyGroup
from bpy.props import BoolProperty, StringProperty

class OPTemplate:
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

class NGROUPS_OT_CreateNGroups(OPTemplate, Operator):
    bl_idname = 'ngroups.create_ngroups'
    bl_label = 'Create NGroups'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        
        Functions.AddData(mesh)
        return {'FINISHED'}

class NGROUPS_OT_RemoveNGroups(OPTemplate, Operator):
    bl_idname = 'ngroups.remove_ngroups'
    bl_label = 'Remove NGroups'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups

        Functions.RemoveData(mesh)
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class NGROUPS_OT_NormalGroupAdd(OPTemplate, Operator):
    bl_idname = 'ngroups.normalgroup_add'
    bl_label = 'Add group'
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        Functions.AddGroup(mesh)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}

class NGROUPS_OT_NormalGroupRemove(OPTemplate, Operator):
    bl_idname = 'ngroups.normalgroup_remove'
    bl_label = 'Remove group'
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        Functions.RemoveSelectedGroup(mesh)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}

class NGROUPS_OT_NormalGroupMove(OPTemplate, Operator):
    bl_idname = 'ngroups.normalgroup_move'
    bl_label = 'Move group'
    
    direction: StringProperty(default='UP', options={'HIDDEN'})    

    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        
        if len(variables.NormalGroups) > 0:
            variables.GroupIndex = Functions.ui_item_move(variables.NormalGroups, variables.GroupIndex, self.direction)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}
    
class NGROUPS_OT_AssignAttributeFactor(OPTemplate, Operator):
    bl_idname = 'ngroups.assign_attribute_factor'
    bl_label = 'Assign to group'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups       
        
        Functions.SetSelectedGroupFactor(mesh, variables.Factor)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}
    
class NGROUPS_OT_RemoveGroupFactor(OPTemplate, Operator):
    bl_idname = 'ngroups.remove_attribute_factor'
    bl_label = 'Remove from group'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh      

        Functions.SetSelectedGroupFactor(mesh, 0)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}

class NGROUPS_OT_SelectGroup(OPTemplate, Operator):
    bl_idname = 'ngroups.select_groups'
    bl_label = 'select group'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh      

        Functions.LoopsFromAttribute(mesh, True)
        context.area.tag_redraw()
        return {'FINISHED'}

class NGROUPS_OT_DeselectGroup(OPTemplate, Operator):
    bl_idname = 'ngroups.deselect_groups'
    bl_label = 'select group'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh       

        Functions.LoopsFromAttribute(mesh, False)
        context.area.tag_redraw()
        return {'FINISHED'}

class NGROUPS_OT_ComputeResultNormals(OPTemplate, Operator):
    bl_idname = 'ngroups.compute_result_normals'
    bl_label = 'select group'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh    

        Functions.ComputeResult(mesh)
        return {'FINISHED'}

class NGROUPS_OT_WriteBaseNormals(OPTemplate, Operator):
    bl_idname = 'ngroups.write_base_normals'
    bl_label = 'Write layers to mesh normals'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh    

        Functions.SetDefaultNormalToAttribute_MODETOGGLE(mesh)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class NGROUPS_OT_SetMeshNormals(OPTemplate, Operator):
    bl_idname = 'ngroups.set_mesh_normals'
    bl_label = 'select group'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh    

        Functions.SetMeshNormals_MODETOGGLE(mesh)
        return {'FINISHED'}

class NGROUPS_OT_ComputeMirrors(OPTemplate, Operator):
    bl_idname = 'ngroups.compute_mirrors'
    bl_label = 'Compute mirrors'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh    

        Functions.ComputeMirrors(mesh)
        return {'FINISHED'}

class NGROUPS_OT_ToggleCheckerMaterial(OPTemplate, Operator):
    bl_idname = 'ngroups.toggle_checker_material'
    bl_label = 'Compute mirrors'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh    
        mesh.NGroups.HasCheckerMaterial = not mesh.NGroups.HasCheckerMaterial
        
        if mesh.NGroups.HasCheckerMaterial:
            MaterialFunctions.SetCheckerMaterial(mesh)
        else:
            MaterialFunctions.RemoveChekcerMaterial(mesh)
        return {'FINISHED'}

class NGROUPS_OT_SetMaterialFromLayer(OPTemplate, Operator):
    bl_idname = 'ngroups.set_material_from_layer'
    bl_label = 'Compute mirrors'

    layer: StringProperty(default='COLOR', options={'HIDDEN'})

    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh

        MaterialFunctions.SetMaterialAttributeValue(mesh, self.layer)
        return {'FINISHED'}

class NGroups_OT_SmoothFromNeighbourVertices(OPTemplate, Operator):
    bl_idname = 'ngroups.smooth_from_neighbour_vertices'
    bl_label = 'Smooth brush'
        
    def execute(self , context):
        mesh = bpy.props.NGroups_EditingMesh
        Functions.SmoothFromNeighbourVerticesFromMesh(mesh)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}

class NGROUPS_OT_AddVectorData(OPTemplate, Operator):
    bl_idname = 'ngroups.add_vector_data'
    bl_label = 'Add vector data to layer'
    
    def execute(self , context):
        mesh = bpy.props.NGroups_EditingMesh
        
        VectorFunctions.AddVectorData(mesh)
        return {'FINISHED'}

class NGROUPS_OT_RemoveVectorData(OPTemplate, Operator):
    bl_idname = 'ngroups.remove_vector_data'
    bl_label = 'Remove vector data from layer (data will be lost)'
    
    def execute(self , context):
        mesh = bpy.props.NGroups_EditingMesh
        
        VectorFunctions.RemoveSelectedGroupVectorData(mesh)
        return {'FINISHED'}
    
class NGROUPS_OT_VectorGroupAdd(OPTemplate, Operator):
    bl_idname = 'ngroups.vector_group_add'
    bl_label = 'Add group'
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        
        VectorFunctions.AddVectorGroup(mesh)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}

class NGROUPS_OT_VectorGroupRemove(OPTemplate, Operator):
    bl_idname = 'ngroups.vector_group_remove'
    bl_label = 'Remove group'
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        VectorFunctions.RemoveVectorSelectedGroup(mesh)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}

class NGROUPS_OT_VectorGroupMove(OPTemplate, Operator):
    bl_idname = 'ngroups.vector_group_move'
    bl_label = 'Move group'
    
    direction: StringProperty(default='UP', options={'HIDDEN'})    

    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        activeGroup = variables.NormalGroups[variables.GroupIndex]
        
        if len(activeGroup.VectorGroups) > 0:
            activeGroup.VectorIndex = Functions.ui_item_move(activeGroup.VectorGroups, activeGroup.VectorIndex, self.direction)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}
    
class NGROUPS_OT_SetVectorShape(OPTemplate, Operator):
    bl_idname = 'ngroups.set_vector_shape'
    bl_label = 'Set vector shape'
    

    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        
        VectorFunctions.SetShapeForLayer(mesh, variables.Shape)
        return {'FINISHED'}
    
class NGROUPS_OT_EditVector(OPTemplate, Operator):
    bl_idname = 'ngroups.edit_vector'
    bl_label = 'Edit vector'
    

    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        bpy.ops.ngroups.draw_normals('INVOKE_DEFAULT')
        return {'FINISHED'}
    
class NGROUPS_OT_AssignToVector(OPTemplate, Operator):
    bl_idname = 'ngroups.assign_to_vector'
    bl_label = 'Assign to vector'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups       
        
        VectorFunctions.AssignSelectionToVector(mesh)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}
    
class NGROUPS_OT_RemoveFromVector(OPTemplate, Operator):
    bl_idname = 'ngroups.remove_from_factor'
    bl_label = 'Remove from vector'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh      

        VectorFunctions.RemoveSelectionFromVector(mesh)
        if mesh.NGroups.AutoUpdateGroups:
            Functions.ComputeResult(mesh)
        return {'FINISHED'}

class NGROUPS_OT_SelectVector(OPTemplate, Operator):
    bl_idname = 'ngroups.select_vector'
    bl_label = 'Select vector'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh      
        VectorFunctions.SelectFromVector(mesh, True)
        context.area.tag_redraw()
        return {'FINISHED'}

class NGROUPS_OT_DeselectVector(OPTemplate, Operator):
    bl_idname = 'ngroups.deselect_vector'
    bl_label = 'Deselect vector'
    
    def execute(self, context):
        mesh = bpy.props.NGroups_EditingMesh       
        VectorFunctions.SelectFromVector(mesh, False)
        context.area.tag_redraw()
        return {'FINISHED'}
    
classes = [
    NGROUPS_OT_CreateNGroups,
    NGROUPS_OT_RemoveNGroups,
    NGROUPS_OT_NormalGroupAdd,
    NGROUPS_OT_NormalGroupRemove,
    NGROUPS_OT_NormalGroupMove,
    NGROUPS_OT_AssignAttributeFactor,
    NGROUPS_OT_RemoveGroupFactor,
    NGROUPS_OT_SelectGroup,
    NGROUPS_OT_DeselectGroup,
    NGROUPS_OT_ComputeResultNormals,
    NGROUPS_OT_WriteBaseNormals,
    NGROUPS_OT_SetMeshNormals,
    NGROUPS_OT_ComputeMirrors,
    NGROUPS_OT_ToggleCheckerMaterial,
    NGROUPS_OT_SetMaterialFromLayer,
    NGroups_OT_SmoothFromNeighbourVertices,
    
    NGROUPS_OT_AddVectorData,
    NGROUPS_OT_RemoveVectorData,
    NGROUPS_OT_VectorGroupAdd,
    NGROUPS_OT_VectorGroupRemove,
    NGROUPS_OT_VectorGroupMove,
    NGROUPS_OT_SetVectorShape,
    NGROUPS_OT_EditVector,
    NGROUPS_OT_AssignToVector,
    NGROUPS_OT_RemoveFromVector,
    NGROUPS_OT_SelectVector,
    NGROUPS_OT_DeselectVector
    
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)