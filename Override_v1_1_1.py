# https://blenderartists.org/t/overiding-context/549124/5
# https://b3d.interplanety.org/en/context-override/

import bpy
bl_info = {
    "name": "OVERRIDE",
    "author": "1C0D",  # thks to devtools addon, 3di & dr Sybren from blender chat
    "version": (1, 1, 1),
    "blender": (2, 93, 0),
    "location": "texteditor/console",
    "description": "OVERRIDE SCRIPT and console excecution",
    "category": "Developpement",
}


console = 0
active_text = None

def expanse(line):
    if "C" or "D" in line.startswith(("C","D")):
        line = line.replace("C", "bpy.context").replace("D", "bpy.data")
    return line

def printWrap(line):
    line=f"print({line})"
    return line

def selectline_copy_suppr(self,context): # get text in console
    # selectline
    sc = context.space_data
    line_object = sc.history[-1]
    if line_object:
        global line
        line = line_object.body
        line = expanse(line)
        if self.print:
            line = printWrap(line)

def del_temp_text():
    if "temp_text" in bpy.data.texts.keys():
        bpy.data.texts.remove(bpy.data.texts['temp_text'])


def create_text_active(context):
    global active_text
    global console

    param = get_area(context, 'TEXT_EDITOR')
    area=param[2]
    active_text = area.spaces[0].text
    del_temp_text() # clean up
    bpy.data.texts.new("temp_text") # create a text
    text = bpy.data.texts['temp_text']
    area.spaces[0].text = text # make it active

    new_context = override(context, *param)
    bpy.ops.text.insert(new_context, text='import bpy\n\n') #needed in text editor
    bpy.ops.text.insert(new_context, text=line)

    console = 1 #set the operator below to 1
    bpy.ops.text.override(new_context, "INVOKE_DEFAULT")


def get_area(context, area_type):
    for window in context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type != area_type:
                continue
            for region in area.regions:
                if region.type != 'WINDOW':
                    continue
                return window, screen, area, region


def override(context, *param):
    override = {'window': param[0], 'screen': param[1], 'area': param[2], 'region': param[3]}
    return {
        **context.copy(),
        **override,
    }


def clean_temp_text(area):
    del_temp_text()
    if console:
        area.spaces[0].text = active_text


class OVERRIDE_OT_console(bpy.types.Operator): 
    """Override context clicking on target area after this button
    you can wrap your command with a print pressing button+shift
        
    """
    bl_idname = "console.override"
    bl_label = "override console exe"
    bl_option = {'INTERNAL'}

    print : bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.shift:
            self.print = True

        return self.execute(context)

    def execute(self, context):
        selectline_copy_suppr(self, context)
        create_text_active(context)

        return {'FINISHED'}


class OVERRIDE_OT_text_editor(bpy.types.Operator): #run for console and text editor
    """Tooltip"""
    bl_idname = "text.override"
    bl_label = "override text editor script"
    bl_option = {'INTERNAL'}

    def invoke(self, context, event):            
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if event.type != 'LEFTMOUSE':
            return {'RUNNING_MODAL'}

        window = context.window
        screen = context.window.screen
        for area in screen.areas:
            if (area.x < event.mouse_x < area.x + area.width and area.y < event.mouse_y < area.y + area.height):
                for region in area.regions:
                    if region.type != 'WINDOW':
                        continue
                    param=(window, screen, area, region)
                    new_context = override(context, *param)
                    try:
                        bpy.ops.text.run_script(new_context)
                    except RuntimeError:
                        if console:
                            param = get_area(context, 'TEXT_EDITOR')
                            clean_temp_text(param[2])
                        self.report({'ERROR'}, "CONTEXT INCORRECT")

                        return {'CANCELLED'}                

        if console:
            param = get_area(context, 'TEXT_EDITOR')            
            clean_temp_text(param[2])

            param = get_area(context, 'CONSOLE')
            new_context = override(context, *param)
            self.report({'INFO'}, "EXECUTED! Check OS Console")

        return {'FINISHED'}


def draw(self, context):
    layout = self.layout
    layout.operator("text.override", text='', icon="DECORATE_DRIVER")


def draw1(self, context):
    layout = self.layout
    layout.operator("console.override", text='', icon="DECORATE_DRIVER")


def register():

    bpy.utils.register_class(OVERRIDE_OT_text_editor)
    bpy.utils.register_class(OVERRIDE_OT_console)
    bpy.types.TEXT_HT_header.prepend(draw)
    bpy.types.CONSOLE_HT_header.prepend(draw1)


def unregister():

    bpy.utils.unregister_class(OVERRIDE_OT_text_editor)
    bpy.utils.unregister_class(OVERRIDE_OT_console)
    bpy.types.TEXT_HT_header.remove(draw)
    bpy.types.CONSOLE_HT_header.remove(draw1)


if __name__ == "__main__":
    register()
