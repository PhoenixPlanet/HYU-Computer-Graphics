from typing import Dict
from enum import Enum

from OpenGL.GL import *
from glfw.GLFW import *
import glm

import numpy as np

from .shader import get_shader_program
from .vertex_object_helper import VertexObjectInfo
from .camera import CameraHelper
from .event import InputEventHelper, MouseEventHelper, MouseEventType, EventType

class ProjectionType(Enum):
    ORTHOGONAL = glm.ortho(-5,5, -5,5, -10,10)
    PERSPECTIVE = glm.perspective(45, 1, 0.1, 100)


class GraphicsManager():
    def __init__(self, width, height, title) -> None:
        self.uniform_locations = {}
        self.shader_program = None
        self.VAO_Dict:Dict[str, VertexObjectInfo] = {}
        self.VBO = {}
        self.hasMVP = False
        self.projection = ProjectionType.PERSPECTIVE
        self.camera = CameraHelper()
        self.camera.change_elevation(45)
        self.camera.change_azimuth(45)
        self.camera.change_radius(1)
        
        if not glfwInit():
            raise Exception('glfwInit has failed')
        
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)   # OpenGL 3.3
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE) # for macOS

        # create a window and OpenGL context
        self.window_width = width
        self.window_height = height
        self.window = glfwCreateWindow(width, height, title, None, None)
        if not self.window:
            glfwTerminate()
            raise Exception('window has not created')
        
        glfwMakeContextCurrent(self.window)
        
        self.event_helper = InputEventHelper(self.window)        

        def key_callback(window, key, scancode, action, mods):
            if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
                glfwSetWindowShouldClose(window, GLFW_TRUE)
            
            if key==GLFW_KEY_V and action==GLFW_PRESS:
                self.projection = ProjectionType.PERSPECTIVE if self.projection == ProjectionType.ORTHOGONAL else ProjectionType.ORTHOGONAL
                
        def scroll_callback(window, xoffset, yoffset):
            self.camera.change_radius(-yoffset/30)
                
        self.event_helper.set_keyboard_event(key_callback)
        self.event_helper.set_mouse_scroll_event(scroll_callback)
        
        self.mouse_helper = MouseEventHelper(self.event_helper)
        
        def on_left_mouse_callback(xoffset, yoffset):
            multiple = 50
            azimuth = xoffset / self.window_width * multiple
            elevation = yoffset / self.window_height * multiple
            self.camera.change_azimuth_by_base(-azimuth)
            self.camera.change_elevation_by_base(-elevation)
            
        def on_right_mouse_callback(xoffset, yoffset):
            multiple = 1
            pan_u = xoffset / self.window_width * multiple
            pan_v = yoffset / self.window_height * multiple
            self.camera.pan_by_base(pan_u, pan_v)
            
        def set_base(xpos, ypos):
            self.camera.set_move_base()
            
        self.mouse_helper.set_callback(GLFW_MOUSE_BUTTON_LEFT, MouseEventType.ON_MOUSEDOWN, on_left_mouse_callback)
        self.mouse_helper.set_callback(GLFW_MOUSE_BUTTON_RIGHT, MouseEventType.ON_MOUSEDOWN, on_right_mouse_callback)
        self.mouse_helper.set_callback(GLFW_MOUSE_BUTTON_LEFT, MouseEventType.ON_CLICK, set_base)
        self.mouse_helper.set_callback(GLFW_MOUSE_BUTTON_RIGHT, MouseEventType.ON_CLICK, set_base)
        
        def print_files(window, filepaths):
            for f in filepaths:
                print(f)
                
        self.event_helper.set_drag_drop_event(print_files)
        
    def load_shader_program(self, vertex_file_path, fragment_file_path):
        self.shader_program = get_shader_program(vertex_file_path, fragment_file_path)
        
    def add_uniform_var(self, name: str):
        if not self.shader_program:
            raise Exception('You should initialize shader program first')
        
        if not name in self.uniform_locations:
            self.uniform_locations[name] = glGetUniformLocation(self.shader_program, name)
        
        return self.uniform_locations[name]
    
    def init_uniform_MVP(self):
        self.add_uniform_var("MVP")
        self.hasMVP = True
        
    def add_vertex_object_glm_array(self, name:str, vertices: glm.array, attr_num:int, size:int, drawtype:Constant=GL_TRIANGLES):
        # create and activate VAO (vertex array object)
        VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
        glBindVertexArray(VAO)      # activate VAO

        # create and activate VBO (vertex buffer object)
        VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
        glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

        # copy vertex data to VBO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer
        
        stride = size * attr_num
        for i in range(attr_num):
            pointer = i * size
            glVertexAttribPointer(
                i, 
                size, 
                GL_FLOAT, 
                GL_FALSE, 
                stride * glm.sizeof(glm.float32), 
                None if pointer == 0 else ctypes.c_void_p(pointer*glm.sizeof(glm.float32))
            )
            glEnableVertexAttribArray(i)
            
        vertices_info = VertexObjectInfo(vertices, int((vertices.length / (attr_num*size))), attr_num, size, drawtype, VAO)
        
        self.VAO_Dict[name] = vertices_info
        
    def add_vertex_object(self, name:str, vertices_info:VertexObjectInfo):
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)

        vertices = vertices_info.vertices_arr
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)

        stride = vertices_info.size * vertices_info.attr_num
        for i in range(vertices_info.attr_num):
            pointer = i * vertices_info.size
            glVertexAttribPointer(
                i, 
                vertices_info.size, 
                GL_FLOAT, 
                GL_FALSE, 
                stride * glm.sizeof(glm.float32), 
                None if pointer == 0 else ctypes.c_void_p(pointer*glm.sizeof(glm.float32))
            )
            glEnableVertexAttribArray(i)
        
        vertices_info.VAO = VAO
        self.VAO_Dict[name] = vertices_info
        
    def uniform(self, name: str):
        return self.uniform_locations[name]
    
    def get_view_projection(self):
        return self.projection.value * self.camera.get_view_matrix()
    
    def draw(self, name):
        vertices_info = self.VAO_Dict[name]
        
        MVP = self.get_view_projection()
        glUniformMatrix4fv(self.uniform_locations["MVP"], 1, GL_FALSE, glm.value_ptr(MVP))
        
        glBindVertexArray(vertices_info.VAO)
        glDrawArrays(vertices_info.type, 0, vertices_info.vertices_num)
        
    def draw_grid(self, name:str, gap:float, line_num:int, drop_center:bool=False):
        vertices_info = self.VAO_Dict[name]
        
        START = glm.translate(glm.vec3(-gap*line_num, 0, 0))
        
        T = glm.translate(glm.vec3(gap, 0, 0))
        R = glm.rotate(-np.pi/2, glm.vec3(0, 1, 0))
        
        W = START
        H = START * R
        
        VP = self.get_view_projection()
        MVP = VP * W
        
        glBindVertexArray(vertices_info.VAO)
        
        for i in range(line_num * 2 + 1):
            if drop_center and i == line_num:
                W = T * W
                continue
            MVP = VP*W
            glUniformMatrix4fv(self.uniform_locations["MVP"], 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(vertices_info.type, 0, vertices_info.vertices_num)
            MVP = VP*R*W
            glUniformMatrix4fv(self.uniform_locations["MVP"], 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(vertices_info.type, 0, vertices_info.vertices_num)
            W = T * W
            
    def _before_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        glUseProgram(self.shader_program)
        
        self.mouse_helper.update_state()
        
    def _after_draw(self):
        # swap front and back buffers
        glfwSwapBuffers(self.window)

        # poll events
        glfwPollEvents()
        
    class RenderUpdate:
        def __init__(self, manager) -> None:
            self.manager = manager
            
        def __enter__(self):
            self.manager._before_draw()
            
        def __exit__(self, type, value, trackback):
            self.manager._after_draw()
            
    def render_update(self):
        return self.RenderUpdate(self)