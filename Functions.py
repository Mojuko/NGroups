from . import MaterialFunctions, Data, VectorFunctions

import bpy, bmesh
import math, mathutils
from mathutils import Vector
from mathutils import Euler
import decimal
from decimal import *
def ui_item_remove(variable, index):
    if 0 <= index < len(variable):
        variable.remove(index)

    if index > 0:
        index -= 1

    return index

def ui_item_move(variable, index, direction):
    if direction == 'UP':
        new_index = (index - 1) % len(variable)
        variable.move(index, new_index)

    elif direction == 'DOWN':
        new_index = (index + 1) % len(variable)
        variable.move(index, new_index)

    else: return index

    return new_index

def AddAttributeToMesh(mesh, attributeData):
    attribute = mesh.attributes.get(attributeData[0])
    if attribute == None:
        attribute = mesh.attributes.new(attributeData[0], attributeData[1], attributeData[2])
    return attribute

def RemoveAttributeByName(mesh, attributeName):
    attribute = mesh.attributes.get(attributeName)
    if attribute != None:
        mesh.attributes.remove(attribute)

def GetAttributeByIndex(mesh, index):
    name = Data.GroupAttributes[0] + f"{index}"
    attribute = mesh.attributes.get(name)
    return attribute

def RemoveAttributeByIndex(mesh, index):
    attribute = GetAttributeByIndex(mesh, index)
    if attribute != None:
        mesh.attributes.remove(attribute)

def AddAttributesFromList(mesh, attributeList):
    for attribute in attributeList:
        AddAttributeToMesh(mesh, attribute)

def RemoveAttributesFromList(mesh, attributeList):
    for attribute in attributeList:
        RemoveAttributeByName(mesh, attribute[0])

def AddData(mesh):
    variables = mesh.NGroups
    variables.HasData = True 
    
    AddAttributesFromList(mesh, Data.AttributesArray)
    
    SetBaseColor(mesh)
    SetDefaultNormalToAttribute_MODETOGGLE(mesh)

def RemoveData(mesh):
    
    variables = mesh.NGroups
    
    SetMeshNormalsFromAttribute_MODETOGGLE(mesh, Data.BaseNormalsAttribute[0])
    
    for i in range(0, variables.UniqueIndex + 1, 1):
        RemoveAttributeByIndex(mesh, i)
        VectorFunctions.RemoveVectorAttributeByIndex(mesh, i)

    bpy.props.EditingMesh = None
    MaterialFunctions.RemoveChekcerMaterial(mesh)
       
    variables.NormalGroups.clear()
    variables.HasData = False
    variables.UniqueIndex = 0                
    variables.GroupIndex = 0
    variables.AutoUpdateGroups = True
    variables.UpdateNormalsWithCompute = True
    variables.Factor = 1
    variables.DefaultColor = [0,0,0]
    variables.OriginalMaterials = ''
    variables.HasCheckerMaterial = False
    variables.VectorFactor = 1
    variables.HoldObject = False

    RemoveAttributesFromList(mesh, Data.AttributesArray)
    

def AddGroup(mesh):
    variables = mesh.NGroups
    newGroup = variables.NormalGroups.add()
    variables.GroupIndex = len(variables.NormalGroups) - 1
    variables.UniqueIndex = variables.UniqueIndex + 1
    
    newGroup.name = f'New group.{variables.UniqueIndex:03}'
    newGroup.Index = variables.UniqueIndex
    
    attributeData = []
    attributeData.append(Data.GroupAttributes[0] + f"{variables.UniqueIndex}")
    attributeData.append(Data.GroupAttributes[1])
    attributeData.append(Data.GroupAttributes[2])

    attribute = AddAttributeToMesh(mesh, attributeData)
    

def RemoveSelectedGroup(mesh):
    variables = mesh.NGroups
    activeGroup = variables.NormalGroups[variables.GroupIndex]
    if len(variables.NormalGroups) > 0:
        if activeGroup.IsVectorLayer:
            VectorFunctions.RemoveSelectedGroupVectorData(mesh)
        RemoveAttributeByIndex(mesh, activeGroup.Index)
        variables.GroupIndex = ui_item_remove(variables.NormalGroups, variables.GroupIndex)
        
def GetBmeshLoopFloatLayerFromIndex(bm, index):
    name = Data.GroupAttributes[0] + f"{index}"
    layer = bm.loops.layers.float.get(name)
    return layer

def GetBmeshLoopColorLayer(bm, name):
    layer = bm.loops.layers.color.get(name)
    return layer

