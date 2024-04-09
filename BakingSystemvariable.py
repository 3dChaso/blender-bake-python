import os
import ctypes
import subprocess
import bpy
from .quality import *
import time
from math import inf
from .util import *
#--------------------------读写系统变量--------------------------
def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        # 如果当前用户已经是管理员，则直接返回True
        return True
    else:
        return False
def Write_OS_Var():#写全局变量
    if not run_as_admin():
        print("请以管理员身份运行该程序！")
    else:
        bakePath = "D:\\bakeTemp\\"
        subprocess.call(["setx", "bakeTemp", bakePath])
        print("全局变量写入完毕,请重启程序")   
    
def read_OS_Var():#读取全局变量
    global path_value
    if not run_as_admin():
        print("请以管理员身份运行该程序！")
    else:
        path_value = os.getenv('bakeTemp')
        if path_value != None:
            print("读取全局变量成功-bakeTemp:", path_value)
            return True
        else:
            return False
             
def try_read_OS_Var():
    if not read_OS_Var():#失败，写入一次
        Write_OS_Var()
        return None
    else:
        return path_value
#--------------------------渲染器设置--------------------------
def render_set(context):
    # 获取当前场景的渲染设置  
    render_settings = bpy.context.scene.render  
    # 读取面板质量设置 
    qualityLevel = context.scene.my_value
    iniass = []
    # 检查并打印渲染引擎  
    if render_settings.engine == 'CYCLES':  
        print("当前使用的是Cycles渲染引擎")  
    else:  
        bpy.context.scene.my_bool_prop1 = True
        print("当前使用的不是Cycles渲染引擎,自动覆盖设置")
    if bpy.context.scene.my_bool_prop1:#覆盖按钮
        # 设置渲染引擎为 Cycles
        bpy.context.scene.render.engine = 'CYCLES'
        # 设置渲染设备为 GPU
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
        iniass = read_qulity_ini(qualityLevel)
        if len(iniass) > 0:#覆盖质量分级
            bpy.context.scene.cycles.samples = iniass[0]
            bpy.context.scene.cycles.preview_samples = iniass[1]
            bpy.context.scene.cycles.use_denoising = iniass[2]
            bpy.context.scene.cycles.preview_denoising = iniass[3]
            bpy.context.scene.cycles.seed = iniass[4]
            bpy.context.scene.cycles.samples_threshold = iniass[5]
            print(f"覆盖渲染质量为{qualityLevel}")
        else:#覆盖默认值
            bpy.context.scene.cycles.samples = 1024
            bpy.context.scene.cycles.preview_samples = 1024
            bpy.context.scene.cycles.use_denoising = False
            bpy.context.scene.cycles.preview_denoising = False
            bpy.context.scene.cycles.seed = 0
            bpy.context.scene.cycles.samples_threshold = 0.1
            print("使用的是默认值")
    return iniass
def read_qulity_ini(qulity):
    iniass = []
    if(HighCycles.INI_samples):
        print("读取到配置ini")
        if qulity == 1:
            # 使用 vars() 获取类的属性字典
            leve = vars(LowCycles)
        elif qulity == 2:
            leve = vars(MediumCycles)      
        elif qulity == 3:
            leve = vars(HighCycles)  
            # 遍历属性字典中的每个键值对，但排除特殊成员
        for member_name, member_value in leve.items():
            if not member_name.startswith("__"):
                iniass.append(member_value)
                print(f"成员名称: {member_name}, 成员值: {member_value}")
    else:
        print("没有读取到配置ini,使用默认参数")
    return iniass

#--------------------------方案名--------------------------
def get_item_design_id(design_str):
    design_str_arr = design_str.split(":")
    return design_str_arr[1]
def get_design(context):
    return get_item_design_id(context.scene.design_property)

#--------------------------获取烘焙贴图大小--------------------------
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
#--------------------------全程烘焙--------------------------
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

def OSoutput():
        OSoutput_folder = try_read_OS_Var()
        return OSoutput_folder+bpy.data.collections.get("硬装")["projectName"]+"\\Textures\\"

# 重置烘焙节点
def change_image_source_to_generated(node):  
    if node.type == 'TEX_IMAGE' and node.name == 'bakeNode':  
        # 如果图像纹理节点没有连接的图像，则无需更改  
        if node.image:  
            # 将图像属性来源更改为"生成"  
            node.image.source = 'GENERATED' 

