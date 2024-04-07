import bpy
import math
from math import inf
import time
import os
from .util import *
bl_info = {
    "name": "烘焙功能菜单",        # 插件名称
    "author": "王思",        # 作者名称
    "version": (0, 3, 1),                # 插件版本号
    "blender": (3, 6, 0),                # Blender 软件最低版本要求
    "location": "Blender插件框架",                # 位置信息
    "description": "洞窝blender烘焙脚本开发",                # 插件描述
    "doc_url": "https://www.baidu.com",        # 插件文档链接
    "tracker_url": "https://www.baidu.com",        # 报告问题链接
    "category": "View",            # 插件分类
} 
def get_item_design_id(design_str):
    design_str_arr = design_str.split(":")
    return design_str_arr[1]

def get_design(context):
    return get_item_design_id(context.scene.design_property)
#bl_idname 必须 xx.xx 的格式，否则会报错。execute() 函数中可以执行自定义指令。
# 定义一个操作类
# 第一个按钮的操作类
class CustomOperator1(bpy.types.Operator):
    bl_idname = "custom.operator1"  # 操作的唯一标识符
    bl_label = "Custom Operator 1"   # 操作的名称
    bl_description = "根据模型面积添加烘焙节点使用对应大小图像"
    def execute(self, context):
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
                        if any(s < 0 for s in obj.scale):
                            FlipNormal = True
                        else:
                            FlipNormal = False
                        # 应用对象变换
                        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True) #应用全部变换
                        if FlipNormal:
                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.mesh.select_all(action='SELECT')
                            bpy.ops.mesh.flip_normals()
                            bpy.ops.object.mode_set(mode='OBJECT')
                            print("网格法线已翻转")
                print ("应用变换完毕")
                return
        dulihua()
        yingyongbianhuan()
        # 图像资源名称
        Rate = 1
        image512_name = "bake512"
        image1K_name = "bake1024"
        image2K_name = "bake2048"
        image4K_name = "bake4096"
        if image512_name not in bpy.data.images:
            bpy.ops.image.new(name=image512_name, width=512*Rate, height=512*Rate)
        if image1K_name not in bpy.data.images:
            bpy.ops.image.new(name=image1K_name, width=1024*Rate, height=1024*Rate)
        if image2K_name not in bpy.data.images:
            bpy.ops.image.new(name=image2K_name, width=2048*Rate, height=2048*Rate)
        if image4K_name not in bpy.data.images:
            bpy.ops.image.new(name=image4K_name, width=4096*Rate, height=4096*Rate)


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
                                if 0 < model_area <= 0.2:
                                    bake_node.image = bpy.data.images.get("bake512")
                                    print("使用了bake512")
                                elif 0.2 < model_area <= 0.5:
                                    bake_node.image = bpy.data.images.get("bake1024")
                                    print("使用了bake1024")  
                                elif 0.5 < model_area <= 10:
                                    bake_node.image = bpy.data.images.get("bake2048")
                                    print("使用了bake2048")  
                                else:
                                    bake_node.image = bpy.data.images.get("bake4096")
                                    print("使用了bake4096")    
                                nodes.active = bake_node
        print("Custom Operator 2 executed")
        return {'FINISHED'}
# 第二个按钮的操作类
class CustomOperator2(bpy.types.Operator):
    bl_idname = "custom.operator2"  # 操作的唯一标识符
    bl_label = "Custom Operator 2"   # 操作的名称
    bl_description = "删除工程中bakeNode节点和图像资源"
    def execute(self, context):
        # 获取场景中所有的材质
        materials = bpy.data.materials
        # 循环遍历所有的材质
        for material in materials:
            # 如果材质使用了节点
            if material.use_nodes:
                node_tree = material.node_tree
                
                # 获取所有节点
                nodes = node_tree.nodes
                
                # 存储要删除的节点
                nodes_to_remove = []
                
                # 遍历节点，查找名为“bakeNode”的节点
                for node in nodes:
                    if node.type == 'TEX_IMAGE' and node.name == "bakeNode":
                        nodes_to_remove.append(node)
                
                # 删除所有名为“bakeNode”的节点
                for node in nodes_to_remove:
                    node_tree.nodes.remove(node)      
        # 删除贴图资源
        for img in bpy.data.images:
         if "bake1024" in img.name or "bake2048" in img.name or "bake4096" in img.name or "bake512" in img.name:
            bpy.data.images.remove(img)
        # 在这里编写第二个按钮的操作逻辑
        print("Custom Operator 2 executed")
        return {'FINISHED'}