def GetBmeshLoopVectorLayer(bm, name):
    layer = bm.loops.layers.float_vector.get(name)
    return layer

def GetSelectedLoops(bm):
    selectionMode = bpy.context.tool_settings.mesh_select_mode[:]
    loops = []
    if (selectionMode[2] == True):
        faces = [face for face in bm.faces if face.select]
        for face in faces:
            loops.extend(face.loops)
        
    if (selectionMode[0] == True or selectionMode[1] == True):
        vertices = [vert for vert in bm.verts if vert.select]
        for vert in vertices:
            loops.extend(vert.link_loops)
    
    return loops

NumbersLength = Decimal(10) ** -4

def FloatToDecimal(floatValue):
    return Decimal(f'{floatValue:.5f}').quantize(Decimal(str(NumbersLength)), decimal.ROUND_DOWN)

def FloatTuple3ToDecimal(floatTuple):
    return (FloatToDecimal(floatTuple[0]), FloatToDecimal(floatTuple[1]), FloatToDecimal(floatTuple[2]))

def MulD(a, b, accuracy):
    return (a * b).quantize(accuracy)

def DivD(a, b, accuracy):
    return (a / b).quantize(accuracy)

def DivDTuple3ByDecimal(tuple, decimal, accuracy):
    return (DivD(tuple[0], decimal, accuracy), DivD(tuple[1], decimal, accuracy), DivD(tuple[2], decimal, accuracy))

def SumDTuple3(tuple1, tuple2):
    return (tuple1[0] + tuple2[0],tuple1[1] + tuple2[1], tuple1[2] + tuple2[2])

def ComputeMirrors(mesh):
    variables = mesh.NGroups
    bm = bmesh.from_edit_mesh(mesh)
    
    mirrorLayerX = bm.loops.layers.int.get(Data.MirrorAttributeX[0])
    mirrorLayerY = bm.loops.layers.int.get(Data.MirrorAttributeY[0])
    
    facePairsX, noMirrorFacesX = GetMirroredFacePairs(bm, 'X')
    LoopsXPairs, noMirrorLoopsX = GetMirroredLoopPairsFromFacePairs(bm, facePairsX, 'X')
    for face in noMirrorFacesX:
        for loop in face.loops:
            noMirrorLoopsX.add(loop)
    
    for loop, mirrorLoop in LoopsXPairs:
        loop[mirrorLayerX] = mirrorLoop.index
        mirrorLoop[mirrorLayerX] = loop.index
    for loop in noMirrorLoopsX:
        loop[mirrorLayerX] = loop.index
    
    facePairsY, noMirrorFacesY = GetMirroredFacePairs(bm, 'Y')
    LoopsYPairs, noMirrorLoopsY = GetMirroredLoopPairsFromFacePairs(bm, facePairsY, 'Y')
    for face in noMirrorFacesY:
        for loop in face.loops:
            noMirrorLoopsY.add(loop)

    for loop, mirrorLoop in LoopsYPairs:
        loop[mirrorLayerY] = mirrorLoop.index
        mirrorLoop[mirrorLayerY] = loop.index
    for loop in noMirrorLoopsY:
        loop[mirrorLayerY] = loop.index
    bmesh.update_edit_mesh(mesh)
    bm.free()

def GetMirroredFacePairs(bm, axis):
    faces = bm.faces
    facePositions = []

    zeroTuple = FloatTuple3ToDecimal((0,0,0))

    for face in faces:
        faceCentralPosition = zeroTuple
                
        positions = [vert.co for vert in face.verts]
        for pos in positions:
            pos = FloatTuple3ToDecimal(pos.to_tuple())
            faceCentralPosition = SumDTuple3(faceCentralPosition, pos)
        faceCentralPosition = DivDTuple3ByDecimal(faceCentralPosition, FloatToDecimal(len(face.verts)), NumbersLength)
        facePositions.append(faceCentralPosition)

    faceDictionary = {}
    faceMirrorPairs = set()
    noMirrorFaces = set()
    for i,face in enumerate(bm.faces):
        posTuple = facePositions[i]
        faceDictionary[posTuple] = face
        
    while len(faceDictionary.keys()) > 0:
        pos, face = faceDictionary.popitem()
        
        mirrorPos = None
        
        if axis == 'X':
            mirrorPos = (-pos[0], pos[1], pos[2])
        elif axis == 'Y':
            mirrorPos = (pos[0], -pos[1], pos[2])

        mirrorFace = faceDictionary.get(mirrorPos)
        if mirrorFace != None:
            faceMirrorPairs.add((face, mirrorFace))
            del faceDictionary[mirrorPos]
        elif pos[0] == FloatToDecimal(0.0) and axis == 'X':
            faceMirrorPairs.add((face, face))
        elif pos[1] == FloatToDecimal(0.0) and axis == 'Y':
            faceMirrorPairs.add((face, face))
        else:
            noMirrorFaces.add(face)
             
    return faceMirrorPairs , noMirrorFaces

