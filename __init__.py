import bpy
from .BakingSystemvariable import *
from math import inf
import time
import os
from .util import *
bl_info = {
    "name": "烘焙功能菜单",        # 插件名称
    "author": "王思",        # 作者名称
    "version": (0, 4, 1),                # 插件版本号
    "blender": (3, 6, 0),                # Blender 软件最低版本要求
    "location": "Blender插件框架",                # 位置信息
    "description": "洞窝blender烘焙脚本开发",                # 插件描述
    "doc_url": "https://www.baidu.com",        # 插件文档链接
    "tracker_url": "https://www.baidu.com",        # 报告问题链接
    "category": "View",            # 插件分类
} 
OSoutput_folder = ''
# 第一个按钮的操作类添加烘焙节点
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
        iniass = []
        # 图像资源名称
        iniass = render_set(context)
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
        print("Custom Operator 2 executed")
        return {'FINISHED'}
# 第二个按钮的操作类删除节点
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

# 第三个按钮的操作类合并软装
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
# 第四个按钮的操作类删除二UV
class CustomOperator4(bpy.types.Operator):
    bl_idname = "custom.operator4"  # 操作的唯一标识符
    bl_label = "Custom Operator 4"   # 操作的名称
    bl_description = "遍历所有对象,删除第二个和后面所有的UV,并添加bakeUV"
    def execute(self, context):
        # 执行函数以删除第二个及其后的所有 UV 图层
        remove_second_and_subsequent_uv()
        # 获取名为“硬装”的合集
        collection = bpy.data.collections.get("硬装")
        bpy.ops.object.mode_set(mode='OBJECT')
        if collection:
            # 获取默认的场景对象
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
# 第五个按钮的操作类合并硬装
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
# 第六个按钮的操作类优化材质
class CustomOperator6(bpy.types.Operator):
    bl_idname = "custom.operator6"  # 操作的唯一标识符
    bl_label = "Custom Operator 6"   # 操作的名称
    bl_description = "将所有对象的漫射材质删除，并新建一个漫射材质槽"
    
    def execute(self, context):
        # 遍历场景中所有的对象
        for obj in bpy.context.scene.objects:
            # 检查对象是否为网格对象
            if obj.type == 'MESH':
                # 执行处理材质的函数
                process_materials(obj)
        print("操作完成")
        return {'FINISHED'}
# 第七个按钮的操作类遍历烘焙
class CustomOperator7(bpy.types.Operator):
    bl_idname = "custom.operator7"  # 操作的唯一标识符
    bl_label = "Custom Operator 7"   # 操作的名称
    bl_description = "调整渲染设置,遍历渲染图片到D盘bakeTemp目录"
    def execute(self, context):
        global error_objects
        i = 0 #计数
        render_set(context) # 渲染设置
        output_folder = OSoutput()
        print("输出路径:" + output_folder)
        error_objects = []  # 用于存储出错物体的名称  
        # 记录结束时间  
        start_time = time.time()   
        SCenemesh = 0 #场景模型数量
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
        # 完成后取消所有物体的选中状态  
        bpy.ops.object.select_all(action='DESELECT')
        # 记录结束时间  
        end_time = time.time()  
        # 计算渲染时间（秒）  
        render_time = end_time - start_time 
        # 打印渲染时间
        print("所有对象渲染完毕: {:.2f} 分钟".format(render_time / 60),"错误数量为:",str(len(error_objects)))
        return {'FINISHED'}

# 第八个按钮的操作类手动烘焙
class CustomOperator8(bpy.types.Operator):
    bl_idname = "custom.operator8"  # 操作的唯一标识符
    bl_label = "Custom Operator 8"   # 操作的名称
    bl_description = "调整渲染设置,将选中对象渲染图片到D盘bakeTemp目录"
    def execute(self, context):
        global error_objects
        i = 0 #计数
        render_set(context) # 渲染设置
        output_folder = OSoutput()
        print("输出路径:" + output_folder)
        error_objects = []  # 用于存储出错物体的名称  
        start_time = time.time()   
        # 获取当前场景中选中的对象
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:   
            if obj.type == 'MESH':
                i = i + 1
                # 如果是网格遍历,获取错误对象
                Bakeing(obj,output_folder,error_objects)
                print("进度:["+str(i)+"/"+str(len(selected_objects))+"]") 
            else:  
                print(f"选中的不是网格 {obj.name}")
        # 完成后取消所有物体的选中状态  
        bpy.ops.object.select_all(action='DESELECT')
        # 记录结束时间  
        end_time = time.time()  
        # 计算渲染时间（秒）  
        render_time = end_time - start_time 
        # 打印渲染时间  
        print("所有对象渲染完毕: {:.2f} 分钟".format(render_time / 60),"错误数量为:",str(len(error_objects)))
        return {'FINISHED'}

# 第九个按钮的操作类测试
class CustomOperator9(bpy.types.Operator):
    bl_idname = "custom.operator9"  # 操作的唯一标识符
    bl_label = "Custom Operator 9"   # 操作的名称
    bl_description = "测试"
    def execute(self, context):
        # 读取系统变量
        path_value = os.getenv('CUDA_CACHE_MAXSIZE')
        print("baketemp:", path_value)
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
        layout.operator("custom.operator9", text="测试")
        layout.prop(context.scene, "my_value")
        

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
    bpy.utils.register_class(CustomOperator9)
    bpy.utils.register_class(CustomPanel)
    bpy.types.Scene.my_bool_prop1 = bpy.props.BoolProperty(name="my_bool_prop1", description="是否覆盖当前场景的渲染设置", default=True)
    bpy.types.Scene.my_value = bpy.props.FloatProperty(name="渲染质量", default=3,description="设置渲染质量:3为最高,2为中等质量,1为低质量",min=0,max = 3)
    OSoutput_folder = try_read_OS_Var()
    if OSoutput_folder == None:
        print("全局路径读取失败,请以管理员身份启动该程序,或手动添加全局变量bakeTemp='D:\\bakeTemp\\'")
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
    bpy.utils.unregister_class(CustomOperator9)
    bpy.utils.unregister_class(CustomPanel)
    del bpy.types.Scene.my_bool_prop1
    del bpy.types.Scene.my_value

# 测试代码
if __name__ == "__main__":
    register()
