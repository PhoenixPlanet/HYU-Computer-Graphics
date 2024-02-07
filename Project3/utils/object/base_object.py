from __future__ import annotations

from typing import Union, List

from OpenGL.GL import *
import glm

from .vertex_object import VertexObjectInfo
from ..struct import Vec3D, Color

from ..context import ContextBase

class BaseObject:
    def __init__(self, name:str, context:ContextBase, vertices_info:VertexObjectInfo) -> None:
        self.name = name
        self.context:ContextBase = context
        
        self.vertices_info = vertices_info
        self.global_transform = glm.mat4()
        
        self.init_VAO(self.vertices_info)
        
        self.local_position:Vec3D = Vec3D(0, 0, 0, 1)
        self.local_rotation:Vec3D = Vec3D(0, 0, 0)
        self.local_scale:Vec3D = Vec3D(1, 1, 1)
        
        self.velocity:Vec3D = Vec3D(0, 0, 0)
        self.acceleration:Vec3D = Vec3D(0, 0, 0)
        
        self.pre_scale:Vec3D = Vec3D(1, 1, 1)
        
        self.parent:Union[BaseObject, None] = None
        self.children:List[BaseObject] = []
        
        self.material_color = Color.WHITE()
        
    def init_VAO(self, vertices_info: VertexObjectInfo):
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)

        vertices = vertices_info.vertices_arr
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)

        stride = vertices_info.dimension * (len(vertices_info.enabled_attr))
        for i in range(len(vertices_info.enabled_attr)):
            pointer = i * vertices_info.dimension
            glVertexAttribPointer(
                i, 
                vertices_info.dimension, 
                GL_FLOAT, 
                GL_FALSE, 
                stride * glm.sizeof(glm.float32), 
                None if pointer == 0 else ctypes.c_void_p(pointer*glm.sizeof(glm.float32))
            )
            glEnableVertexAttribArray(i)
        
        vertices_info.VAO = VAO
        
        return vertices_info
        
    def draw_info(self):
        return self.vertices_info
    
    def get_global_transfrom(self):
        return self.global_transform
    
    def get_transform_matrix(self):
        PS = glm.scale(glm.vec3(self.pre_scale.x, self.pre_scale.y, self.pre_scale.z))
        return self.global_transform * PS
    
    def update_global_transform(self):
        parent_transform = glm.mat4()
        
        if self.parent != None:
            parent_transform = self.parent.get_global_transfrom()
            
        S = glm.scale(glm.vec3(self.local_scale.x, self.local_scale.y, self.local_scale.z))
        
        Rx = glm.rotate(self.local_rotation.x, glm.vec3(1, 0, 0))
        Ry = glm.rotate(self.local_rotation.y, glm.vec3(0, 1, 0))
        Rz = glm.rotate(self.local_rotation.z, glm.vec3(0, 0, 1))
        R = Rz * Ry * Rx
        
        T = glm.translate(glm.vec3(self.local_position.x, self.local_position.y, self.local_position.z))
        
        M = T * R * S
        
        self.global_transform = parent_transform * M
        
        for c in self.children:
            c.update_global_transform()
                
        return self.global_transform
    
    def add_children(self, object:BaseObject):
        object.parent = self
        self.children.append(object)
    
    def update(self):
        for c in self.children:
            c.update()
    
    def fixed_update(self):
        frametime = 1 / self.context.manager.framerate
        
        self.velocity.x += self.acceleration.x * frametime
        self.velocity.y += self.acceleration.y * frametime
        self.velocity.z += self.acceleration.z * frametime
        
        self.local_position.x += self.velocity.x * frametime
        self.local_position.y += self.velocity.y * frametime
        self.local_position.z += self.velocity.z * frametime
        
        for c in self.children:
            c.fixed_update()
    
    def print_hierarchy(self, depth:int):
        print("  " * depth + f"---{self.name}")
        
        for c in self.children:
            
            c.print_hierarchy(depth + 1)