# 第三个按钮的操作类
class CustomOperator3(bpy.types.Operator):
    bl_idname = "custom.operator3"  # 操作的唯一标识符
    bl_label = "Custom Operator 3"   # 操作的名称
    bl_description = "遍历所有对象,合并它的子级并解除父级,注意不要放在合集里"
    def execute(self, context):
      # 检查是否存在名为“软装”的集合
        def check_collection_existence(collection_name):
            for collection in bpy.data.collections:
                if collection.name == collection_name:
                    return True
            return False

        # 创建名为“软装”的集合
        def create_collection(collection_name):
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)
        bpy.ops.object.select_all(action='DESELECT')
        # 将对象移动到指定的集合中
        def move_object_to_collection(obj, collection_name):
            if check_collection_existence(collection_name):
                collection = bpy.data.collections.get(collection_name)
                if collection:
                    collection.objects.link(obj)

        collection_name = "软装"
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
                    
                    # 将合并后的对象移动到“软装”集合中
                    selct_objs_move_to_collection(collection_name)
                    #move_object_to_collection(merged_obj, collection_name)
                    
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
            
        print("Custom Operator 3 executed")
        return {'FINISHED'}
# 第四个按钮的操作类
class CustomOperator4(bpy.types.Operator):
    bl_idname = "custom.operator4"  # 操作的唯一标识符
    bl_label = "Custom Operator 4"   # 操作的名称
    bl_description = "遍历所有对象,删除第二个和后面所有的UV,并添加bakeUV"
    def execute(self, context):
        # 在这里编写第三个按钮的操作逻辑
        def remove_second_and_subsequent_uv():
            # 获取场景中的所有对象
            all_objects = bpy.data.objects
            
            # 遍历场景中的所有对象
            for obj in all_objects:
                # 检查对象是否是网格对象
                if obj.type == 'MESH':
                    # 获取对象的网格数据
                    mesh = obj.data
                    # 检查对象是否有多个 UV 图层
                    if len(mesh.uv_layers) > 1:
                        # 从第二个 UV 图层开始删除，直到只剩下一个
                        for i in range(len(mesh.uv_layers) - 1, 0, -1):
                            uv_layer_to_remove = mesh.uv_layers[i]
                            mesh.uv_layers.remove(uv_layer_to_remove)
                        print("已删除", obj.name, "的第二个及其后的所有 UV 图层")
                    # 创建一个新的 UV 贴图
                    uv_layer = obj.data.uv_layers.new(name="bakeUV")
                    # 选择第二个 UV 图层
                    obj.data.uv_layers.active_index = 1
        # 执行函数以删除第二个及其后的所有 UV 图层
        remove_second_and_subsequent_uv()
        # 获取名为“硬装”的合集
        collection = bpy.data.collections.get("硬装")
        bpy.ops.object.mode_set(mode='OBJECT')
        if collection:
            # 获取默认的场景对象
            scene = bpy.context.scene
            view_layer = bpy.context.view_layer

            # 遍历合集中的所有物体
            for obj in collection.objects:
                # 清除之前的选择和活动对象
                bpy.ops.object.select_all(action='DESELECT')
                view_layer.objects.active = None

                # 选择当前物体
                obj.select_set(True)
                view_layer.objects.active = obj

                # 进入编辑模式执行UV投射
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.001)
                bpy.ops.object.mode_set(mode='OBJECT')
        else:
            print("未找到名为“硬装”的合集")

        print("Custom Operator 4 executed")
        return {'FINISHED'}
