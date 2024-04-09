import bpy
from .BakingSystemvariable import *
import os

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
# # 第一个按钮的操作类添加烘焙节点
# class CustomOperator1(bpy.types.Operator):
#     bl_idname = "custom.operator1"  # 操作的唯一标识符
#     bl_label = "Custom Operator 1"   # 操作的名称
#     bl_description = "根据模型面积添加烘焙节点使用对应大小图像"
#     def execute(self, context):
#         print("Custom Operator 2 executed")
#         return {'FINISHED'}
# # 第二个按钮的操作类删除节点
# class CustomOperator2(bpy.types.Operator):
#     bl_idname = "custom.operator2"  # 操作的唯一标识符
#     bl_label = "Custom Operator 2"   # 操作的名称
#     bl_description = "删除工程中bakeNode节点和图像资源"
#     def execute(self, context):

#         print("Custom Operator 2 executed")
#         return {'FINISHED'}

# 第三个按钮的操作类合并软装
# class CustomOperator3(bpy.types.Operator):
#     bl_idname = "custom.operator3"  # 操作的唯一标识符
#     bl_label = "Custom Operator 3"   # 操作的名称
#     bl_description = "遍历所有对象,合并它的子级并解除父级,注意不要放在合集里"
#     def execute(self, context):
#         return {'FINISHED'}
# 第四个按钮的操作类删除二UV
# class CustomOperator4(bpy.types.Operator):
#     bl_idname = "custom.operator4"  # 操作的唯一标识符
#     bl_label = "Custom Operator 4"   # 操作的名称
#     bl_description = "遍历所有对象,删除第二个和后面所有的UV,并添加bakeUV"
#     def execute(self, context):
#         # 执行函数以删除第二个及其后的所有 UV 图层
#         remove_second_and_subsequent_uv()
#         smartUV()

#         print("Custom Operator 4 executed")
#         return {'FINISHED'}
# 第五个按钮的操作类合并硬装
class CustomOperator5(bpy.types.Operator):
    bl_idname = "custom.operator5"  # 操作的唯一标识符
    bl_label = "Custom Operator 5"   # 操作的名称
    bl_description = "合并硬装的集合[硬装]天花板,墙,地板,合并软装到[软装],保存工程,优化UV,添加第二UV"
    def execute(self, context):
        OSoutput_folder = try_read_OS_Var()
        # 遍历名为“硬”的集合
        collection_name = "硬装"
        collection = bpy.data.collections.get(collection_name)
        projectName = get_design(context)
        collection["projectName"] = projectName
        print("方案名为 '%s' 记录在硬装合集自定义属性里" % projectName)
        #bpy.data.collections.get("硬装")["projectName"]
        # 硬装合并开始
        yingCom(collection,collection_name)
        print("硬装合并完毕")
        ruanCom()           
        print("软装合并完毕")
        remove_second_and_subsequent_uv()
        smartUV()
        savepath = OSoutput_folder + projectName+".blend"
        bpy.ops.wm.save_mainfile ( filepath = savepath )
        print(f"工程保持完毕:{savepath}")
        return {'FINISHED'}
# 第六个按钮的操作类优化材质
# class CustomOperator6(bpy.types.Operator):
#     bl_idname = "custom.operator6"  # 操作的唯一标识符
#     bl_label = "Custom Operator 6"   # 操作的名称
#     bl_description = "将所有对象的漫射材质删除，并新建一个漫射材质槽,导出一个fbx"
#     def execute(self, context):
        
#         return {'FINISHED'}
# 第七个按钮的操作类遍历烘焙
class CustomOperator7(bpy.types.Operator):
    bl_idname = "custom.operator7"  # 操作的唯一标识符
    bl_label = "Custom Operator 7"   # 操作的名称
    bl_description = "调整渲染设置,遍历渲染图片到D盘bakeTemp目录"
    def execute(self, context):
        readyBake(context,True)
        return {'FINISHED'}

# 第八个按钮的操作类手动烘焙
class CustomOperator8(bpy.types.Operator):
    bl_idname = "custom.operator8"  # 操作的唯一标识符
    bl_label = "Custom Operator 8"   # 操作的名称
    bl_description = "调整渲染设置,将选中对象渲染图片到D盘bakeTemp目录"
    def execute(self, context):
        readyBake(context,False)  
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
        layout.operator("custom.operator5", text="合并网格保存工程")
        # 添加一个布尔属性
        #layout.prop(context.scene, "my_bool_prop", text="合并时保持应用父级位置")
        # layout.operator("custom.operator3", text="软装合并网格")
        # layout.operator("custom.operator4", text="删除第二UV,添加bakeUV")
        # layout.operator("custom.operator1", text="添加bakeNode节点")
        # layout.operator("custom.operator2", text="删除bakeNode节点")
        layout.prop(context.scene, "my_bool_prop1", text="覆盖渲染设置")
        layout.operator("custom.operator7", text="开始遍历烘焙")
        layout.operator("custom.operator8", text="手动选择烘焙")
        # layout.operator("custom.operator6", text="优化材质导出FBX")
        layout.operator("custom.operator9", text="测试")
        layout.prop(context.scene, "my_value")
        

# 注册操作和面板类
def register():
    # bpy.utils.register_class(CustomOperator1)
    # bpy.utils.register_class(CustomOperator2)
    # bpy.utils.register_class(CustomOperator3)
    # bpy.utils.register_class(CustomOperator4)
    bpy.utils.register_class(CustomOperator5)
    # bpy.utils.register_class(CustomOperator6)
    bpy.utils.register_class(CustomOperator7)
    bpy.utils.register_class(CustomOperator8)
    bpy.utils.register_class(CustomOperator9)
    bpy.utils.register_class(CustomPanel)
    bpy.types.Scene.my_bool_prop1 = bpy.props.BoolProperty(
        name="my_bool_prop1", 
        description="是否覆盖当前场景的渲染设置",
        default=True)
    bpy.types.Scene.my_value = bpy.props.FloatProperty(
        name="渲染质量", default=3,
        description="设置渲染质量:3为最高,2为中等质量,1为低质量",
        min=0,
        max = 3)
    OSoutput_folder = try_read_OS_Var()
    if OSoutput_folder == None:
        print("全局路径读取失败,请以管理员身份启动该程序,或手动添加全局变量bakeTemp='D:\\bakeTemp\\'")
# 注销操作和面板类
def unregister():
    # bpy.utils.unregister_class(CustomOperator1)
    # bpy.utils.unregister_class(CustomOperator2)
    # bpy.utils.unregister_class(CustomOperator3)
    # bpy.utils.unregister_class(CustomOperator4)
    bpy.utils.unregister_class(CustomOperator5)
    # bpy.utils.unregister_class(CustomOperator6)
    bpy.utils.unregister_class(CustomOperator7)
    bpy.utils.unregister_class(CustomOperator8)
    bpy.utils.unregister_class(CustomOperator9)
    bpy.utils.unregister_class(CustomPanel)
    del bpy.types.Scene.my_bool_prop1
    del bpy.types.Scene.my_value

# 测试代码
if __name__ == "__main__":
    register()
