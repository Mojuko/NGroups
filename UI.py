from . import Properties, Brushes
import bpy
import math

from bpy.types import Context, Mesh, Operator, Panel, UIList, Menu, PropertyGroup
from .Properties import NGROUPS_NormalGroupProperties, NGROUPS_NormalEditingVariables



class NGROUPS_UL_NormalGroups(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align = True)
        row.prop(item, 'name', text='', emboss=False, icon='MOD_NORMALEDIT')
        col = row.column()
        col.alignment = 'LEFT'
        if item.IsVectorLayer == False:
            col.label( text = f'{math.degrees(item.Angle):.2f} deg')
        else:
            col.label( text = f'Vector')
        rowSmall = row.row(align = True)
        if item.YMirror == False:
            col = rowSmall.column()
            col.ui_units_x = 1.
            col.prop(item, 'XMirror', text = 'X', toggle = 1)
        if item.XMirror == False:    
            col = rowSmall.column()
            col.ui_units_x = 1
            col.prop(item, 'YMirror', text = 'Y', toggle = 1)
        
        col = row.column()
        col.ui_units_x = 1
        col.prop(item, 'Color')
        
        col = row.column()
        col.ui_units_x = 1
        visibleIcon = 'HIDE_OFF'
        if item.Visible == False:
            visibleIcon = 'HIDE_ON'
        col.prop(item, 'Visible', icon = visibleIcon, icon_only = True, emboss = False)
        
class NGROUPS_UL_VectorGroups(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align = True)
        row.prop(item, 'name', text='', emboss=False, icon='ORIENTATION_GLOBAL')
        col = row.column()
        col.alignment = 'LEFT'
                
        col.label( text = f'{item.Type}')
        col = row.column()
        col.alignment = 'LEFT'
        col.label( text = f'{item.Value}')