# 第五个按钮的操作类
class CustomOperator5(bpy.types.Operator):
    bl_idname = "custom.operator5"  # 操作的唯一标识符
    bl_label = "Custom Operator 5"   # 操作的名称
    bl_description = "合并硬装的集合[硬装],天花板,墙,地板,并记录方案名在自定义属性里"
    def execute(self, context):
        # 遍历名为“硬”的集合
        collection_name = "硬装"
        collection = bpy.data.collections.get(collection_name)
        projectName = get_design(context)
        collection["projectName"] = projectName
        print("方案名为 '%s' 记录在硬装合集自定义属性里" % projectName)
        #bpy.data.collections.get("硬装")["projectName"]
        if collection:
            # 初始化计数器
            ceiling_count = 0
            floor_count = 0
            wall_count = 0
            
            # 初始化最低点和最高点
            min_z = inf
            max_z = -inf
            
            # 遍历集合中的每个对象
            for obj in collection.objects:
                # 获取对象的最低和最高点
                vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
                min_z = min(min_z, min(v.z for v in vertices))
                max_z = max(max_z, max(v.z for v in vertices))
                
            # 遍历集合中的每个对象
            ceiling_objects = []
            floor_objects = []
            wall_objects = []
            for obj in collection.objects:
                # 获取对象的最低和最高点
                vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
                min_height = min(v.z for v in vertices)
                max_height = max(v.z for v in vertices)
                
                # 判断并将对象添加到相应的列表中
                if max_height < 0.05:
                    floor_objects.append(obj)
                elif min_height > 2:
                    ceiling_objects.append(obj)
                else:
                    wall_objects.append(obj)
            
            # 合并 Ceiling 对象
            if ceiling_objects:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in ceiling_objects:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = ceiling_objects[0]
                bpy.ops.object.join()
                bpy.context.active_object.name = "Ceiling"
                ceiling_count = len(ceiling_objects)
            
            # 合并 Floor 对象
            if floor_objects:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in floor_objects:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = floor_objects[0]
                bpy.ops.object.join()
                bpy.context.active_object.name = "Floor"
                floor_count = len(floor_objects)
            
            # 合并 Wall 对象
            if wall_objects:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in wall_objects:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = wall_objects[0]
                bpy.ops.object.join()
                bpy.context.active_object.name = "Wall"
                wall_count = len(wall_objects)
            
            # 打印结果
            print("合并了 %d 个 Ceiling 对象" % ceiling_count)
            print("合并了 %d 个 Floor 对象" % floor_count)
            print("合并了 %d 个 Wall 对象" % wall_count)
        else:
            print("没有找到名为 '%s' 的集合" % collection_name)

        print("Custom Operator 5 executed")
        return {'FINISHED'}
# 第六个按钮的操作类
class CustomOperator6(bpy.types.Operator):
    bl_idname = "custom.operator6"  # 操作的唯一标识符
    bl_label = "Custom Operator 6"   # 操作的名称
    bl_description = "将选中对象的漫射材质删除,并新建一个漫射材质槽"
    def execute(self, context):
        # 遍历每个选中的对象
        for obj in bpy.context.selected_objects:
            # 遍历每个材质槽
            for slot in obj.material_slots:
                material = slot.material
                # 检查材质是否存在且不含有 "glass" 或 "mirror" 关键字
                if material and ("glass" not in material.name.lower() and "mirror" not in material.name.lower()):
                    # 删除材质槽中的材质
                    bpy.data.materials.remove(material)

                    # 创建新的材质
                    new_material = bpy.data.materials.new(name=obj.name + "_mt")

                    # 如果物体已经存在材质槽，则将新材质插入到第一个位置
                    if obj.material_slots:
                        obj.material_slots[0].material = new_material
                    # 否则，创建一个新的材质槽并将新材质放置其中
                    else:
                        bpy.ops.object.material_slot_add()
                        obj.material_slots[0].material = new_material

        print("操作完成")
        print("Custom Operator 5 executed")
        return {'FINISHED'}