def GetMirroredLoopPairsFromFacePairs(bm, facePairs, axis):
    loopMirrorPairs = set()
    noMirroredLoops = set()

    for face, mirrorFace in facePairs:
        loops = []
        loopDictionary = {}
        
        loops.extend(face.loops)
        if face != mirrorFace:
            loops.extend(mirrorFace.loops)
        
        for loop in loops:
            loopPos = FloatTuple3ToDecimal(loop.vert.co.to_tuple())
            copy = loopDictionary.get(loopPos)
            if copy !=  None:
                loopDictionary.pop(loopPos, None)
                loopMirrorPairs.add((loop, copy))
            else:
                loopDictionary[loopPos] = loop
        
        
        while len(loopDictionary.keys()) > 0:
            pos, loop = loopDictionary.popitem()
            mirrorPos = None
        
            if axis == 'X':
                mirrorPos = (-pos[0], pos[1], pos[2])
            elif axis == 'Y':
                mirrorPos = (pos[0], -pos[1], pos[2])
                
            mirrorLoop = loopDictionary.get(mirrorPos)
            if mirrorLoop != None:
                loopMirrorPairs.add((loop, mirrorLoop))
                del loopDictionary[mirrorPos]
            else:
                noMirroredLoops.add(loop)
                            
    return loopMirrorPairs, noMirroredLoops
         

def GetLoopsByGroup(bm, layer, factor):
    temp = []
    for face in bm.faces:
        temp.extend(face.loops)
    loops = [loop for loop in temp if loop[layer] > factor]
    return loops


def SetSelectedGroupFactor(mesh, factor):
    variables = mesh.NGroups
    group = variables.NormalGroups[variables.GroupIndex]
    index = group.Index
    
    bm = bmesh.from_edit_mesh(mesh)
    
    groupLayer = GetBmeshLoopFloatLayerFromIndex(bm, index)
    selectedLoops = GetSelectedLoops(bm)
    
    for loop in selectedLoops:
        loop[groupLayer] = factor

    bmesh.update_edit_mesh(mesh)
    bm.free()

def GetAllLoops(bm):
    loops = []
    for face in bm.faces:
        loops.extend(face.loops)
    return loops

def LoopsFromAttribute(mesh, select):
    selectionMode = bpy.context.tool_settings.mesh_select_mode[:]
    variables = mesh.NGroups
    group = variables.NormalGroups[variables.GroupIndex]
    index = group.Index
    
    bm = bmesh.from_edit_mesh(mesh)
    
    groupLayer = GetBmeshLoopFloatLayerFromIndex(bm, index)
    
    loops = GetLoopsByGroup(bm, groupLayer , 0)

    if (selectionMode[2] == True):
        for loop in loops:
            loop.face.select = select
    
    if (selectionMode[0] == True or selectionMode[1] == True):
        for loop in loops:
            loop.vert.select = select
    
    bmesh.update_edit_mesh(mesh)
    bm.free()

def GetAllNormals(mesh):
    version = bpy.app.version_string
    versionNumbers = version.split('.')
    if int(versionNumbers[0] + versionNumbers[1]) < 41:
        mesh.calc_normals_split()
    normals = [loop.normal for loop in mesh.loops]
    return normals

def SetDefaultNormalToAttribute_MODETOGGLE(mesh):
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    normals = GetAllNormals(mesh)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    bm = bmesh.from_edit_mesh(mesh)
    baseNormalsLayer = GetBmeshLoopVectorLayer(bm, Data.BaseNormalsAttribute[0])
    
    loops = GetAllLoops(bm)
    
    for i, loop in enumerate(loops):
        loop[baseNormalsLayer] = normals[i]

    bmesh.update_edit_mesh(mesh)
    bm.free()
    
    
def SetBaseColor(mesh):
    variables = mesh.NGroups
    bm = bmesh.from_edit_mesh(mesh)

    colorLayer = GetBmeshLoopColorLayer(bm, Data.ColorAttrbitue[0])
    loops = GetAllLoops(bm)

    defaultColor = Color3ToColor4(variables.DefaultColor)  

    for loop in loops:
        loop[colorLayer] = defaultColor

    bmesh.update_edit_mesh(mesh)
    bm.free()

