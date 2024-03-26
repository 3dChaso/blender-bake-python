import bpy

bl_info = {
    "name": "烘焙功能菜单",        # 插件名称
    "author": "王思",        # 作者名称
    "version": (0, 1, 6),                # 插件版本号
    "blender": (3, 6, 0),                # Blender 软件最低版本要求
    "location": "Blender插件框架",                # 位置信息
    "description": "洞窝blender烘焙脚本开发",                # 插件描述
    "doc_url": "https://www.baidu.com",        # 插件文档链接
    "tracker_url": "https://www.baidu.com",        # 报告问题链接
    "category": "View",            # 插件分类
} 
#bl_idname 必须 xx.xx 的格式，否则会报错。execute() 函数中可以执行自定义指令。
# 定义一个操作类
# 第一个按钮的操作类
class CustomOperator1(bpy.types.Operator):
    bl_idname = "custom.operator1"  # 操作的唯一标识符
    bl_label = "Custom Operator 1"   # 操作的名称
    bl_description = "搜索工程中是否有“bake”的图像资源,如果不存在则创建一个,创建的节点bakeNode并激活"
    def execute(self, context):
        # 图像资源名称
        image_name = "bake"
        if image_name not in bpy.data.images:
            bpy.ops.image.new(name=image_name, width=4096, height=4096)
         # 获取场景中所有的材质
        materials = bpy.data.materials
        # 循环遍历所有的材质
        for material in materials:
            # 创建一个新的节点树
            material.use_nodes = True
            node_tree = material.node_tree
            
            # 检查是否已经存在名为“bakeNode”的节点
            bake_node = node_tree.nodes.get("bakeNode")
            
            if not bake_node:
                # 创建一个新的图像纹理节点
                texture_node = node_tree.nodes.new('ShaderNodeTexImage')
                
                # 将新创建的节点命名为“bakeNode”
                texture_node.name = "bakeNode"

                # 获取图像资源
                image = bpy.data.images.get(image_name)
                if image:
                    # 设置图像节点的图像
                    texture_node.image = image
                    
                    # 激活节点
                    node_tree.nodes.active = texture_node
        print("Custom Operator 2 executed")
        return {'FINISHED'}
# 第二个按钮的操作类
class CustomOperator2(bpy.types.Operator):
    bl_idname = "custom.operator2"  # 操作的唯一标识符
    bl_label = "Custom Operator 2"   # 操作的名称
    bl_description = "删除工程中bakeNode节点"
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
        # 在这里编写第二个按钮的操作逻辑
        print("Custom Operator 2 executed")
        return {'FINISHED'}

# 第三个按钮的操作类
class CustomOperator3(bpy.types.Operator):
    bl_idname = "custom.operator3"  # 操作的唯一标识符
    bl_label = "Custom Operator 3"   # 操作的名称
    bl_description = "遍历所有对象,合并它的子级并解除父级"

    def execute(self, context):
        def merge_meshes_and_clear_parent(obj):
            # 如果对象没有子级，则直接返回
            if not obj.children:
                return
            # 获取子级中的所有网格对象
            meshes = [child for child in obj.children if child.type == 'MESH']
            # 如果没有网格对象，则遍历下一个对象
            if not meshes:
                return
            # 如果只有一个网格对象，则清除父级并保持变换结果
            if len(meshes) == 1:
                mesh = meshes[0]
                #mesh.matrix_world = obj.matrix_world @ mesh.matrix_world  # 应用父级的变换
                bpy.ops.object.select_all(action='DESELECT')
                mesh.select_set(True)
                bpy.context.view_layer.objects.active = mesh
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')  # 清除父级并保持变换结果
                return
            # 如果有多个网格对象，则合并网格并清除父级
            bpy.ops.object.select_all(action='DESELECT')
            for mesh in meshes:
                mesh.select_set(True)
                # mesh.matrix_world = obj.matrix_world @ mesh.matrix_world  # 应用父级的变换
            bpy.context.view_layer.objects.active = meshes[0]
            bpy.ops.object.join()
            bpy.context.active_object.parent = None  # 清除父级
        # 遍历场景中的所有对象
        for obj in bpy.context.scene.objects:
            merge_meshes_and_clear_parent(obj)
        # 在这里编写第三个按钮的操作逻辑
        print("Custom Operator 3 executed")
        return {'FINISHED'}