# 第七个按钮的操作类
class CustomOperator7(bpy.types.Operator):
    bl_idname = "custom.operator7"  # 操作的唯一标识符
    bl_label = "Custom Operator 7"   # 操作的名称
    bl_description = "调整渲染设置,遍历渲染图片到D盘bakeTemp目录"
    def execute(self, context):
        # 获取当前场景的渲染设置  
        render_settings = bpy.context.scene.render  
        
        # 检查并打印渲染引擎  
        if render_settings.engine == 'CYCLES':  
            print("当前使用的是Cycles渲染引擎")  
        else:  
            bpy.context.scene.my_bool_prop1 = True
            print("当前使用的不是Cycles渲染引擎,自动覆盖设置")
        if bpy.context.scene.my_bool_prop1:
            # 设置渲染引擎为 Cycles
            bpy.context.scene.render.engine = 'CYCLES'
            # 设置渲染设备为 GPU
            bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
            #bpy.context.preferences.addons['cycles'].preferences.devices[0].use = True
            # 设置渲染参数
            bpy.context.scene.cycles.samples = 1024
            bpy.context.scene.cycles.preview_samples = 1024
            bpy.context.scene.cycles.use_denoising = False
            bpy.context.scene.cycles.preview_denoising = False
            bpy.context.scene.cycles.seed = 0
            bpy.context.scene.cycles.samples_threshold = 0.1
        
        # 检查并创建目录
        # def create_directory_if_not_exists(directory):
        #     if not os.path.exists(directory):
        #         os.makedirs(directory)
        # # 创建 bakeTemp 文件夹在 d 盘
        # bake_temp_dir = "D:/bakeTemp"
        # create_directory_if_not_exists(bake_temp_dir)

        def get_active_image_texture_name(material):  
            if not material.node_tree:  
                return None  
            # 获取材质的活动节点  
            active_node = material.node_tree.nodes.active  
            if not active_node or not isinstance(active_node, bpy.types.ShaderNodeTexImage):  
                print("获取尺寸出错")
                return None    
            # 获取图片资源名  
            image = active_node.image  
            if image:  
                return image.name
            print("获取尺寸出错")  
            return None  

        # 获取选中的对象
        def getBakeSize():
            selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']  
            if not selected_objects:  
                print("没有选中任何网格对象。")  
            # 遍历选中对象的材质  
            for obj in selected_objects:  
                for slot in obj.material_slots:  
                    material = slot.material  
                    if material:  
                        image_name = get_active_image_texture_name(material)  
                        return(image_name)

        output_folder = "D:/bakeTemp/"+bpy.data.collections.get("硬装")["projectName"]
        print("输出路径:" + output_folder)
        # 遍历场景中的所有网格物体  
        i = 0 #计数
        SCenemesh = 0 #场景模型数量
        for obj in bpy.context.scene.objects:   
            if obj.type == 'MESH':  
                SCenemesh = SCenemesh + 1
        def saveBakeImge(image_name, output_folder,ObjName):  
            # 确保输出文件夹存在  
            if not os.path.exists(output_folder):  
                os.makedirs(output_folder)  
            
            # 查找名为image_name的图片资源  
            for image in bpy.data.images:  
                if image.name == image_name:  
                    # 构造完整的图片路径  
                    file_path = os.path.join(output_folder, f"{ObjName}.png")  
                    try:
                        # 切换到图像编辑器上下文
                        bpy.context.area.type = 'IMAGE_EDITOR'
                        bpy.context.area.spaces.active.image = image

                        bpy.ops.image.save_as(save_as_render=True, show_multiview=False, use_multiview=False, filepath=file_path)
                        print("Image saved successfully to:", file_path)
                    except Exception as e:
                        print("Error saving image:", e)
                    return   
            print(f"未找到名为 {image_name} 的图片资源。")  
        # 记录结束时间  
        start_time = time.time()   
        for obj in bpy.context.scene.objects:
            error_objects = []  # 用于存储出错物体的名称     
            if obj.type == 'MESH':
                # 单张时间开始    
                solostart_time = time.time() 
                bpy.ops.object.select_all(action='DESELECT') 
                obj.select_set(True)
                ObjName = obj.name
                print(f"当前选中的mesh是 {ObjName} ")
                # 重置烘焙节点
                def change_image_source_to_generated(node):  
                    if node.type == 'TEX_IMAGE' and node.name == 'bakeNode':  
                        # 如果图像纹理节点没有连接的图像，则无需更改  
                        if node.image:  
                            # 将图像属性来源更改为"生成"  
                            node.image.source = 'GENERATED' 
                for slot in obj.material_slots:  
                    if slot.material:  
                        for node in slot.material.node_tree.nodes:  
                            change_image_source_to_generated(node) 

                # 开始烘焙  
                bakeImageSize = getBakeSize()
                print(f"对象 {bakeImageSize} 图片大小")
                try:
                    bpy.ops.object.bake(save_mode='EXTERNAL', use_cage=False)  
                    # 保存烘焙后的图像  
                    saveBakeImge(bakeImageSize,output_folder,ObjName)
                except Exception as e:
                    error_objects.append(obj.name)  
                i = i + 1
                # 计算单张渲染时间   
                soloend_time = time.time()
                solorender_time = soloend_time - solostart_time 
                print("进度:["+str(i)+"/"+str(SCenemesh)+"]")
                print(f"单张用时: {solorender_time:.2f} 秒")
                # 取消选中当前物体，为下一个物体做准备  
                obj.select_set(False)  

            else:  
                print(f"选中的不是网格 {obj.name}")
            if error_objects:  
                print(f"烘焙错误对象: {', '.join(error_objects)}") 
        # 完成后取消所有物体的选中状态  
        bpy.ops.object.select_all(action='DESELECT')
        # 记录结束时间  
        end_time = time.time()  
        # 计算渲染时间（秒）  
        render_time = end_time - start_time 
        # 打印渲染时间  
        print(f"所有对象渲染完毕: {render_time:.2f} 秒","错误数量为:",str(len(error_objects)))
        return {'FINISHED'}

