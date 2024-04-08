import bpy
import os

def get_obj(name):
    obj = bpy.data.objects.get(name)
    if not (obj):
        obj = new_empty_obj(name)
    return obj

def link_collection_all(name, obj):
    link_collection(name, obj)
    for child_obj in obj.children:
        link_collection(name, child_obj)
    
def link_collection(name, obj):
    col = get_collection(name)
    objCol = obj.users_collection[0]
    if (objCol == col):
        return
    col.objects.link(obj)
    bpy.context.scene.collection.children.unlink(obj)
    
def get_collection(name):
    col =  bpy.data.collections.get(name)
    if (col):
        return col
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col
       
    
def new_empty_obj(name):
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    emptyObjs = bpy.context.selected_objects[0]
    emptyObjs.name = name
    return emptyObjs


def selct_objs_move_to_collection(colName):
        get_collection(colName)
        colIndex = get_col_index(colName)
        bpy.ops.object.move_to_collection(collection_index=colIndex)
    
def get_col_index(colName):
    cols = get_all_colection_children()
    for i in range(len(cols)):
        if (cols[i].name == colName):
            return i
    return -1

def get_all_colection_children():
    return get_collection_children(bpy.context.scene.collection)
        
def get_collection_children(collection):
    cols = []
    cols.append(collection)
    for i in range(len(collection.children)):
        cols.extend(get_collection_children(collection.children[i]))
    return cols