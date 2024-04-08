import bpy
#软合集
# 检查是否存在名为“软”的集合
def check_collection_existence(collection_name):
    for collection in bpy.data.collections:
        if collection.name == collection_name:
            return True
    return False

# 创建名为“软”的集合
def create_collection(collection_name):
    new_collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(new_collection)

collection_name = "软"
if not check_collection_existence(collection_name):
    create_collection(collection_name)
    print(f"已创建名为'{collection_name}'的集合。")
else:
    print(f"名为'{collection_name}'的集合已存在。")

# 遍历所有的对象
for obj in bpy.data.objects:
    # 如果当前对象有子级
    if obj.children:
        # 判断是否有模型对象
        has_mesh_children = False
        for child in obj.children:
            if child.type == 'MESH':
                has_mesh_children = True
                break
        
        # 如果有模型对象，选中所有子级并设置活动对象为第一个子对象
        if has_mesh_children:
            bpy.context.view_layer.objects.active = obj.children[0]  # 将第一个子对象设为活动对象
            for child in obj.children:
                if child.type == 'MESH':
                    child.select_set(True)  # 选中子级模型对象
            obj.select_set(False)  # 取消选中父级对象
            
            # 合并选中的模型对象
            bpy.ops.object.join()
            
            # 重命名合并后的对象为父级的名称
            merged_obj = bpy.context.active_object
            merged_obj.name = obj.name
            
            # 保持父级对象的变换
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')  # 清除父级并保持变换结果 
            
            bpy.ops.object.select_all(action='DESELECT')

def delete_empty_objects():
    # 获取当前场景中的所有对象
    objects = bpy.context.scene.objects
    
    # 记录删除的对象数量
    deleted_count = 0
    
    # 循环遍历所有对象
    for obj in objects:
        # 检查对象是否没有网格数据且没有子对象
        if obj.type == 'EMPTY' and not obj.children and not obj.data:
            # 删除空对象
            bpy.data.objects.remove(obj, do_unlink=True)
            deleted_count += 1
    
    # 如果删除了至少一个对象，则继续执行删除操作
    if deleted_count > 0:
        delete_empty_objects()

# 调用函数以删除所有空对象
delete_empty_objects()