# 第八个按钮的操作类
class CustomOperator8(bpy.types.Operator):
    bl_idname = "custom.operator8"  # 操作的唯一标识符
    bl_label = "Custom Operator 8"   # 操作的名称
    bl_description = "调整渲染设置,将选中对象渲染图片到D盘bakeTemp目录"
    def execute(self, context):
        # 获取当前场景的渲染设置  
        render_settings = bpy.context.scene.render  
        
        # 检查并打印渲染引擎  
        if render_settings.engine == 'CYCLES':  
            print("当前使用的是Cycles渲染引擎")  
        else:  
            bpy.context.scene.my_bool_prop1 = True
            print("当前使用的不是Cycles渲染引擎,自动覆盖设置")
        if bpy.context.scene.my_bool_prop1:
            # 设置渲染引擎为 Cycles
            bpy.context.scene.render.engine = 'CYCLES'
            # 设置渲染设备为 GPU
            bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
            #bpy.context.preferences.addons['cycles'].preferences.devices[0].use = True
            # 设置渲染参数
            bpy.context.scene.cycles.samples = 1024
            bpy.context.scene.cycles.preview_samples = 1024
            bpy.context.scene.cycles.use_denoising = False
            bpy.context.scene.cycles.preview_denoising = False
            bpy.context.scene.cycles.seed = 0
            bpy.context.scene.cycles.samples_threshold = 0.1
        
        # 检查并创建目录
        # def create_directory_if_not_exists(directory):
        #     if not os.path.exists(directory):
        #         os.makedirs(directory)
        # # 创建 bakeTemp 文件夹在 d 盘
        # bake_temp_dir = "D:/bakeTemp"
        # create_directory_if_not_exists(bake_temp_dir)

        def get_active_image_texture_name(material):  
            if not material.node_tree:  
                return None  
            # 获取材质的活动节点  
            active_node = material.node_tree.nodes.active  
            if not active_node or not isinstance(active_node, bpy.types.ShaderNodeTexImage):  
                print("获取尺寸出错")
                return None    
            # 获取图片资源名  
            image = active_node.image  
            if image:  
                return image.name
            print("获取尺寸出错")  
            return None  

        # 获取选中的对象
        def getBakeSize():
            selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']  
            if not selected_objects:  
                print("没有选中任何网格对象。")  
            # 遍历选中对象的材质  
            for obj in selected_objects:  
                for slot in obj.material_slots:  
                    material = slot.material  
                    if material:  
                        image_name = get_active_image_texture_name(material)  
                        return(image_name)

        output_folder = "D:/bakeTemp/"+bpy.data.collections.get("硬装")["projectName"]
        print("输出路径:" + output_folder)
        # 遍历场景中的所有网格物体  
        i = 0 #计数
        def saveBakeImge(image_name, output_folder,ObjName):  
            # 确保输出文件夹存在  
            if not os.path.exists(output_folder):  
                os.makedirs(output_folder)  
            
            # 查找名为image_name的图片资源  
            for image in bpy.data.images:  
                if image.name == image_name:  
                    # 构造完整的图片路径  
                    file_path = os.path.join(output_folder, f"{ObjName}.png")  
                    try:
                        # 切换到图像编辑器上下文
                        bpy.context.area.type = 'IMAGE_EDITOR'
                        bpy.context.area.spaces.active.image = image

                        bpy.ops.image.save_as(save_as_render=True, show_multiview=False, use_multiview=False, filepath=file_path)
                        print("Image saved successfully to:", file_path)
                    except Exception as e:
                        print("Error saving image:", e)
                    return   
            print(f"未找到名为 {image_name} 的图片资源。")  
        # 记录结束时间  
        start_time = time.time()   
        # 获取当前场景中选中的对象
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            error_objects = []  # 用于存储出错物体的名称     
            if obj.type == 'MESH':
                # 单张时间开始    
                solostart_time = time.time() 
                bpy.ops.object.select_all(action='DESELECT') 
                obj.select_set(True)
                ObjName = obj.name
                print(f"当前选中的mesh是 {ObjName} ")
                # 重置烘焙节点
                def change_image_source_to_generated(node):  
                    if node.type == 'TEX_IMAGE' and node.name == 'bakeNode':  
                        # 如果图像纹理节点没有连接的图像，则无需更改  
                        if node.image:  
                            # 将图像属性来源更改为"生成"  
                            node.image.source = 'GENERATED' 
                for slot in obj.material_slots:  
                    if slot.material:  
                        for node in slot.material.node_tree.nodes:  
                            change_image_source_to_generated(node) 

                # 开始烘焙  
                bakeImageSize = getBakeSize()
                print(f"对象 {bakeImageSize} 图片大小")
                try:
                    bpy.ops.object.bake(save_mode='EXTERNAL', use_cage=False)  
                    # 保存烘焙后的图像  
                    saveBakeImge(bakeImageSize,output_folder,ObjName)
                except Exception as e:
                    error_objects.append(obj.name)  
                i = i + 1
                # 计算单张渲染时间   
                soloend_time = time.time()
                solorender_time = soloend_time - solostart_time 
                print("进度:["+str(i)+"/"+str(selected_objects)+"]")
                print(f"单张用时: {solorender_time:.2f} 秒")
                # 取消选中当前物体，为下一个物体做准备  
                obj.select_set(False)  

            else:  
                print(f"选中的不是网格 {obj.name}")
            if error_objects:  
                print(f"烘焙错误对象: {', '.join(error_objects)}") 
        # 完成后取消所有物体的选中状态  
        bpy.ops.object.select_all(action='DESELECT')
        # 记录结束时间  
        end_time = time.time()  
        # 计算渲染时间（秒）  
        render_time = end_time - start_time 
        # 打印渲染时间  
        print(f"所有对象渲染完毕: {render_time:.2f} 秒","错误数量为:",str(len(error_objects)))
        return {'FINISHED'}
