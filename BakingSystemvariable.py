import os
import ctypes
import subprocess
import bpy
from .quality import *
import time
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