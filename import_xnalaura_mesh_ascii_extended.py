bl_info = {
	"name": "Import XNALara Extended Mesh (.ascii)",
	"author": "FigureSculptor",
	"version": (2, 0),
	"blender": (2, 5, 7),
	"api": 36079,
	"location": "File > Import > Import XNALara Extended Mesh (.ascii)",
	"description": "Import XNALara Extended Mesh",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Import-Export"}

"""
Version': '1.0' 

The parsing logic is adapted from loginc in ImportMeshAsciiExtended.py for Blender 2.48 by Dusan Pavlicek

"""

import bpy
import mathutils
import os
import sys
import string
import math
import re
from bpy import *
from string import *
from struct import *
from math import *
from bpy.props import *
from mathutils import *

warningCounter = 0
rootDir = ''
logf = None
armature = None
armature_object = None
meshes = []
mesh_objects = []
unused_bones = []


def importMesh(file, boneCount):
	global armature
	global armature_object
	global meshes
	global mesh_objects
	global unused_bones
	
	meshFullName = meshName = ReadLine(file)
	print("meshFullName: " + meshFullName )

	
	me_ob = bpy.data.meshes.new(meshFullName)
	obmesh = bpy.data.objects.new(me_ob.name,me_ob)
	print(("New Mesh = " + me_ob.name ))
	meshes.append(me_ob)
	mesh_objects.append(obmesh)
	
	me_ob.update()
	
	# storeName(meshName, meshFullName)
	# mesh.vertexColors = 1
	
	uvLayerCount = int(ReadLineIgnoreComments(file))
	print("UV Layer Count: " + str(uvLayerCount))
	
	for i in range(0, uvLayerCount):
		me_ob.tessface_uv_textures.new(name="UV" + str(i+1))

	matdata = bpy.data.materials.new(meshName)
	textureCount = int(ReadLineIgnoreComments(file))
	print("Texture Count: " + str(textureCount))
	faceImage = None
	
	# TODO: Textures
	
	textureFilenames = []
	
	for textureID in range(0, textureCount):
		textureFilename = ReadLine(file)
		
		if (textureFilename.lower().startswith("c:") or textureFilename.lower().startswith("d:")):
			parts = textureFilename.split("\\")
			textureFilename = parts.pop()
		
		textureFilename = os.path.join(rootDir, os.path.basename(textureFilename))
		print("textureFilename: " + textureFilename)
		uvLayerID = int(ReadLineIgnoreComments(file))
		
		textureName = meshName + '_' + str(textureID + 1)
		textureFilenames.append(textureFilename)

	nbVrtx = 1
	vrtxList = [[0,0,0]]
	
	vertexCount = int(ReadLineIgnoreComments(file))
	coords = [[0, 0, 0]]
	normals = [[0, 0, 0]]
	colors = [[0, 0, 0, 0]]
	uvs = [[0, 0]]
	for vertexID in range(0, vertexCount):
		tuple = ReadTuple(file)
		x = float(tuple[0])
		y = float(tuple[1])
		z = float(tuple[2])
		coords.append([x, -z, y])
		
		tuple = ReadTuple(file)
		nx = float(tuple[0])
		ny = float(tuple[1])
		nz = float(tuple[2])
		normals.append([nx, -nz, ny])
		
		tuple = ReadTuple(file)
		# r = int(tuple[0])
		# g = int(tuple[1])
		# b = int(tuple[2])
		# a = int(tuple[3])
		# colors.append([r, g, b, a])
		
		uvList = []
		for i in range(0, uvLayerCount):
			tuple = ReadTuple(file)
			u = float(tuple[0])
			v = float(tuple[1])
			uvList.append([u, 1 - v])
		uvs.append(uvList)

		if (boneCount != None):
			if (boneCount > 0):
				indices = ReadTuple(file) # boneIndices
				weights = ReadTuple(file) # boneWeights
			
				for id in range(0, len(indices) ):
					groupID = int(indices[id])
					#print("groupID: " + str(groupID))
					weight = float(weights[id])
					if (groupID > 0) and weight > 0:
						nameGroup = bonesNameList[int(groupID)]
						vrtxList.append([nameGroup, weight, int(vertexID+1)])
						nbVrtx = nbVrtx + 1
	

	faceCount = int(ReadLineIgnoreComments(file))
	# print faceCount

	indices = []

	for i in range(0, faceCount):
		tuple = ReadTuple(file)
		index1 = int(tuple[0])
		index2 = int(tuple[1])
		index3 = int(tuple[2])
		if (faceCount == 1):
			indices.append([1, 2, 3])
		else:
			indices.append([index1 + 1, index3 + 1, index2 + 1])

	# mesh.faces.extend(indices, ignoreDups=True)

	faces = []
	# face_uvs = []
	# 
	# # Monkey 13
	faceDiffs = 0
	for faceID in range(0, faceCount):
	 # print faceID
	 try:
		 #face = mesh.faces[faceID]
		 #face.image = faceImage
		 index1 = indices[faceID][0]
		 index2 = indices[faceID][1]
		 index3 = indices[faceID][2]
		 # color1 = colors[index1]
		 # color2 = colors[index2]
		 # color3 = colors[index3]
		 # face.col[0].r = color1[0]
		 # face.col[0].g = color1[1]
		 # face.col[0].b = color1[2]
		 # face.col[0].a = color1[3]
		 # face.col[1].r = color2[0]
		 # face.col[1].g = color2[1]
		 # face.col[1].b = color2[2]
		 # face.col[1].a = color2[3]
		 # face.col[2].r = color3[0]
		 # face.col[2].g = color3[1]
		 # face.col[2].b = color3[2]
		 # face.col[2].a = color3[3]
		 # face.smooth = True
	 
		 faces.extend([index1, index2, index3, 0])
	 
	 
	 except:
		 print (str(faceID))
		 faceDiffs += 1
	 
	 faceCount -= faceDiffs
	
	me_ob.vertices.add(len(coords))
	me_ob.tessfaces.add(len(faces)//4)
	me_ob.vertices.foreach_set("co", unpack_list(coords))
	me_ob.tessfaces.foreach_set("vertices_raw", faces)
	me_ob.tessfaces.foreach_set("use_smooth", [True] * len(me_ob.tessfaces))
	me_ob.update_tag()
	
 
	
	for uvLayerID in range(0, uvLayerCount):
		uvtex = me_ob.tessface_uv_textures[uvLayerID]
		if (uvLayerID == 0):
			uvtex.active = True;
		for faceID in range(0, faceCount):
			face = me_ob.tessfaces[faceID]
			index1 = indices[faceID][0]
			index2 = indices[faceID][1]
			index3 = indices[faceID][2]
			#print ("indices: " + str(index1) + " / " + str(index2) + " / " + str(index3))
			blender_tface = uvtex.data[faceID]
			uv1 = Vector(uvs[index1][uvLayerID])
			uv2 = Vector(uvs[index2][uvLayerID])
			uv3 = Vector(uvs[index3][uvLayerID])
			#print ("uvs: " + str(uv1) + " / " + str(uv2) + " / " + str(uv3))
			# blender_tface.uv = [uv1, uv2, uv3]
			blender_tface.uv1 = uv1
			blender_tface.uv2 = uv2
			blender_tface.uv3 = uv3
			
 
			
	matdata = bpy.data.materials.new("Material")
	me_ob.materials.append(matdata)
	matdata.specular_intensity = 0.0
	matdata.alpha = 0.0
	matdata.use_transparency = True
	matdata.use_transparent_shadows = True
	matdata.use_face_texture = True
	texCounter = 0
	for textureFilename in textureFilenames:
		print("textureFilename: " + textureFilename)
		try:		
			textureBasename = os.path.basename(textureFilename)
			print("textureBasename " + textureBasename)
			print("len: " + str(len(textureBasename))) 
			textureObjName = None
			
			name_parts = textureBasename.split(".")
			textureNameNoExtension = name_parts[0]
	
			if (len(textureNameNoExtension) <= 21):
				textureObjName = textureNameNoExtension
			else:
				textureObjName = textureNameNoExtension[len(textureNameNoExtension)-22:len(textureNameNoExtension)]
			
			if (textureObjName.find(".") != -1):
				parts = textureObjName.split(".")
				textureObjName = parts[0]
				


			print("textureObjName: " + textureObjName)

			bpy.ops.image.open(filepath=textureFilename)

		
			image = None

			# find the image we just loaded
			for one_image in bpy.data.images:
				if (one_image.filepath == textureFilename):
					image = one_image

			image.name = textureObjName
			image.use_premultiply = True
			# print("image: " + str(image))
			imgTex = bpy.data.textures.new(textureFilename,type='IMAGE')
			imgTex.name = textureObjName
			imgTex.image = image
			mtex = matdata.texture_slots.add()
			mtex.texture_coords = "UV"
			mtex.texture = imgTex
			mtex.use_map_alpha = True
			mtex.alpha_factor = 1.0
			mtex.uv_layer = "UV1" #make work with multiple UVs
			if (texCounter == 0):
				mtex.use = True
				# faces = me_ob.faces
				# print ("face: " + str(faces))
				# faces.foreach_set("image", image)
				# textureFace.image = image
				# textureFace.use_image = True
			else:
				print("mtex.name: " + mtex.name)
				if (mtex.name.lower().endswith("_n") or mtex.name.lower().find("_n.") != -1 or mtex.name.lower().endswith("_nm") or mtex.name.lower().find("_nm.") != -1 or mtex.name.lower().endswith("_norm") or mtex.name.lower().find("_norm.") != -1 or mtex.name.lower().find("bump") != -1):
					# we done have ourselves a normal map
					print("normal map")
					mtex.use = True
					mtex.use_map_color_diffuse = False
					mtex.normal_factor = 1.0
					mtex.normal_map_space = 'TANGENT'
					mtex.use_map_normal = True
					mtex.use_map_alpha = False
					imgTex.use_normal_map = True
				elif (mtex.name.lower().endswith("_s") or mtex.name.lower().find("_s.") != -1 or mtex.name.lower().endswith("_spec") or mtex.name.lower().find("_spec.") != -1):
					print("specular map")
					mtex.use = True
					mtex.use_map_color_diffuse = False
					mtex.use_map_alpha = False
					mtex.specular_factor = .2
					mtex.use_map_specular = True
					mtex.use_map_alpha = False
				else:
					mtex.use = False

		except Exception as inst:
			print("Error loading " + textureBasename)
			print (type(inst))	   # the exception instance
			print (inst.args)	   # arguments stored in .args
			print (inst)
			# If error loading texture, turn transparency off
			matdata.alpha = 1.0
			matdata.use_transparency = True
			
		texCounter = texCounter + 1;
		
	#bpy.types.Mesh.update (calc_tessface=True)
	me_ob.update()
	
	# print("vrtxList: " + str(vrtxList))
	# print("nbVrtx: " + str(nbVrtx))
	for i in range(1, nbVrtx):
		#print("vrtxList[" + str(i) + "]: " + str(vrtxList[i]))
		groupname = vrtxList[i][0]
		vg = obmesh.vertex_groups.get(groupname)
		if not vg:
			vg = obmesh.vertex_groups.new(groupname)
		vg.add([vrtxList[i][2]], vrtxList[i][1], "REPLACE")
	
	mod = obmesh.modifiers.new(type="ARMATURE",name="Armature")
	mod.use_vertex_groups = True
	mod.object = armature_object
	



	bpy.context.scene.objects.link(obmesh)
	bpy.context.scene.update()

# def removeUnusedBonesRecursive(bone, level):
#	  global meshes
#	  global mesh_objects
#	  
#	  print("checking bone" + bone.name + " at level " + str(level))
#	  
#	  for one_child in bone.children:
#		  removeUnusedBonesRecursive(one_child, level+1)
#		  
#		  found = False
# 
#		  # This is really expensive - and doesn't seem to work
#		  # Look for bone's vertex group
#		  # for one_mesh, one_mesh_object in zip(meshes, mesh_objects):
#		  #		for one_group in one_mesh_object.vertex_groups:
#		  #			for one_vertex in one_mesh.vertices:
#		  #				for member_group in one_vertex.groups:
#		  #					if member_group == one_group:
#		  #						found = True
#		  #						break
#		  # 
#		  # if (found):
#		  if (one_child.name.lower().startswith("unused")):
#			  one_child.select = True
#			  bpy.ops.armature.delete()

# def meshmerge(selectedobjects):
#	  bpy.ops.object.mode_set(mode='OBJECT')
#	  cloneobjects = []
#	  if len(selectedobjects) > 1:
#		  print("selectedobjects:",len(selectedobjects))
#		  count = 0 #reset count
#		  for count in range(len( selectedobjects)):
#			  #print("Index:",count)
#			  if selectedobjects[count] != None:
#				  me_da = selectedobjects[count].data.copy() #copy data
#				  me_ob = selectedobjects[count].copy() #copy object
#				  #note two copy two types else it will use the current data or mesh
#				  me_ob.data = me_da
#				  bpy.context.scene.objects.link(me_ob)#link the object to the scene #current object location
#				  print("Index:",count,"clone object",me_ob.name)
#				  cloneobjects.append(me_ob)
#		  #bpy.ops.object.mode_set(mode='OBJECT')
#		  for i in bpy.data.objects: i.select = False #deselect all objects
#		  count = 0 #reset count
#		  #bpy.ops.object.mode_set(mode='OBJECT')
#		  for count in range(len( cloneobjects)):
#			  if count == 0:
#				  bpy.context.scene.objects.active = cloneobjects[count]
#				  print("Set Active Object:",cloneobjects[count].name)
#			  cloneobjects[count].select = True
#		  bpy.ops.object.join()
#		  return cloneobjects[0]
	
def fileImport(filename, removeUnusedBones, combineMeshes):
	
	global rootDir
	global warningCounter
	global logf
	global meshes
	global mesh_objects
	global unused_bones

	print ("------------------------------------------------------------")
	print ("--------------SCRIPT EXECUTING PYTHON IMPORTER--------------")
	print ("------------------------------------------------------------")
	print ("Importing file: ", filename)

	rootDir = os.path.dirname(filename)
	print ("rootDir: " + rootDir)
	file = open(filename,'r')
	
	boneCount = ImportArmature(file, filename)
	print("Bone count: " + str(boneCount))
	
	meshCount = int(ReadLineIgnoreComments(file))
	print("Mesh count: " + str(meshCount))
	
	for i in range(0, meshCount):
		importMesh(file, boneCount)
		
	# This can take a little while
	if (removeUnusedBones):
		print("Looking for unused bones")
		# reverse to work from leaf bones up to root
		unused_bones.reverse()
		for one_bone in unused_bones:
			if (one_bone.children == None):
				one_bone.select = True
				bpy.ops.armature.delete()
		# for one_bone in armature_object.data.edit_bones:
		#	  removeUnusedBonesRecursive(one_bone, 0)
		
	# switch to object mode and deselect all
	bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
	bpy.ops.object.select_all(action="DESELECT")

	# if selected, combine meshes into a single mesh
	
 
	   
	if (combineMeshes):
		bpy.ops.object.select_by_type(extend=False,type="MESH")
		bpy.context.scene.objects.active=bpy.context.selected_objects[0]
		# for one_object in mesh_objects:
		#	  one_object.select = True
		bpy.ops.object.join()
		bpy.ops.object.mode_set(mode='EDIT', toggle=False)
		bpy.ops.mesh.remove_doubles()
		bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
		bpy.context.active_object.name =  'Mesh'
 

	

def getInputFilename(filename, removeUnusedBones, combineMeshes):
	fileImport(filename, removeUnusedBones, combineMeshes)



class IMPORT_OT_mesh_ascii(bpy.types.Operator):
	'''Load an XNALara ASCII mesh File'''
	bl_idname = "import_scene.ascii"
	bl_label = "Import XNALara Extended Mesh"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	
	# List of operator properties, the attributes will be assigned
	# to the class instance from the operator settings before calling.
	filepath = StringProperty(name="File Path", description="Filepath used for importing the file", maxlen= 1024, default= "")
	removeUnusedBones = False
	#removeUnusedBones = BoolProperty(name="Remove Unused Bones?", description="Remove unused bones from the armature upon import?", default=False)
	combineMeshes = BoolProperty(name="Combine Meshes?", description="Combine all meshes into a single object?", default=False)
	def execute(self, context):
		getInputFilename(self.filepath, self.removeUnusedBones, self.combineMeshes)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}  

def menu_func(self, context):
	self.layout.operator(IMPORT_OT_mesh_ascii.bl_idname, text="XNALara Extended Mesh (.ascii)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
	register()
	
	
	
def ReadLine(file):
	line = file.readline()
	if line.endswith('\n'):
		line = line[:-1]
	if line.endswith('\r'):
		line = line[:-1]
	return line


def ReadLineIgnoreComments(file):
	line = ReadLine(file)
	pos = line.find('#')
	if pos >= 0:
		line = line[0:pos]
	return line


def ReadTuple(file):
	line = ReadLineIgnoreComments(file)
	return line.split()		   


def unpack_list(list_of_tuples):
	l = []
	for t in list_of_tuples:
		l.extend(t)
	return l

def has_bone(armature_object, boneName):
	has_key = False

	for one_bone in armature_object.data.edit_bones:
		if one_bone.name == boneName:
			has_key = True
	
	return has_key
 
def ImportArmature(file,filename):
	global armature
	global armature_object
	print ('XNAaraL v1.4')
	boneCount = int(ReadLineIgnoreComments(file))

	armature = bpy.data.armatures.new("Armature")
	armature_object = bpy.data.objects.new("Armature", armature)
	bpy.context.scene.objects.link(armature_object)
	for i in bpy.context.scene.objects: i.select = False
	armature.draw_type = 'STICK'
	armature_object.select = True
	bpy.context.scene.objects.active = armature_object
	bpy.ops.object.mode_set(mode='EDIT')
	armature_object.show_x_ray = True;

	global bonesNameList # bone's names list
	bonesNameList = []
	boneParentList = []
	boneTupleList = []
	bonesList = []
	boneChildRel = []

	# for all bones
	for i in range(0, boneCount):
		boneName = ReadLine(file)
		# print boneName
		parentID = int(ReadLineIgnoreComments(file))
		tuple = ReadTuple(file) # relPosition # .replace(',','.')


		bonesNameList.append(boneName)
		boneTupleList.append(tuple)
		boneParentList.append(parentID)

		bpy.ops.object.mode_set(mode='EDIT')
		editBone = armature_object.data.edit_bones.new(boneName)

		x = float(tuple[0])
		y = float(tuple[1])
		z = float(tuple[2])
		editBone.head = Vector([x, -z, y])
		editBone.tail = Vector([x, -z, y-0.2])



		boneChildRel.append([0, 0, 0, 0, 0, 0, 0, 0, False])
		bonesList.append(editBone) # insert into the global name's bone list
		if (i != 0):
			editBone.parent = armature.edit_bones[bonesNameList[0]]

	for i in range(0, boneCount):
		boneName = bonesNameList[i]
		# print boneName
		parentID = boneParentList[i]
		tuple = boneTupleList[i]
		x = float(tuple[0])
		y = float(tuple[1])
		z = float(tuple[2])
		
		if has_bone(armature_object, boneName):
			editBone = armature.edit_bones[boneName]
		else:
			editBone = None
		
		if filename.find("ear Effe") > -1:
			return
		# if bone has parent
		if parentID != -1 and editBone != None and parentID in bonesNameList:
			editBone.parent = armature.edit_bones[bonesNameList[parentID]]

			# if it's a "used" bone add its head's coordinate to tail 
			if not boneName.startswith('unused'):
				boneChildRel[parentID][0] += x
				boneChildRel[parentID][1] += -z
				boneChildRel[parentID][2] += y
				boneChildRel[parentID][3] += 1
			else: # else, it's a "unused" bone
				boneChildRel[parentID][4] += x
				boneChildRel[parentID][5] += -z
				boneChildRel[parentID][6] += y
				boneChildRel[parentID][7] += 1

		# move "unused" bones into layer 2
		if boneName.startswith('unused'):
			# for i in range(0, 30):
			#	  editBone.layers[i] = False;
			# editBone.layers[31] = True;
			# editBone.hide = True;
			unused_bones.append(editBone)

	# now for all bones, set the tail position according to children's head
	if filename.find("ssassins") > -1:
		return
	for i in range(0, boneCount):
		# if there are at least one "used" child
		if boneChildRel[i][3]>0:
			bonesList[i].tail[0] = boneChildRel[i][0] / boneChildRel[i][3]	# x/nb
			bonesList[i].tail[1] = boneChildRel[i][1] / boneChildRel[i][3]	# y/nb
			bonesList[i].tail[2] = boneChildRel[i][2] / boneChildRel[i][3]	# z/nb
			boneChildRel[i][8] = True
		else:	# else try to use "unused" child
			if boneChildRel[i][7]>0:
				bonesList[i].tail[0] = boneChildRel[i][4] / boneChildRel[i][7]	# x/nb
				bonesList[i].tail[1] = boneChildRel[i][5] / boneChildRel[i][7]	# y/nb
				bonesList[i].tail[2] = boneChildRel[i][6] / boneChildRel[i][7]	# z/nb
				boneChildRel[i][8] = True

	bpy.context.scene.update()

	for i in range(0, boneCount):

		if has_bone(armature_object, bonesNameList[i]):
			bone = armature.edit_bones[bonesNameList[i]]

			if (has_bone(armature_object, bonesNameList[parentID])):
				parent = armature.edit_bones[bonesNameList[parentID]]
			else:
				parent = None
			
			# if (parent.tail == editBone.head):
			#	  editBone.use_connect = True;

			if (editBone != None and parent != None):
				if (editBone.tail == parent.head):
					editBone.use_connect = True;

			# If the tail's bone couldn't be calculated, then take the parent vector direction (tail - head)
			if boneChildRel[i][8] == False and bone.parent != None:
				dx = bone.parent.tail[0] - bone.parent.head[0]
				dy = bone.parent.tail[1] - bone.parent.head[1]
				dz = bone.parent.tail[2] - bone.parent.head[2]
				bone.tail[0] = bone.head[0] + dx
				bone.tail[1] = bone.head[1] + dy
				bone.tail[2] = bone.head[2] + dz

			# Monkey 13				
			if bone.length <=0.0000001:
				#print bone.name
				if bone.length <=0.0:
					print (' - ')
					bone.tail[1] = bone.head[1] - 0.02
				else:
					print (' + ')
					bone.tail[1] = bone.head[1] + 0.02

	bpy.context.scene.update()
	return boneCount