# 定义一个面板类
class CustomPanel(bpy.types.Panel):
    bl_idname = "Q1_PT_bekemenu"  # 面板的唯一标识符前后有字母加_pt_不报错
    bl_label = "功能集合"      # 面板的名称
    bl_space_type = 'VIEW_3D'      # 面板所在的区域
    bl_region_type = 'UI'          # 面板所在的区域类型
    bl_category = '洞窝blender烘焙菜单'   # 面板所在的类别

    def draw(self, context):
        layout = self.layout
        # 添加按钮到面板中，并为每个按钮指定相应的操作
        layout.operator("custom.operator5", text="硬装合并记录方案名")
        # 添加一个布尔属性
        #layout.prop(context.scene, "my_bool_prop", text="合并时保持应用父级位置")
        layout.operator("custom.operator3", text="软装合并网格")
        layout.operator("custom.operator4", text="删除第二UV,添加bakeUV")
        layout.operator("custom.operator1", text="添加bakeNode节点")
        layout.operator("custom.operator2", text="删除bakeNode节点")
        layout.prop(context.scene, "my_bool_prop1", text="覆盖渲染设置")
        layout.operator("custom.operator7", text="开始遍历烘焙")
        layout.operator("custom.operator8", text="手动选择烘焙")
        layout.operator("custom.operator6", text="自动化优化材质")
        

