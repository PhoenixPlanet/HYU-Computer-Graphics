from __future__ import annotations

from enum import Enum
from typing import Dict, List, Union, Callable, Generator, Optional, Any

from OpenGL.GL import *
from glfw.GLFW import *
import glm

import numpy as np

from ..shader import frame_shader, phong_shader
from ..object import ShaderType
from .camera import CameraHelper
from ..event import InputEventHelper, MouseEventHelper, MouseEventType, EventType
from .screen import Screen
from .render_manager import RenderManager
from ..context import ContextMode, ContextBase


class GraphicsManager():
    def __init__(self, width, height, title, framerate=30) -> None:
        self.window_width = width
        self.window_height = height
        self.window_title = title
        
        self.screen = Screen(width, height)
        
        self.camera = CameraHelper()
        self.camera.change_elevation(45)
        self.camera.change_azimuth(45)
        self.camera.change_radius(10)
        
        self.time:float = 0
        self.timestamp_for_frame = 0
        self.frame = framerate
        
        self.window = None
        self.init_glfw()
        
        self.bind_event_callback()
        
        self.renderer = RenderManager(
            {
                ShaderType.BASIC: frame_shader,
                ShaderType.PHONG: phong_shader
            }, 
            self.screen, 
            self.camera
        )
        self.renderer.init_renderer()
        
        self.context_mode = ContextMode.SINGLE
        
    
    def init_glfw(self):
        # Initialize GLFW
        if not glfwInit():
            raise Exception('glfwInit has failed')
        
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)   # OpenGL 3.3
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE) # for macOS

        # create a window and OpenGL context
        self.window = glfwCreateWindow(self.window_width, self.window_height, self.window_title, None, None)
        if not self.window:
            glfwTerminate()
            raise Exception('window has not created')
        
        glfwMakeContextCurrent(self.window)
        
        
    def bind_event_callback(self):
        # Initialize Event Helper Class
        self.event_helper = InputEventHelper(self.window)        

        # Set callback functions for keboard input
        def key_callback(window, key, scancode, action, mods):
            if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
                glfwSetWindowShouldClose(window, GLFW_TRUE)
            
            if key==GLFW_KEY_V and action==GLFW_PRESS:
                self.screen.toggle_projection_type()
                
            if key==GLFW_KEY_Z and action==GLFW_PRESS:
                self.renderer.toggle_polygon_mode()
                
            if key==GLFW_KEY_H and action==GLFW_PRESS:
                self.set_hierarchy_mode()
        
        # Set callback functions for mouse input (for camera moving)
        def scroll_callback(window, xoffset, yoffset):
            self.camera.change_radius(-yoffset/30)
                
        self.event_helper.set_keyboard_event(key_callback)
        self.event_helper.set_mouse_scroll_event(scroll_callback)
        
        self.mouse_helper = MouseEventHelper(self.event_helper)
        
        def on_left_mouse_callback(xoffset, yoffset):
            multiple = 50
            azimuth = xoffset / self.window_width * multiple
            elevation = yoffset / self.window_height * multiple
            self.camera.change_angle_by_base(-azimuth, elevation)
            
        def on_right_mouse_callback(xoffset, yoffset):
            multiple = 1
            pan_u = xoffset / self.window_width * multiple
            pan_v = yoffset / self.window_height * multiple
            self.camera.pan_by_base(pan_u, -pan_v)
            
        def set_base(xpos, ypos):
            self.camera.set_move_base()
            
        self.mouse_helper.set_callback(GLFW_MOUSE_BUTTON_LEFT, MouseEventType.ON_MOUSEDOWN, on_left_mouse_callback)
        self.mouse_helper.set_callback(GLFW_MOUSE_BUTTON_RIGHT, MouseEventType.ON_MOUSEDOWN, on_right_mouse_callback)
        self.mouse_helper.set_callback(GLFW_MOUSE_BUTTON_LEFT, MouseEventType.ON_CLICK, set_base)
        self.mouse_helper.set_callback(GLFW_MOUSE_BUTTON_RIGHT, MouseEventType.ON_CLICK, set_base)
        
        # Set callback functions for screen size
        self.event_helper.set_frame_buffer_size_event(self.screen.on_viewport_size_change)
        
    
    def set_single_mode(self):
        if self.context_mode == ContextMode.HIEARARCHI:
            self.context_mode = ContextMode.SINGLE
            
    def set_hierarchy_mode(self):
        if self.context_mode == ContextMode.SINGLE:
            self.context_mode = ContextMode.HIEARARCHI
    
            
    def _pre_update(self):
        """Update states of all components in Graphics manager 
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        
        # update event helper
        self.mouse_helper.update_state()
        
        
    def _post_update(self):
        # swap front and back buffers
        glfwSwapBuffers(self.window)

        # poll events
        glfwPollEvents()
        
    
    def run(self, context: ContextBase):
        while not glfwWindowShouldClose(self.window):
            self._pre_update()
            
            context.pre_update()
            
            self.time = glfwGetTime()
            if self.timestamp_for_frame + (1 / self.frame) <= self.time:
                self.timestamp_for_frame = self.time
                context.fixed_update()
            
            context.update()
            
            context.coroutine_update()
            
            context.post_update()
            
            self._post_update()
    
    def exit(self):
        glfwTerminate()