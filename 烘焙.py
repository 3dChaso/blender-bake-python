


# 确保至少有一个物体被选中
if len(bpy.context.selected_objects) == 0:
    bpy.context.scene.objects[0].select_set(True)

# 遍历场景中所有模型进行烘焙
bpy.ops.object.select_all(action='DESELECT')
objects_to_bake = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
total_objects = len(objects_to_bake)

for index, obj in enumerate(objects_to_bake, start=1):
    # 选择当前模型
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # 烘焙 UV
    bpy.ops.object.bake(type='DIFFUSE')
    
    # 保存烘焙图像
    image_name = obj.name + ".png"
    image_path = os.path.join(bake_temp_dir, image_name)
    bpy.data.images['Render Result'].save_render(filepath=image_path)
    print("Baked image saved for", obj.name, "at", image_path)

    # 更新进度条
    bpy.context.window_manager.progress_update(index / total_objects * 100)

    # 检查是否取消操作
    if bpy.context.window_manager.progress_cancel:
        print("Baking process cancelled.")
        break

print("Baking completed!")



import bpy  
import os  
  
# 设置烘焙结果的保存目录  
bake_temp_dir = r"D:\bakeTemp"  
if not os.path.exists(bake_temp_dir):  
    os.makedirs(bake_temp_dir)  
  
def get_active_image_texture_name(material):  
    """  
    获取材质中活动节点使用的图片资源名。  
    假设活动节点是ShaderNodeTexImage。  
    """  
    if not material.node_tree:  
        return None  
      
    # 获取材质的活动节点  
    active_node = material.node_tree.nodes.active  
    if not active_node or not isinstance(active_node, bpy.types.ShaderNodeTexImage):  
        return None  
      
    # 获取图片资源名  
    image = active_node.image  
    if image:  
        return image.name  
    return None  
def main():  
    # 获取选中的对象  
    selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']  
    if not selected_objects:  
        print("没有选中任何网格对象。")  
        return  
      
    # 遍历选中对象的材质  
    for obj in selected_objects:  
        for slot in obj.material_slots:  
            material = slot.material  
            if material:  
                image_name = get_active_image_texture_name(material)  
                if image_name:  
                    print(f"对象 {obj.name} 的材质 {material.name} 中活动节点使用的图片资源名为: {image_name}")  
                else:  
                    print(f"对象 {obj.name} 的材质 {material.name} 没有找到使用图片资源的活动节点。") 
# 遍历场景中的所有网格物体  
for obj in bpy.data.objects:  
    if obj.type == 'MESH':  
        # 选中对象
        obj.select_set(True)
        # 开始烘焙  
        bpy.ops.object.bake(save_mode='EXTERNAL', use_cage=False)  
            
        # 保存烘焙后的图像  
        image_path = os.path.join(bake_temp_dir, f"{obj.name}_bake.png")  
        # bake_image.save_as(filepath=image_path, check_existing=True, relative_path=False)  
        # print(f"Saved baked image to {image_path}")  

        # 取消选中当前物体，为下一个物体做准备  
        obj.select_set(False)  

    else:  
        print(f"Skipping non-mesh object {obj.name}")  
  
# 完成后取消所有物体的选中状态  
bpy.ops.object.select_all(action='DESELECT')




import bpy  
import os  
  
def save_image_resource(image_name, output_folder):  
    """  
    将指定的图片资源另存为新的文件。  
      
    参数:  
    image_name -- 图片资源的名称  
    output_folder -- 图片保存的路径  
    """  
    # 确保输出文件夹存在  
    if not os.path.exists(output_folder):  
        os.makedirs(output_folder)  
      
    # 查找名为image_name的图片资源  
    for image in bpy.data.images:  
        if image.name == image_name:  
            # 构造完整的图片路径  
            file_path = os.path.join(output_folder, f"{image_name}.png")  
              
            # 另存图片资源到文件  
            image.save_as(filepath=file_path)  
            print(f"图片资源 {image_name} 已另存为: {file_path}")  
            return  
      
    print(f"未找到名为 {image_name} 的图片资源。")  
  
# 设置图片资源名和输出文件夹  
image_name = "bake1024"  
output_folder = r"D:\bakeTemp"  
  
# 调用函数另存图片资源  
save_image_resource(image_name, output_folder)




import bpy  
import os  
  
def save_image_resource(image_name, output_folder):  
    """  
    将指定的图片资源另存为新的文件。  
      
    参数:  
    image_name -- 图片资源的名称  
    output_folder -- 图片保存的路径  
    """  
    # 确保输出文件夹存在  
    if not os.path.exists(output_folder):  
        os.makedirs(output_folder)  
      
    # 查找名为image_name的图片资源  
    for image in bpy.data.images:  
        if image.name == image_name:  
            # 构造完整的图片路径  
            file_path = os.path.join(output_folder, f"{image_name}.png")  
              
            # 另存图片资源到文件  
            image.filepath_raw = file_path  
            image.save()  
            print(f"图片资源 {image_name} 已另存为: {file_path}")  
            return  
      
    print(f"未找到名为 {image_name} 的图片资源。")  
  
# 设置图片资源名和输出文件夹  
image_name = "bake1024"  
output_folder = r"D:\bakeTemp"  
  
# 调用函数另存图片资源  
save_image_resource(image_name, output_folder)




bpy.ops.image.save_as(save_as_render=False, filepath="//..\\..\\temp\\bake4096.png", relative_path=True, show_multiview=False, use_multiview=False)
bpy.ops.image.save_as(save_as_render=True, filepath="//..\\..\\temp\\bake4096.png", show_multiview=False, use_multiview=False)
