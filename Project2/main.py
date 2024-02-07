import os

from glfw.GLFW import *

import utils
import objs

class MainContext(utils.ContextBase):
    def __init__(self, manager: utils.GraphicsManager) -> None:
        super().__init__(manager)
        self.grid_obj = utils.BaseObject("grid", self, utils.VertexObjectHelper.gridline(utils.Vec3D(0, 1, 0), 20, 20, 1, False))
        
        self.frame_obj = objs.FrameObj("frame", self)
        self.table = objs.Table("table", self)
        self.add_object(self.table)
        
        self.manager.event_helper.set_drag_drop_event(self.obj_file_load_on_dragdrop)
        self.manager.event_helper.add_callback(utils.EventType.KEYBOARD, self.print_hierarchy_on_click_p)
        
    def obj_file_load_on_dragdrop(self, window, file_paths):
        obj = self.get_obj_from_file(file_paths[0])
        self.set_single_mode_object(obj)
        self.set_single_mode()
        
    def get_obj_from_file(self, file_path):
        vertices = utils.VertexObjectHelper.from_obj_file(file_path)
        obj = utils.BaseObject(os.path.basename(file_path), self, vertices)
        return obj
    
    def print_hierarchy_on_click_p(self, window, key, scancode, action, mods):
        if key==GLFW_KEY_P and action==GLFW_PRESS:
            self.print_hierarchy()
        
    def update(self):
        super().update()
        
        self.draw(self.grid_obj)
        #self.draw(self.frame_obj)

def main():
    manager = utils.GraphicsManager(800, 800, "(2019039843)", 60)    
    
    main_context = MainContext(manager)
    
    manager.run(main_context)

    manager.exit()

if __name__ == "__main__":
    main()