import bpy  
import os  
  
# 设置目标目录和文件名  
target_directory = r"D:\bakeTemp"  
filename = "test.png"  
  
# 确保目标目录存在  
if not os.path.exists(target_directory):  
    os.makedirs(target_directory)  
  
# 构建完整的文件路径  
full_path = os.path.join(target_directory, filename)  
  
# 设置渲染图像的文件路径  
bpy.data.images["bake1024"].filepath_raw = full_path  
  
# 设置另存为渲染图  
bpy.data.images["bake1024"].save_render = True  
  
# 色彩管理跟随场景  
bpy.data.images["bake1024"].use_scene_color_management = True  
  
# 保存图像  
bpy.data.images["bake1024"].save()  
  
print(f"Image saved to: {full_path}")






import bpy
from bpy_extras.io_utils import unpack_list

# 获取当前场景中的所有图像
images = bpy.data.images

# 遍历所有图像，查找名称为“bake1024”的图像
target_image = None
for img in images:
    if img.name == "bake1024":
        target_image = img
        break

# 如果找到目标图像，则执行保存和设置色彩空间操作
if target_image is not None:
    # 保存图像到指定路径
    target_image.save_render("D:/temp/image.png")
    
    # 设置色彩空间为“AgX Base sRGB”
    target_image.colorspace_settings.name = 'AgX Base sRGB'
    print("图像已保存并色彩空间已设置为 'AgX Base sRGB'")
else:
    print("未找到名称为 'bake1024' 的图像")



import bpy  
  
# 检查是否存在名为"test"的对象  
obj = bpy.data.objects.get("test")  
  

obj.bake(type='COMBINED', filepath='D:/image11.png', width=512, height=512, margin=16, margin_type='EXTEND', use_selected_to_active=False, save_mode='INTERNAL', use_clear=True, use_cage=False)  
    obj.select_set(True)  
      
    # 设置视图为选中的对象  
    bpy.context.view_layer.objects.active = obj  
    print("Object 'test' selected and set as active.")  
else:  
    print("Object 'test' not found in the scene.")




# 获取当前选中的对象列表  
selected_objects = bpy.context.selected_objects  
  
# 遍历选中的对象并打印它们的名称  
for obj in selected_objects:  
    obj.bake(save_mode='EXTERNAL',type='COMBINED', filepath='D:/image11.png', width=512, height=512, margin=16, margin_type='EXTEND', use_selected_to_active=False, save_mode='INTERNAL', use_clear=True, use_cage=False)