def Bakeing(obj,output_folder,error_objects):
    # 单张时间开始    
    solostart_time = time.time() 
    bpy.ops.object.select_all(action='DESELECT') 
    obj.select_set(True)
    ObjName = obj.name
    print(f"当前选中的mesh是 {ObjName} ")
    for slot in obj.material_slots:  
        if slot.material:  
            for node in slot.material.node_tree.nodes:  
                change_image_source_to_generated(node) 
    # 开始烘焙  
    bakeImageSize = getBakeSize()
    print(f"对象 {bakeImageSize} 图片大小")
    try:
        bpy.ops.object.bake(save_mode='EXTERNAL',type='COMBINED')  
        # 保存烘焙后的图像  
        saveBakeImge(bakeImageSize,output_folder,ObjName)
    except Exception as e:
        print(f"烘焙错误对象: {obj.name}") 
        error_objects.append(obj.name)
    # 计算单张渲染时间   
    soloend_time = time.time()
    solorender_time = soloend_time - solostart_time 
    print(f"单张用时: {solorender_time:.2f} 秒")
    # 取消选中当前物体，为下一个物体做准备  
    obj.select_set(False)  
    # 返回捕捉错误对象
    return error_objects

#--------------------------删除材质--------------------------
def process_materials(obj):
    # 遍历所有的材质槽
    for slot in obj.material_slots:
        # 获取当前材质
        material = slot.material
        if material:
            # 如果材质名不包含"transparent"和"glass"，则删除该材质槽
            if "transparent" not in material.name.lower() and "glass" not in material.name.lower():
                bpy.data.materials.remove(material)

    # 创建一个新的材质
    new_material = bpy.data.materials.new(name=obj.name + "_mt")
    # 将新材质插入到第一个位置
    if obj.material_slots:
        obj.material_slots[0].material = new_material
    else:
        obj.data.materials.append(new_material)
#--------------------------删除UV--------------------------
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

#--------------------------删除增加节点--------------------------
def UpdateNode(iniass):
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
    # 从 iniass 列表中获取 Rate
    Rate = iniass[6]
    print(f"Rate:{Rate}")

    # 定义图像名称和对应的尺寸
    image_sizes = {
        "bake512": 512,
        "bake1024": 1024,
        "bake2048": 2048,
        "bake4096": 4096
    }

    # 遍历图像名称和尺寸，创建新图像
    for image_name, size in image_sizes.items():
        if image_name not in bpy.data.images:
            chicun = int(size * Rate)
            bpy.ops.image.new(name=image_name, width=chicun, height=chicun)


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

#--------------------------烘焙前操作--------------------------
def readyBake(context,auto):
    global error_objects
    error_objects = []  # 用于存储出错物体的名称  
    iniass = render_set(context) # 渲染设置
    UpdateNode(iniass) # 更新节点
    output_folder = OSoutput()
    print("输出路径:" + output_folder)
    # 记录结束时间  
    start_time = time.time()   
    if auto:
        autoRender(output_folder)
    else:
        manualRender(output_folder)

    # 完成后取消所有物体的选中状态  
    bpy.ops.object.select_all(action='DESELECT')
    # 记录结束时间  
    end_time = time.time()  
    # 计算渲染时间（秒）  
    render_time = end_time - start_time 
    print("所有对象渲染完毕: {:.2f} 分钟".format(render_time / 60),"错误数量为:",str(len(error_objects)))
#--------------------------自动烘焙--------------------------
def autoRender(output_folder):
    SCenemesh = 0 #场景模型数量
    i = 0 #计数
    for obj in bpy.context.scene.objects:   #统计所有数量
        if obj.type == 'MESH':  
            SCenemesh = SCenemesh + 1       
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            i = i + 1
            # 如果是网格遍历,获取错误对象
            Bakeing(obj,output_folder,error_objects)
            print("进度:["+str(i)+"/"+str(SCenemesh)+"]")  
        else:  
            print(f"选中的不是网格 {obj.name}")

#--------------------------手动烘焙--------------------------
def manualRender(output_folder):
    i = 0 #计数
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:   
        if obj.type == 'MESH':
            i = i + 1
            # 如果是网格遍历,获取错误对象
            Bakeing(obj,output_folder,error_objects)
            print("进度:["+str(i)+"/"+str(len(selected_objects))+"]") 
        else:  
            print(f"选中的不是网格 {obj.name}")

#--------------------------软装合并--------------------------
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

def check_collection_existence(collection_name):
    for collection in bpy.data.collections:
        if collection.name == collection_name:
            return True
    return False

# 创建名为“软装”的集合
def create_collection(collection_name):
    new_collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(new_collection)

    
def ruanCom():
    # 检查是否存在名为“软装”的集合
    bpy.ops.object.select_all(action='DESELECT')
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
                
                bpy.ops.object.select_all(action='DESELECT')

    # 调用函数以删除所有空对象
    delete_empty_objects()
#--------------------------硬装区分天墙地--------------------------
def yingCom(collection,collection_name):
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