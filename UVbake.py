import bpy
import os
# 设置渲染引擎为 Cycles
bpy.context.scene.render.engine = 'CYCLES'

# 设置渲染设备为 GPU
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
#bpy.context.preferences.addons['cycles'].preferences.devices[0].use = True

# 设置渲染参数
bpy.context.scene.cycles.samples = 64
bpy.context.scene.cycles.preview_samples = 64
bpy.context.scene.cycles.use_denoising = False
bpy.context.scene.cycles.preview_denoising = False
bpy.context.scene.cycles.seed = 0
bpy.context.scene.cycles.blur_glossy = 0.1
# 检查并创建目录
def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
# 创建 bakeTemp 文件夹在 d 盘
bake_temp_dir = "D:/bakeTemp"
create_directory_if_not_exists(bake_temp_dir)

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

output_folder = r"D:\bakeTemp"  
# 遍历场景中的所有网格物体  

def saveBakeImge(image_name, output_folder,ObjName):  
    # 确保输出文件夹存在  
    if not os.path.exists(output_folder):  
        os.makedirs(output_folder)  
      
    # 查找名为image_name的图片资源  
    for image in bpy.data.images:  
        if image.name == image_name:  
            # 构造完整的图片路径  
            file_path = os.path.join(output_folder, f"{ObjName}.png")  
              
            # 另存图片资源到文件  
            image.filepath_raw = file_path  
            image.save()  
            print(f"图片资源 {image_name} 已另存为: {file_path}")  
            return  
      
    print(f"未找到名为 {image_name} 的图片资源。")  


for obj in bpy.data.objects:  
    if obj.type == 'MESH':  
        selected_objects = bpy.context.selected_objects  
        for obj in selected_objects:  
            obj.select_set(False)
        # 选中对象
        obj.select_set(True)
        ObjName = obj.name
        
  

        # 开始烘焙  
        bakeImageSize = getBakeSize()
        print(f"对象 {bakeImageSize} 图片大小")
        bpy.ops.object.bake(save_mode='EXTERNAL', use_cage=False)  
        # 保存烘焙后的图像  
        saveBakeImge(bakeImageSize,output_folder,ObjName)
        #image_path = os.path.join(bake_temp_dir, f"{obj.name}_bake.png")  
        # bake_image.save_as(filepath=image_path, check_existing=True, relative_path=False)  
        # print(f"Saved baked image to {image_path}")  

        # 取消选中当前物体，为下一个物体做准备  
        obj.select_set(False)  

    else:  
        print(f"Skipping non-mesh object {obj.name}")    
# 完成后取消所有物体的选中状态  
bpy.ops.object.select_all(action='DESELECT')