# 注册操作和面板类
def register():
    bpy.utils.register_class(CustomOperator1)
    bpy.utils.register_class(CustomOperator2)
    bpy.utils.register_class(CustomOperator3)
    bpy.utils.register_class(CustomOperator4)
    bpy.utils.register_class(CustomOperator5)
    bpy.utils.register_class(CustomOperator6)
    bpy.utils.register_class(CustomOperator7)
    bpy.utils.register_class(CustomOperator8)
    bpy.utils.register_class(CustomPanel)
    #bpy.types.Scene.my_bool_prop = bpy.props.BoolProperty(name="my_bool_prop", description="合并后是否应用父级,如何合并错位可以选择应用", default=True)
    bpy.types.Scene.my_bool_prop1 = bpy.props.BoolProperty(name="my_bool_prop1", description="是否覆盖当前场景的渲染设置", default=True)

    # # 调用单选框并检查其状态
    # if bpy.context.scene.my_bool_prop:
    #     print("单选框已勾选")
    # else:
    #     print("单选框未勾选")

# 注销操作和面板类
def unregister():
    bpy.utils.unregister_class(CustomOperator1)
    bpy.utils.unregister_class(CustomOperator2)
    bpy.utils.unregister_class(CustomOperator3)
    bpy.utils.unregister_class(CustomOperator4)
    bpy.utils.unregister_class(CustomOperator5)
    bpy.utils.unregister_class(CustomOperator6)
    bpy.utils.unregister_class(CustomOperator7)
    bpy.utils.unregister_class(CustomOperator8)
    bpy.utils.unregister_class(CustomPanel)
    #del bpy.types.Scene.my_bool_prop
    del bpy.types.Scene.my_bool_prop1

# 测试代码
if __name__ == "__main__":
    register()
