from typing import Dict, Callable, Union
from enum import Enum

from glfw.GLFW import *

from .event_helper import InputEventHelper

class MouseEventType(Enum):
    ON_CLICK = 0
    ON_MOUSEDOWN = 1
    ON_MOUSEUP = 2

class MouseEventHelper():
    def __init__(self, input_event_helper:InputEventHelper) -> None:
        self.MOUSE_BUTTONS = [GLFW_MOUSE_BUTTON_LEFT, GLFW_MOUSE_BUTTON_RIGHT, GLFW_MOUSE_BUTTON_MIDDLE]
        self.event_helper = input_event_helper
        self.pressed_states = {mb: False for mb in self.MOUSE_BUTTONS}
        self.mouse_event_callbacks: Dict[int, Dict[MouseEventType, Union[Callable, None]]] = \
            {mb: {key: None for key in [k for k in MouseEventType]} for mb in self.MOUSE_BUTTONS}
        self.xpos = 0
        self.ypos = 0
        self.xstart = 0
        self.ystart = 0
        
        def cursor_pos_callback(window, xpos, ypos):
            self.xpos = xpos
            self.ypos = ypos
        
        def mouse_button_callback(window, button, action, mods):
            if action == GLFW_RELEASE:
                self.pressed_states[button] = False
                
                callback = self.mouse_event_callbacks[button][MouseEventType.ON_MOUSEUP]
                if callback is not None:
                    callback(self.xpos, self.ypos)
            
            if action == GLFW_PRESS:
                self.pressed_states[button] = True
                self.xstart, self.ystart = glfwGetCursorPos(window)
                
                callback = self.mouse_event_callbacks[button][MouseEventType.ON_CLICK]
                if callback is not None:
                    callback(self.xpos, self.ypos)
                    
        self.event_helper.set_cursor_pos_event(cursor_pos_callback)
        self.event_helper.set_mouse_button_event(mouse_button_callback)
        
    # needs to be called for every drawing loop
    def update_state(self):
        for key, value in self.pressed_states.items():
            if value:
                callback = self.mouse_event_callbacks[key][MouseEventType.ON_MOUSEDOWN]
                if callback is not None:
                    callback(self.xpos - self.xstart, self.ystart - self.ypos)
                    
    def set_callback(self, button, event_type, callback):
        self.mouse_event_callbacks[button][event_type] = callback