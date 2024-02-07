from typing import Dict
from enum import Enum

from OpenGL.GL import *
import glm
import numpy as np

from ..object import BaseObject
from ..object import ShaderType
from ..shader import Shader
from .screen import Screen
from .camera import CameraHelper


class PolygonMode(Enum):
    WIREFRAME = 0
    SOLID = 1
    
    
class RenderManager:
    def __init__(self, shaders: Dict[ShaderType, Shader], screen: Screen, camera: CameraHelper) -> None:
        self.shaders = shaders
        self.screen = screen
        self.camera = camera
        
        self.polygon_mode = PolygonMode.SOLID
        
    def init_renderer(self):
        for type, shader in self.shaders.items():
            shader.init_shader()
        
    def draw(self, object:BaseObject):
        if (self.polygon_mode == PolygonMode.SOLID):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        vertices_info = object.draw_info()
        
        VP = self.screen.get_projection_matrix() * self.camera.get_view_matrix()
        M = object.get_transform_matrix()
        MVP = VP * M
        
        shader = self.shaders[vertices_info.shader_type]
        glUseProgram(shader.program)
        
        glUniformMatrix4fv(shader.get_uniform_loc("MVP"), 1, GL_FALSE, glm.value_ptr(MVP))
        if vertices_info.shader_type == ShaderType.PHONG:
            glUniformMatrix4fv(shader.get_uniform_loc("M"), 1, GL_FALSE, glm.value_ptr(M))
            camera_pos = self.camera.get_camera_pos()
            glUniform3f(shader.get_uniform_loc("view_pos"), camera_pos.x, camera_pos.y, camera_pos.z)
            glUniform3f(shader.get_uniform_loc("material_color"), object.material_color.r, object.material_color.g, object.material_color.b)
            
        glBindVertexArray(vertices_info.VAO)
        glDrawArrays(vertices_info.type, 0, vertices_info.vertices_num)
        
        for c in object.children:
            self.draw(c)
        
    def draw_grid(self, object:BaseObject, gap:float, line_num:int, drop_center:bool=False):
        if (self.polygon_mode == PolygonMode.SOLID):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        vertices_info = object.draw_info()
        
        START = glm.translate(glm.vec3(-gap*line_num, 0, 0))
        
        T = glm.translate(glm.vec3(gap, 0, 0))
        R = glm.rotate(-np.pi/2, glm.vec3(0, 1, 0))
        
        W = START
        
        VP = self.screen.get_projection_matrix() * self.camera.get_view_matrix()
        MVP = VP * W
        
        shader = self.shaders[vertices_info.shader_type]
        glUseProgram(shader.program)
        
        glBindVertexArray(vertices_info.VAO)
        
        for i in range(line_num * 2 + 1):
            if drop_center and i == line_num:
                W = T * W
                continue
            MVP = VP*W
            glUniformMatrix4fv(shader.get_uniform_loc("MVP"), 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(vertices_info.type, 0, vertices_info.vertices_num)
            MVP = VP*R*W
            glUniformMatrix4fv(shader.get_uniform_loc("MVP"), 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(vertices_info.type, 0, vertices_info.vertices_num)
            W = T * W

    def toggle_polygon_mode(self):
        if (self.polygon_mode == PolygonMode.SOLID):
            self.polygon_mode = PolygonMode.WIREFRAME
        else:
            self.polygon_mode = PolygonMode.SOLID
        