# 第四个按钮的操作类
class CustomOperator4(bpy.types.Operator):
    bl_idname = "custom.operator4"  # 操作的唯一标识符
    bl_label = "Custom Operator 4"   # 操作的名称
    bl_description = "遍历所有对象,删除第二个和后面所有的UV"
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

        # 执行函数以删除第二个及其后的所有 UV 图层
        remove_second_and_subsequent_uv()
        print("Custom Operator 4 executed")
        return {'FINISHED'}
# 第五个按钮的操作类
class CustomOperator5(bpy.types.Operator):
    bl_idname = "custom.operator5"  # 操作的唯一标识符
    bl_label = "Custom Operator 5"   # 操作的名称
    bl_description = "将选中的对象添加bakeUV"
    def execute(self, context):
        # 在这里编写第三个按钮的操作逻辑
# 获取当前场景
        scene = bpy.context.scene

        # 获取当前选中的对象
        selected_objects = bpy.context.selected_objects

        # 遍历每个选中的对象
        for obj in selected_objects:
            # 检查对象是否是网格对象
            if obj.type == 'MESH':
                # 创建一个新的 UV 贴图
                uv_layer = obj.data.uv_layers.new(name="bakeUV")
                # 选择第二个 UV 图层
                obj.data.uv_layers.active_index = 1
            else:
                print("对象", obj.name, "不是网格对象，无法添加 UV 贴图。")
        # 提示用户操作完成
        print("已添加名为 'bakeUV' 的新 UV 贴图，并选择第二个 UV 图层。")
        print("Custom Operator 5 executed")
        return {'FINISHED'}
# 第六个按钮的操作类
class CustomOperator6(bpy.types.Operator):
    bl_idname = "custom.operator6"  # 操作的唯一标识符
    bl_label = "Custom Operator 6"   # 操作的名称

    def execute(self, context):
        # 在这里编写第三个按钮的操作逻辑
        print("Custom Operator 6 executed")
        return {'FINISHED'}
# 第七个按钮的操作类
class CustomOperator7(bpy.types.Operator):
    bl_idname = "custom.operator7"  # 操作的唯一标识符
    bl_label = "Custom Operator 7"   # 操作的名称

    def execute(self, context):
        # 在这里编写第三个按钮的操作逻辑
        print("Custom Operator 7 executed")
        return {'FINISHED'}
# 定义一个面板类
class CustomPanel(bpy.types.Panel):
    bl_idname = "烘焙菜单面板"  # 面板的唯一标识符
    bl_label = "功能集合"      # 面板的名称
    bl_space_type = 'VIEW_3D'      # 面板所在的区域
    bl_region_type = 'UI'          # 面板所在的区域类型
    bl_category = '洞窝blender烘焙菜单'   # 面板所在的类别

    def draw(self, context):
        layout = self.layout
        # 添加按钮到面板中，并为每个按钮指定相应的操作
        layout.operator("custom.operator1", text="添加bakeNode节点")
        layout.operator("custom.operator2", text="删除bakeNode节点")
        layout.operator("custom.operator3", text="合并同父网格")
        layout.operator("custom.operator4", text="删除第二UV")
        layout.operator("custom.operator5", text="添加bakeUV")
        layout.operator("custom.operator6", text="暂存")
        layout.operator("custom.operator7", text="暂存")

# 注册操作和面板类
def register():
    bpy.utils.register_class(CustomOperator1)
    bpy.utils.register_class(CustomOperator2)
    bpy.utils.register_class(CustomOperator3)
    bpy.utils.register_class(CustomOperator4)
    bpy.utils.register_class(CustomOperator5)
    bpy.utils.register_class(CustomOperator6)
    bpy.utils.register_class(CustomOperator7)
    bpy.utils.register_class(CustomPanel)

# 注销操作和面板类
def unregister():
    bpy.utils.unregister_class(CustomOperator1)
    bpy.utils.unregister_class(CustomOperator2)
    bpy.utils.unregister_class(CustomOperator3)
    bpy.utils.unregister_class(CustomOperator4)
    bpy.utils.unregister_class(CustomOperator5)
    bpy.utils.unregister_class(CustomOperator6)
    bpy.utils.unregister_class(CustomOperator7)
    bpy.utils.unregister_class(CustomPanel)

# 测试代码
if __name__ == "__main__":
    register()
