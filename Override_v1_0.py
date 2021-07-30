# https://blenderartists.org/t/overiding-context/549124/5
# https://b3d.interplanety.org/en/context-override/

import bpy
bl_info = {
    "name": "OVERRIDE",
    "author": "1C0D",  # thks to devtools addon, 3di & dr Sybren from blender chat
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "texteditor/console",
    "description": "OVERRIDE SCRIPT and console excecution",
    "category": "Developpement",
}

#todo transform C. in context. and D. in data 

console = 0
active_text = None


def selectline_copy_suppr(context): # get text in console
    # selectline
    sc = context.space_data
    line_object = sc.history[-1]
    if line_object:
        line = line_object.body
        lenght = len(line)
        st = sc.select_start = 0
        se = sc.select_end = lenght
    # copy
    bpy.ops.console.copy()  # to paste in the text editor
    # suppr
    bpy.ops.console.move(type='LINE_END')
    for _ in range(st):
        bpy.ops.console.move(type='PREVIOUS_CHARACTER')
    for _ in range(se-st):
        bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
    sc.select_start = st
    sc.select_end = st


def del_temp_text():
    if "temp_text" in bpy.data.texts.keys():
        bpy.data.texts.remove(bpy.data.texts['temp_text'])


def create_text_active(context):
    global active_text
    global console

    area = get_area(context, 'TEXT_EDITOR')
    active_text = area.spaces[0].text
    del_temp_text() # clean up
    bpy.data.texts.new("temp_text") # create a text
    text = bpy.data.texts['temp_text']
    area.spaces[0].text = text # make it active

    new_context = override(context, area)
    bpy.ops.text.insert(new_context, text='import bpy\n\n') #needed in text editor
    bpy.ops.text.paste(new_context)
    console = 1 #set the operator below to 1
    bpy.ops.text.override(new_context, "INVOKE_DEFAULT")


def get_area(context, area_type):
    for window in context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type != area_type:
                continue
            return area


def override(context, area):
    override = {'area': area}
    return {
        **context.copy(),
        **override,
    }


def clean_temp_text(area):
    del_temp_text()
    area.spaces[0].text = active_text


def console_result(context, new_context): #to generate a result message in console
    clip = context.window_manager.clipboard
    text = f"' {clip} '"
    bpy.ops.console.insert(new_context, text=text)
    bpy.ops.console.execute(new_context)


class OVERRIDE_OT_console(bpy.types.Operator): 
    """Tooltip"""
    bl_idname = "console.override"
    bl_label = "override console exe"

    def execute(self, context):
        selectline_copy_suppr(context)
        create_text_active(context)

        return {'FINISHED'}


class OVERRIDE_OT_text_editor(bpy.types.Operator): #run for console and text editor
    """Tooltip"""
    bl_idname = "text.override"
    bl_label = "override text editor script"

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
                new_context = override(context, area)
                try:
                    bpy.ops.text.run_script(new_context)
                except RuntimeError:
                    if console:
                        area = get_area(context, 'TEXT_EDITOR')
                        clean_temp_text(area)
                    self.report({'ERROR'}, "CONTEXT INCORRECT")

                    return {'CANCELLED'}

        if console:
            area = get_area(context, 'TEXT_EDITOR')
            clean_temp_text(area)

            area = get_area(context, 'CONSOLE')
            new_context = override(context, area)
            console_result(context, new_context)

        return {'FINISHED'}


def draw(self, context):
    layout = self.layout
    layout.operator("text.override", text='', icon="CONSOLE")


def draw1(self, context):
    layout = self.layout
    layout.operator("console.override", text='', icon="CONSOLE")


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