class NGROUPS_PT_main(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NGroups'
    bl_idname = 'NGROUPS_PT_main'
    bl_label = 'NGroups'

    EditedObject = None

    @classmethod
    def poll(self, context):
        obj = context.active_object
        if obj != None and bpy.context.active_object.mode == "EDIT":
            return True
        elif NGROUPS_PT_main.EditedObject != None:
            if NGROUPS_PT_main.EditedObject.data.NGroups.HoldObject:
                return True
        else:
            return False


    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        

        if obj != None and type(obj.data) == bpy.types.Mesh and bpy.context.active_object.mode == "EDIT":
            mesh = obj.data
            bpy.props.NGroups_EditingMesh = mesh
            NGROUPS_PT_main.EditedObject = obj
            variables = mesh.NGroups
                
            if variables.HasData == False:
                row = layout.row()            
                row.operator('ngroups.create_ngroups', text = 'Create NGroups')
            else:
                box = layout.box()
                box.label(text = 'Base values', icon = 'CON_TRANSFORM')
                
                row = box.row()
                row.prop(variables, 'DefaultColor', text = 'Display color')
                
                row = box.row()
                row.prop(variables, 'GeneralOffsetAngle', text = 'General Angle')
               
                
                box = layout.box()
                box.label(text = 'Mesh operations', icon = 'MESH_DATA')
                
                row = box.row()
                row.operator('ngroups.remove_ngroups', text = 'Remove NGroups data (not applied data will be removed)')

                row = box.row()
                row.operator('ngroups.write_base_normals', text = 'Apply mesh normals (set normals to base layer)')
                
                box.separator()
                
                row = box.row()
                row.operator('ngroups.compute_mirrors', text = 'Compute mirrors (Use before mirroring group or after mesh editing)')
                
                box = layout.box()
                row = box.row()
                row.label(text = 'Data Update', icon = 'FILE_REFRESH')
                row = box.row(align = True)
                row.prop(variables, 'AutoUpdateGroups', text = 'Enable auto update')          
                row.prop(variables, 'UpdateNormalsWithCompute', text = 'Enable normals update in compute')
                row = box.row()
                row.operator('ngroups.set_mesh_normals', text = 'update mesh normals (Will be removed if not applied)')                
                row = box.row(align = True)
                row.operator('ngroups.compute_result_normals', text = 'Compute result')

                box = layout.box()
                box.label(text = 'Layers', icon = 'RENDERLAYERS')
                row = box.row()
                row.template_list('NGROUPS_UL_NormalGroups', '', variables, 'NormalGroups', variables, 'GroupIndex')
                
                col = row.column(align=True)
                col.operator('ngroups.normalgroup_add', text = '', icon='ADD')
                col.operator('ngroups.normalgroup_remove', text = '', icon='REMOVE')
                col.operator('ngroups.normalgroup_move', text = '', icon='TRIA_UP').direction = 'UP'
                col.operator('ngroups.normalgroup_move', text = '', icon='TRIA_DOWN').direction = 'DOWN'
                
                
                col.separator()
                if (len(variables.NormalGroups) > 0):
                    activeGroup = variables.NormalGroups[variables.GroupIndex]
                    isVector = variables.NormalGroups[variables.GroupIndex].IsVectorLayer
                    if isVector == False:
                        col.operator('ngroups.add_vector_data', text = '', icon = 'EVENT_V')
                    else:
                        col.operator('ngroups.remove_vector_data', text = '', icon = 'CANCEL')
                row = box.row()
                
                if (len(variables.NormalGroups) > 0):
                    
                    if isVector == False:
                        row.prop(activeGroup, 'Angle', text = 'Relative Angle (to General Angle)')

                    row = box.row()
                    row.prop(variables, 'Factor', slider = True)
            
                    row = box.row()
                    sub = row.row(align = True)
                    sub.operator('ngroups.assign_attribute_factor', text = 'Assign')
                    sub.operator('ngroups.remove_attribute_factor', text = 'Remove')
                    sub = row.row(align = True)
                    sub.operator('ngroups.select_groups', text = 'Select')
                    sub.operator('ngroups.deselect_groups', text = 'Deselect')
                    
                    box = layout.box()
                    box.label(text = 'Smooth', icon = 'MOD_SMOOTH')
                    row = box.row()
                    row.prop(variables, 'SmoothFactor', text = 'Smooth strength', slider = True)
                    row = box.row()
                    row.operator('ngroups.smooth_from_neighbour_vertices', text = 'Smooth selection')
                    
                    if Brushes.NGROUPS_OT_SmoothBrush.State == "STOP":
                        #row = box.row()
                        row.operator('ngroups.smooth_brush', text = 'Smooth brush')
                    else:
                        #row = box.row()
                        row.operator('ngroups.smooth_brush', text = 'Close smooth brush (for realtime update use layer display)', depress = Brushes.NGROUPS_OT_SmoothBrush.State != "STOP")
                        Brushes.NGROUPS_OT_SmoothBrush.Stop = True
                        
                if (len(variables.NormalGroups) > 0): 
                    if isVector:
                        box = layout.box()
                        box.label(text = 'Vector data', icon = 'EMPTY_ARROWS')

                        if len(activeGroup.VectorGroups) > 0:
                            row = box.row()
                            sub = row.row(align = True)
                            sub.operator('ngroups.assign_to_vector', text = 'Assign')
                            sub.operator('ngroups.remove_from_factor', text = 'Remove')
                            sub = row.row(align = True)
                            sub.operator('ngroups.select_vector', text = 'Select')
                            sub.operator('ngroups.deselect_vector', text = 'Deselect')
                            activeVector = activeGroup.VectorGroups[activeGroup.VectorIndex]
                            if (activeVector.Type != ''):
                                row = box.row()
                                row.operator('ngroups.edit_vector', text = 'Edit selected vector data')
                            row = box.row(align = True)
                            row = box.row()
                            row.prop(variables, 'Shape')
                            row.operator('ngroups.set_vector_shape', text = 'Set vector shape')
                        
                        row = box.row()
                        row.template_list('NGROUPS_UL_VectorGroups', '', activeGroup, 'VectorGroups', activeGroup, 'VectorIndex')
                        col = row.column(align=True)
                        col.operator('ngroups.vector_group_add', text = '', icon='ADD')
                        col.operator('ngroups.vector_group_remove', text = '', icon='REMOVE')
                        col.operator('ngroups.vector_group_move', text = '', icon='TRIA_UP').direction = 'UP'
                        col.operator('ngroups.vector_group_move', text = '', icon='TRIA_DOWN').direction = 'DOWN'
                box = layout.box()
                row = box.row()
                row.label(text = "Layers visualization", icon = 'IMAGE_PLANE')
                row = box.row()
                row.operator('ngroups.toggle_checker_material', text = 'Toggle Layers display', depress = variables.HasCheckerMaterial)
                if variables.HasCheckerMaterial:
                    if (len(variables.NormalGroups) > 0):
                        row = box.row()
                        row.operator('ngroups.set_material_from_layer', text = 'Show current layer (Mirror is not displayed)').layer = 'FROM_ACTIVE_GROUP'
                    
                    row = box.row()
                    row.operator('ngroups.set_material_from_layer', text = 'Show all layers').layer = 'COLOR'    
                
                        
                
        elif NGROUPS_PT_main.EditedObject != None and NGROUPS_PT_main.EditedObject.data.NGroups.HoldObject:

            obj = NGROUPS_PT_main.EditedObject
            mesh = obj.data
            variables = mesh.NGroups
            row = layout.row()
            row.prop(variables, 'NormalDistance')
            row = layout.row()
            row.operator('ngroups.flip_normals', text = 'Flip normals')
            row = layout.row()
            row.operator('ngroups.apply_vector', text = 'Apply')
            row.operator('ngroups.cancel_vector', text = 'Cancel')
                
            
            
            
                

                
                
    
classes = [
    NGROUPS_UL_VectorGroups,
    NGROUPS_PT_main,
    NGROUPS_UL_NormalGroups
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)