def LerpList(a, b, factor):
    result = [ai * (1 - factor) + b[i] * factor for i, ai in enumerate(a)]
    return result

def Color3ToColor4(color3):
    return [color3.r, color3.g, color3.b, 1]

def GetBmeshNormalGroupsLayers(bm, variables):
    groupLayers = []
    groups = variables.NormalGroups
    for group in groups:
        groupLayers.append(GetBmeshLoopFloatLayerFromIndex(bm, group.Index))
    return groupLayers

def GetColors(mesh):
    colors = []
    variables = mesh.NGroups
    groups = variables.NormalGroups
    for group in groups:
        colors.append(Color3ToColor4(group.Color))
    return colors

def GetAngles(mesh):
    angles = []
    variables = mesh.NGroups
    groups = variables.NormalGroups
    for group in groups:
        angles.append(group.Angle)
    return angles

def GetVisibility(mesh):
    visible = []
    variables = mesh.NGroups
    groups = variables.NormalGroups
    for group in groups:
        visible.append(group.Visible)
    return visible

def GetMirrors(mesh):
    mirrorX = []
    mirrorY = []
    variables = mesh.NGroups
    groups = variables.NormalGroups
    for group in groups:
        mirrorX.append(group.XMirror)
        mirrorY.append(group.YMirror)
        
    return mirrorX, mirrorY

def GetIsVector(mesh):
    isVector = []
    variables = mesh.NGroups
    groups = variables.NormalGroups
    for group in groups:
        isVector.append(group.IsVectorLayer)
    return isVector
def GetBmeshVectorLayers(bm, variables):
    vectorLayers = []
    groups = variables.NormalGroups
    for group in groups:
        vectorLayers.append(VectorFunctions.GetBmeshLoopIntVectorLayerFromIndex(bm, group.Index))
    return vectorLayers

def ComputeResult(mesh):
    try:
        variables = mesh.NGroups
        obj = bpy.context.active_object
        objMatrix = obj.matrix_world
        bm = bmesh.from_edit_mesh(mesh)
    
        groups = variables.NormalGroups

        loops = GetAllLoops(bm)
    
        colorLayer = GetBmeshLoopColorLayer(bm, Data.ColorAttrbitue[0])
        baseNormalsLayer = GetBmeshLoopVectorLayer(bm, Data.BaseNormalsAttribute[0])
        resultNormalsLayer = GetBmeshLoopVectorLayer(bm, Data.ResultNormalsAttribute[0])
        mirrorLayerX = bm.loops.layers.int.get(Data.MirrorAttributeX[0])
        mirrorLayerY = bm.loops.layers.int.get(Data.MirrorAttributeY[0])    
        groupLayers = GetBmeshNormalGroupsLayers(bm, variables)
        vectorLayers = GetBmeshVectorLayers(bm, variables)
        colors = GetColors(mesh)
        angles = GetAngles(mesh)
        visibility = GetVisibility(mesh)
        mirrorX, mirrorY = GetMirrors(mesh)
        isVector = GetIsVector(mesh)

        defaultColor = Color3ToColor4(variables.DefaultColor)
    
        for loop in loops:
            resultColor = defaultColor
            resultNormal = loop[baseNormalsLayer].copy()

            emptyLoop = True

            for i, groupLayer in enumerate(groupLayers):
                if visibility[i] != True:
                    continue
            
                factor = loop[groupLayer]
                normal = resultNormal
            
                reflectX = False
                reflectY = False
                targetLoop = loop
                hasData = False
                angle = angles[i] + variables.GeneralOffsetAngle
                if mirrorX[i]:
                    otherFactor = loops[loop[mirrorLayerX]][groupLayer]
                    if otherFactor > factor:
                        reflectX = True
                        targetLoop = loops[loop[mirrorLayerX]]
                        factor = otherFactor
                elif mirrorY[i]:
                    otherFactor = loops[loop[mirrorLayerY]][groupLayer]
                    if otherFactor > factor:
                        reflectY = True
                        targetLoop = loops[loop[mirrorLayerY]]
                        factor = otherFactor
            
                if factor == 0:
                    continue
                else:
                    emptyLoop = False
            
                if isVector[i] == False:
                    hasData = True
                    normal = Vector((math.sin(angle), -math.cos(angle), 0))
                else:
                    group = groups[i]
                    for vectorGroup in group.VectorGroups:
                        index = vectorGroup.Index
                        if index == targetLoop[vectorLayers[i]]:
                            if vectorGroup.Type == "SPHERE" and vectorGroup.Value != '':
                                hasData = True
                                pos = vectorGroup.Value.split(';')[0].split(',')
                                pos = Vector((float(pos[0]),float(pos[1]),float(pos[2])))
                                flip = bool(int(vectorGroup.Value.split(';')[1]))
                                mulFactor = 1
                                if flip:
                                    mulFactor = -1
                                startPoint = objMatrix @ targetLoop.vert.co
                                normal = -(pos - startPoint).normalized() * mulFactor
                            
                            if  vectorGroup.Type == "PLANE" and vectorGroup.Value != '':
                                hasData = True
                                eulerRot = vectorGroup.Value.split(';')[0].split(',')
                                rotation = Euler((float(eulerRot[0]),float(eulerRot[1]),float(eulerRot[2])))
                                flip = bool(int(vectorGroup.Value.split(';')[1]))
                                mulFactor = 1
                                if flip:
                                    mulFactor = -1
                                vec = Vector((0,0,1))
                                normal = rotation.to_matrix() @ vec * mulFactor
                if hasData:
                    if reflectX:
                        normal = normal.reflect(Vector((1,0,0)))
                    elif reflectY:
                        normal = normal.reflect(Vector((0,1,0)))

                resultNormal = resultNormal.slerp(normal, factor, normal)
                color = colors[i]
                resultColor = LerpList(resultColor, color, factor)
            
            if (emptyLoop):
                resultNormal = (0,0,0)
            loop[colorLayer] = resultColor

            loop[resultNormalsLayer] = resultNormal
    
        bmesh.update_edit_mesh(mesh)
        bm.free()
    
        if variables.UpdateNormalsWithCompute:
            SetMeshNormals_MODETOGGLE(mesh)
    except:
        return 'ERROR'

