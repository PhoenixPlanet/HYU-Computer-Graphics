import os
from typing import TYPE_CHECKING
from enum import Enum

from glfw.GLFW import *

from ..core import GraphicsManager
from ..context import ContextBase
from ..object import BaseObject, VertexObjectHelper
from ..struct import Vec3D
from ..event import EventType
from .bvh_loader import BVHLoader
from .bvh_enum import BVHRenderMode

class BVHContext(ContextBase):
    def __init__(self, manager: GraphicsManager) -> None:
        super().__init__(manager)
        self.grid_obj = BaseObject("grid", self, VertexObjectHelper.gridline(Vec3D(0, 1, 0), 20, 20, 1, False))
        
        self.cur_frame = 0
        self.play_anim = False
        
        self.anim_info = None
        self.render_mode = BVHRenderMode.LINE
        
        self.manager.event_helper.set_drag_drop_event(self.bvh_file_load_on_dragdrop)
        self.manager.event_helper.add_callback(EventType.KEYBOARD, self.print_hierarchy_on_p)
        self.manager.event_helper.add_callback(EventType.KEYBOARD, self.start_anim_on_space)
        self.manager.event_helper.add_callback(EventType.KEYBOARD, self.toggle_render_mode)
    
    def bvh_file_load_on_dragdrop(self, window, file_paths):
        self.anim_info = BVHLoader.parse_bvh_file(file_paths[0], self)
        self.set_object(self.anim_info.bvh_objects[0])
        self.set_frame_rate(1 / self.anim_info.frame_time)
        self.stop_anim()
    
    def print_hierarchy_on_p(self, window, key, scancode, action, mods):
        if key==GLFW_KEY_P and action==GLFW_PRESS:
            self.print_hierarchy()
            
    def start_anim_on_space(self, window, key, scancode, action, mods):
        if key==GLFW_KEY_SPACE and action==GLFW_PRESS:
            if self.play_anim:
                self.stop_anim()
            else:
                self.start_anim()
                
    def toggle_render_mode(self, window, key, scancode, action, mods):
        if key==GLFW_KEY_1 and action==GLFW_PRESS:
            self.render_mode = BVHRenderMode.LINE
            
        if key==GLFW_KEY_2 and action==GLFW_PRESS:
            self.render_mode = BVHRenderMode.BOX
            
    def start_anim(self):
        if self.anim_info is not None:
            self.cur_frame = 0
            self.play_anim = True
        
    def stop_anim(self):
        self.cur_frame = 0
        self.play_anim = False
        
    def fixed_update(self):
        if self.play_anim and self.anim_info is not None:
            self.cur_frame = self.cur_frame + 1
            
            if (self.cur_frame > self.anim_info.frames):
                self.cur_frame = 1
        
        super().fixed_update()
        
    def update(self):
        super().update()
        
        self.draw(self.grid_obj)