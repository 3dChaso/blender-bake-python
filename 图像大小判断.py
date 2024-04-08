import bpy
def dulihua():
    for obj in bpy.context.scene.objects:   
        #遍历所有模型使其独立化
        for obj in bpy.data.objects:
            # 检查对象是否为模型对象
            if obj.type == 'MESH':
                # 选择对象
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                # 将对象的数据、材质等设为单一用户
                bpy.ops.object.make_single_user(object=True, obdata=True, material=True, animation=False, obdata_animation=False)
        print ("独立化完毕")
        return
def yingyongbianhuan():
    for obj in bpy.context.scene.objects:   
        #遍历所有模型使应用全部变换
        for obj in bpy.data.objects:
            # 检查对象是否为模型对象
            if obj.type == 'MESH':
                # 选择对象
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                # 将对象的数据、材质等设为单一用户
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True) #应用全部变换
        print ("应用变换完毕")
        return
dulihua()
yingyongbianhuan()
# 图像资源名称
image1K_name = "bake1024"
image2K_name = "bake2048"
image4K_name = "bake4096"
if image1K_name not in bpy.data.images:
    bpy.ops.image.new(name=image1K_name, width=1024, height=1024)
if image2K_name not in bpy.data.images:
    bpy.ops.image.new(name=image2K_name, width=2048, height=2048)
if image4K_name not in bpy.data.images:
    bpy.ops.image.new(name=image4K_name, width=4096, height=4096)


# 获取模型面积
def get_model_area(obj):
    return sum(face.area for face in obj.data.polygons)

# 遍历所有模型
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        model_area = get_model_area(obj)
    for slot in obj.material_slots:
                material = slot.material
                if material:
                    nodes = material.node_tree.nodes
                    has_bake_node = False
                    
                    # 检查材质中是否存在名为 "bakeNode" 的节点
                    for node in nodes:
                        if node.type == 'TEX_IMAGE' and node.name == "bakeNode":
                            has_bake_node = True
                            break
                    # 如果不存在 "bakeNode" 节点，则创建并设置图像资源
                    if not has_bake_node:
                        bake_node = nodes.new('ShaderNodeTexImage')
                        bake_node.name = "bakeNode"
                        if 0 < model_area <= 0.5:
                            bake_node.image = bpy.data.images.get("bake1024")
                            print("使用了bake1024")
                        elif 0.5 < model_area <= 10:
                            bake_node.image = bpy.data.images.get("bake2048")
                            print("使用了bake2048")  
                        else:
                            bake_node.image = bpy.data.images.get("bake4096")
                            print("使用了bake4096")    
                        nodes.active = bake_node

# # 遍历选中对象的所有材质
# for obj in selected_objects:
#     if obj.type == 'MESH':
#         for slot in obj.material_slots:
#             material = slot.material
#             if material:
#                 nodes = material.node_tree.nodes
#                 has_bake_node = False
                
#                 # 检查材质中是否存在名为 "bakeNode" 的节点
#                 for node in nodes:
#                     if node.type == 'TEX_IMAGE' and node.name == "bakeNode":
#                         has_bake_node = True
#                         break
                
#                 # 如果不存在 "bakeNode" 节点，则创建并设置图像资源
#                 if not has_bake_node:
#                     bake_node = nodes.new('ShaderNodeTexImage')
#                     bake_node.name = "bakeNode"
#                     bake_node.image = bpy.data.images.get("bake2048")
#                     print("Created bakeNode for material:", material.name)