def SetMeshNormals_MODETOGGLE(mesh):
    SetMeshNormalsFromAttribute_MODETOGGLE(mesh, Data.ResultNormalsAttribute[0])

def SetMeshNormalsFromAttribute_MODETOGGLE(mesh, attributeName):

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    currentNormals = GetAllNormals(mesh)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    bm = bmesh.from_edit_mesh(mesh)
    layer = GetBmeshLoopVectorLayer(bm, attributeName)
    loops = GetAllLoops(bm)
    normals = []
    for i, loop in enumerate(loops):
        if (loop[layer].length <= 0.0):
            normals.append(currentNormals[i].to_tuple())
        else:
            normals.append(loop[layer])
    
    bmesh.update_edit_mesh(mesh)
    bm.free()

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    version = bpy.app.version_string
    versionNumbers = version.split('.')
    if int(versionNumbers[0] + versionNumbers[1]) < 41:
        mesh.use_auto_smooth = True
    mesh.normals_split_custom_set(normals)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
def GetActiveLayer(bm):
    mesh = bpy.props.NGroups_EditingMesh
    variables = mesh.NGroups
    group = variables.NormalGroups[variables.GroupIndex]
    index = group.Index
    return GetBmeshLoopFloatLayerFromIndex(bm, index)
    
def SmoothFromNeighbourVerticesFromMesh(mesh):
    
    bm = bmesh.from_edit_mesh(mesh)    

    groupLayer = GetActiveLayer(bm)
    
    selectedVertices = [vert for vert in bm.verts if vert.select]
    SmoothFromNeighbourVertices(bm, selectedVertices, groupLayer)

    bmesh.update_edit_mesh(mesh)
    bm.free()
    
def SmoothFromNeighbourVertices(bm, selection, groupLayer):
    newFactors = []
    for baseVert in selection:
        
        edges = [edge for edge in baseVert.link_edges]
        verts = set()
        for edge in edges:
            for vert in edge.verts:
                verts.add(vert)
        baseFactor = 0
        loopCounter = 0        
        for loop in vert.link_loops:
                loopCounter = loopCounter + 1
                baseFactor = baseFactor + loop[groupLayer]
        baseFactor = baseFactor / loopCounter

        factor = 0
        loopCounter = 0
        for vert in verts:
            for loop in vert.link_loops:
                loopCounter = loopCounter + 1
                factor = factor + loop[groupLayer]
        factor = factor / loopCounter
        
        mesh = bpy.props.NGroups_EditingMesh
        variables = mesh.NGroups
        smoothFactor = variables.SmoothFactor
        factor = (factor * smoothFactor + (1 - smoothFactor) * baseFactor)

        if factor < 0.009:
            factor = 0
        elif factor > 0.991:
            factor = 1
        
        newFactors.append((baseVert, factor))
        
    for vert, factor in newFactors:
        for loop in vert.link_loops:
            loop[groupLayer] = factor