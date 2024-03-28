import bpy

# 自定义面板
class SimpleCustomPanel(bpy.types.Panel):
    bl_label = "Simple Panel"  # 面板的名称
    bl_idname = "PT_CustomPanel"
    bl_space_type = 'VIEW_3D'  # 面板所在区域
    bl_region_type = 'UI'  # 面板所在区域的类型
    bl_category = 'Tools'  # 面板所属的类别

    # 绘制面板内容
    def draw(self, context):
        layout = self.layout

        # 添加一个布尔属性
        layout.prop(context.scene, "my_bool_prop", text="单选框标签")

# 注册插件
def register():
    bpy.utils.register_class(SimpleCustomPanel)
    bpy.types.Scene.my_bool_prop = bpy.props.BoolProperty(name="my_bool_prop", description="这是一个布尔属性", default=False)

    # 调用单选框并检查其状态
    if bpy.context.scene.my_bool_prop:
        print("单选框已勾选")
    else:
        print("单选框未勾选")

# 注销插件
def unregister():
    bpy.utils.unregister_class(SimpleCustomPanel)
    del bpy.types.Scene.my_bool_prop

if __name__ == "__main__":
    register()
