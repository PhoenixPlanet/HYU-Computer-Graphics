from enum import Enum

from glfw.GLFW import *
        
        
class EventType(Enum):
    MOUSE_CURSOR_POS = 0
    MOUSE_BUTTON = 1
    MOUSE_SCROLL = 2
    KEYBOARD = 3
    DRAG_DROP = 4
    
        
class InputEventHelper():
    def __init__(self, window) -> None:
        self.glfw_window = window
        
        self.EVENT_ENABLE_FLAG = {key: False for key in [k for k in EventType]}
        self.EVENT_GLFW_CALLBACKS = {key: [] for key in [k for k in EventType]}
    
    def _set_event_flag(self, flag:EventType):
        self.EVENT_ENABLE_FLAG[flag] = True
        
    def add_callback(self, event_type, callback):
        self.EVENT_GLFW_CALLBACKS[event_type].append(callback)
    
    def _init_callback(self, event_type, callback):
        self._set_event_flag(event_type)
        self.add_callback(event_type, callback)
        
    def set_keyboard_event(self, callback):
        self._init_callback(EventType.KEYBOARD, callback)
        
        def keyboard_callback_caller(window, key, scancode, action, mods):
            for c in self.EVENT_GLFW_CALLBACKS[EventType.KEYBOARD]:
                c(window, key, scancode, action, mods)
                
        glfwSetKeyCallback(self.glfw_window, keyboard_callback_caller)
        
    def set_cursor_pos_event(self, callback):
        self._init_callback(EventType.MOUSE_CURSOR_POS, callback)
        
        def cursor_pos_callback_caller(window, xpos, ypos):
            for c in self.EVENT_GLFW_CALLBACKS[EventType.MOUSE_CURSOR_POS]:
                c(window, xpos, ypos)
                
        glfwSetCursorPosCallback(self.glfw_window, cursor_pos_callback_caller)
        
    def set_mouse_button_event(self, callback):
        self._init_callback(EventType.MOUSE_BUTTON, callback)
        
        def mouse_button_callback_caller(window, button, action, mods):
            for c in self.EVENT_GLFW_CALLBACKS[EventType.MOUSE_BUTTON]:
                c(window, button, action, mods)
                
        glfwSetMouseButtonCallback(self.glfw_window, mouse_button_callback_caller)
        
    def set_mouse_scroll_event(self, callback):
        self._init_callback(EventType.MOUSE_SCROLL, callback)
        
        def mouse_scroll_callback_caller(window, xoffset, yoffset):
            for c in self.EVENT_GLFW_CALLBACKS[EventType.MOUSE_SCROLL]:
                c(window, xoffset, yoffset)
                
        glfwSetScrollCallback(self.glfw_window, mouse_scroll_callback_caller)
        
    def set_drag_drop_event(self, callback):
        self._init_callback(EventType.DRAG_DROP, callback)
        
        def drag_drop_callback_caller(window, file_paths):
            for c in self.EVENT_GLFW_CALLBACKS[EventType.DRAG_DROP]:
                c(window, file_paths)
                
        glfwSetDropCallback(self.glfw_window, drag_drop_callback_caller)