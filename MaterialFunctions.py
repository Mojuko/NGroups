from . import Data

import bpy

def SetCheckerMaterial(mesh):
	variables = mesh.NGroups
	checkerMaterial = bpy.data.materials.get(Data.CheckerMaterialName)
	if checkerMaterial == None:
		checkerMaterial = bpy.data.materials.new(Data.CheckerMaterialName)
		
	checkerMaterial.use_nodes = True
	nodeTree = checkerMaterial.node_tree

	links = nodeTree.links
	nodes = nodeTree.nodes

	links.clear()
	nodes.clear()
	
	attributeNodeName = 'ShaderNodeAttribute'
	outputNodeName = 'ShaderNodeOutputMaterial'
	combineName = 'ShaderNodeCombineXYZ'
	separateName = 'ShaderNodeSeparateXYZ'
	mathName = 'ShaderNodeMath'
	
	attribute = nodes.new(attributeNodeName)
	output = nodes.new(outputNodeName)

	colorOutput = attribute.outputs['Color']
	surfaceInput = output.inputs['Surface']
	
	if True:
		combine = nodes.new(combineName)
		separate = nodes.new(separateName)
		mathX = nodes.new(mathName)
		mathY = nodes.new(mathName)
		mathZ = nodes.new(mathName)
		mathX.operation = 'SQRT'
		mathY.operation = 'SQRT'
		mathZ.operation = 'SQRT'

		
	
		links.new(colorOutput, separate.inputs['Vector'])
		links.new(surfaceInput, combine.outputs['Vector'])
	
		links.new(separate.outputs['X'], mathX.inputs['Value'])
		links.new(separate.outputs['Y'], mathY.inputs['Value'])
		links.new(separate.outputs['Z'], mathZ.inputs['Value'])
	
		links.new(combine.inputs['X'], mathX.outputs['Value'])
		links.new(combine.inputs['Y'], mathY.outputs['Value'])
		links.new(combine.inputs['Z'], mathZ.outputs['Value'])
	else:
		link = links.new(colorOutput, surfaceInput)
	
	attribute.attribute_name = Data.ColorAttrbitue[0]
	if len(mesh.materials) > 0:
		names = []
		for material in mesh.materials:
			if material != None:
				names.append(material.name)
				material.use_fake_user = True
			else:
				names.append('')
		variables.OriginalMaterials = ''
		for name in names:
			variables.OriginalMaterials = variables.OriginalMaterials + name + ','

		for i,material in enumerate(mesh.materials):
			mesh.materials[i] = checkerMaterial
	else:
		mesh.materials.append(checkerMaterial)

def RemoveChekcerMaterial(mesh):
	variables = mesh.NGroups
	names = variables.OriginalMaterials.split(',')
	for i,material in enumerate(mesh.materials):
		if i < len(names):
			mesh.materials[i] = bpy.data.materials.get(names[i])
		
	checkerMaterial = bpy.data.materials.get(Data.CheckerMaterialName)
	if checkerMaterial != None:
		checkerMaterial = bpy.data.materials.remove(checkerMaterial)
	variables.OriginalMaterials = ''

def SetMaterialAttributeValue(mesh, name):
	variables = mesh.NGroups
	
	checkerMaterial = bpy.data.materials.get(Data.CheckerMaterialName)
	attributeNode = checkerMaterial.node_tree.nodes.get('Attribute')
	if attributeNode == None:
		return
	if name == "COLOR":
		attributeNode.attribute_name = Data.ColorAttrbitue[0]
	elif name == "FROM_ACTIVE_GROUP":
		groupIndex = variables.NormalGroups[variables.GroupIndex].Index
		attributeNode.attribute_name = Data.GroupAttributes[0] + str(groupIndex)
