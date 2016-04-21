bl_info = {
	"name": "Show Modifiers",
	"author": "JuhaW",
	"version": (1, 0, 0),
	"blender": (2, 77, 0),
	"location": "Tools",
	"description": "Show selected objects modifiers/select objects based on modifier",
	"warning": "beta",
	"wiki_url": "https://github.com/JuhaW/ShowModifiers",
	"category": "Object",
}

import bpy
from collections import Counter

class ModifierPanel(bpy.types.Panel):
	bl_label = "Modifiers"
	bl_space_type = 'VIEW_3D'
	bl_region_type = "TOOLS"
	#bl_category = "Trees"

	
	def draw(self, context):
		
		layout = self.layout
		row = layout.row(align = True)
		row.operator('exec.showmodifiers')
		row = layout.row()
		row.prop(context.scene, 'ShowModTab', "Open on modifiers tab")
		row.prop(context.scene, 'ApplyModifier', "Apply modifier")
		
		col = layout.column()
		col = col.column_flow(columns = 2, align = False)
		for j,i in enumerate(V.modifiers):
			index = col.operator('exec.selectmodifierobjects',text = "(" + str(V.modcount[i]) + ")" + i)
			index.modifier = i
		if V.no_modifiers:
			col.alert = True
			col.operator('exec.selectnomodifierobjects', "(" + str(len(V.no_modifiers)) + ")" + "No Modifiers")

class V():
	
	modifiers = []
	modcount = []
	sel_objects = []
	no_modifiers = []
def apply_modifier(mod_name):
	try:
		bpy.ops.object.modifier_apply(modifier=mod_name)
	except RuntimeError as ex:
		# print the error incase its important... but continue
		print(ex)
		
def show_modifier_tab(modifier):
	
	for area in bpy.context.screen.areas:
		if area.type == 'PROPERTIES':
			if modifier in ('CLOTH', 'COLLISION', 'FLUID_SIMULATION', 'SMOKE','SOFT_BODY'):
				try:
					area.spaces[0].context = 'PHYSICS'
				except:
					pass
			elif modifier in ('PARTICLE_SYSTEM'):
				try:
					area.spaces[0].context = 'PARTICLES'
				except:
					pass	
			else:
				try:
					area.spaces[0].context = 'MODIFIER'
				except:
					pass
				
	o = bpy.context.object
	bool = [i.type in (modifier) for i in o.modifiers]
		
	for j, i in enumerate(o.modifiers):
		i.show_expanded = bool[j]

class Exec_SelectNoModifierObjects(bpy.types.Operator):		
	"""Select objects with this modifier"""
	bl_idname = "exec.selectnomodifierobjects"
	bl_label = "Select"
	
	
	def execute(self, context):
		
		bpy.ops.object.select_all(action='DESELECT')
		for oname in V.no_modifiers:
			bpy.context.scene.objects[oname].select = True
			bpy.context.scene.objects.active = bpy.context.scene.objects[oname]
		
		return {'FINISHED'}	

class Exec_SelectModifierObjects(bpy.types.Operator):		
	"""Select objects with this modifier"""
	bl_idname = "exec.selectmodifierobjects"
	bl_label = "Select"
	
	modifier = bpy.props.StringProperty()
	bool = False
	def execute(self, context):
		
		bpy.ops.object.select_all(action='DESELECT')
		print ("modifier:", self.modifier)
		for o in V.sel_objects:

			for i in o.modifiers:
				if self.modifier == i.type:

					o.select = True
					bpy.context.scene.objects.active = o
					if context.scene.ApplyModifier:
						apply_modifier(i.name)
						self.bool = True
		if context.scene.ShowModTab:
			show_modifier_tab(self.modifier)
		if self.bool:
			self.bool = False
			bpy.ops.object.select_all(action='DESELECT')
			for i in V.sel_objects:
				i.select = True
			Exec_ShowModifiers.execute(self, context)
			Exec_SelectModifierObjects.execute(self, context)
			
		return {'FINISHED'}
	
class Exec_ShowModifiers(bpy.types.Operator):		
	"""Show selected objects modifiers"""
	bl_idname = "exec.showmodifiers"
	bl_label = "Show Modifiers"
	
	def execute(self, context):
		
		V.modifiers = []
		V.no_modifiers = []
		V.sel_objects = bpy.context.selected_objects
		for o in V.sel_objects:
			mod = o.modifiers
			if mod.keys() != []:
				for i in mod:
					V.modifiers.append(i.type)
			else:
				V.no_modifiers.append(o.name)
		
		V.modcount = Counter(V.modifiers)
		V.modifiers = sorted(list(set(V.modifiers)))
		#print ("exec:", V.modcount)
		#print ("exec:", V.modifiers)
		
		return {'FINISHED'}


def register():
	
	bpy.utils.register_module(__name__)
	bpy.types.Scene.ShowModTab = bpy.props.BoolProperty(default = True)
	bpy.types.Scene.ApplyModifier = bpy.props.BoolProperty(default = False)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.ShowModTab
	del bpy.types.Scene.ApplyModifier

if __name__ == "__main__":
	register()