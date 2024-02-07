from enum import Enum
from typing import List, TYPE_CHECKING

import OpenGL.GL
import glm
import numpy as np

if TYPE_CHECKING:
    from .bvh_context import BVHContext
from .bvh_enum import BVHRenderMode
from ..object import BaseObject, VertexObjectHelper, VertexObjectInfo
from ..struct import Point, Vec3D, Color

class ChannelType(Enum):
    XPOSITION = 0
    YPOSITION = 1
    ZPOSITION = 2
    XROTATION = 3
    YROTATION = 4
    ZROTATION = 5
    
    Xposition = 0
    Yposition = 1
    Zposition = 2
    Xrotation = 3
    Yrotation = 4
    Zrotation = 5

class BVHObject(BaseObject):
    def __init__(self, name: str, idx: int, context, offset: Vec3D, channels: List[ChannelType]) -> None:
        self.idx = idx
        self.end_points: List[Point] = []
        
        self.channels = channels
        self.offset = offset
        self.local_position = offset
        
        self.min_size_neg = Vec3D(0.05, 0.05, 0.05)
        self.min_size_pos = Vec3D(0.05, 0.05, 0.05)
        
        self.is_end_site = False
        
        self.anim_frames: List[List[float]] = []
        
        vertices_obj = VertexObjectHelper.cube_phong()
        
        self.line_vertices_info:VertexObjectInfo
        
        self.context:BVHContext
        
        super().__init__(name, context, vertices_obj)
        
    def add_end_point(self, point: Point):
        self.end_points.append(point)
    
    def set_is_end_site(self, is_end_site:bool):
        self.is_end_site = is_end_site
        
    def get_chan_num(self):
        return len(self.channels)
    
    def add_frame_data(self, data: List[float]):
        self.anim_frames.append(data)
    
    def set_line_vertices(self, height):
        p_list = []
        
        self.min_size_neg = Vec3D(0.05, 0.05, 0.05)
        self.min_size_pos = Vec3D(0.05, 0.05, 0.05)
        
        for ep in self.end_points:
            p_list.append(Point())
            p_list.append(ep)
            
            if (ep.x < 0):
                if glm.abs(ep.x) > self.min_size_neg.x:
                    self.min_size_neg.x = glm.abs(ep.x)
            else:
                if ep.x > self.min_size_pos.x:
                    self.min_size_pos.x = ep.x
                    
            if (ep.y < 0):
                if glm.abs(ep.y) > self.min_size_neg.y:
                    self.min_size_neg.y = glm.abs(ep.y)
            else:
                if ep.y > self.min_size_pos.y:
                    self.min_size_pos.y = ep.y
                    
            if (ep.z < 0):
                if glm.abs(ep.z) > self.min_size_neg.z:
                    self.min_size_neg.z = glm.abs(ep.z)
            else:
                if ep.z > self.min_size_pos.z:
                    self.min_size_pos.z = ep.z
                    
        x_l = self.min_size_neg.x + self.min_size_pos.x
        y_l = self.min_size_neg.y + self.min_size_pos.y
        z_l = self.min_size_neg.z + self.min_size_pos.z
        
        max_l = max(x_l, y_l, z_l)
        
        scale_factor = 0.05 * max_l / 0.5
        
        if max_l == x_l:
            self.min_size_neg = Vec3D(self.min_size_neg.x, scale_factor, scale_factor)
            self.min_size_pos = Vec3D(self.min_size_pos.x, scale_factor, scale_factor)
        elif max_l == y_l:
            self.min_size_neg = Vec3D(scale_factor, self.min_size_neg.y, scale_factor)
            self.min_size_pos = Vec3D(scale_factor, self.min_size_pos.y, scale_factor)
        elif max_l == z_l:
            self.min_size_neg = Vec3D(scale_factor, scale_factor, self.min_size_neg.z)
            self.min_size_pos = Vec3D(scale_factor, scale_factor, self.min_size_pos.z)
                    
        #print(f"{self.name} {max_l} {scale_factor}")
            
        vertices_obj = VertexObjectHelper.points(
            p_list,
            has_color=True,
            drawtype=OpenGL.GL.GL_LINES
        )
        
        self.line_vertices_info = self.init_VAO(vertices_obj)
        
    def draw_info(self):
        if self.context.render_mode == BVHRenderMode.LINE:
            return self.line_vertices_info
        else:
            return self.vertices_info
    
    def fixed_update(self):
        if self.context.play_anim:
            anim_data = self.anim_frames[self.context.cur_frame - 1]
            
            self.local_position = Vec3D()
            self.local_rotation = Vec3D()
            
            for i, c in enumerate(self.channels):
                if c is ChannelType.XPOSITION:
                    self.local_position.x = anim_data[i]
            
                elif c is ChannelType.YPOSITION:
                    self.local_position.y = anim_data[i]
                    
                elif c is ChannelType.ZPOSITION:
                    self.local_position.z = anim_data[i]
                    
                elif c is ChannelType.XROTATION:
                    self.local_rotation.x = glm.radians(anim_data[i])
                    
                elif c is ChannelType.YROTATION:
                    self.local_rotation.y = glm.radians(anim_data[i])
                    
                elif c is ChannelType.ZROTATION:
                    self.local_rotation.z = glm.radians(anim_data[i])
        
        super().fixed_update()
        
    def get_transform_matrix(self):
        if self.context.render_mode == BVHRenderMode.BOX:
            S = glm.scale(glm.vec3(
                (self.min_size_neg.x + self.min_size_pos.x),
                (self.min_size_neg.y + self.min_size_pos.y),
                (self.min_size_neg.z + self.min_size_pos.z),
            ))
            
            ST = glm.translate(glm.vec3(
                -(self.min_size_neg.x - self.min_size_pos.x) / 2, 
                -(self.min_size_neg.y - self.min_size_pos.y) / 2, 
                -(self.min_size_neg.z - self.min_size_pos.z) / 2
            ))
            #ST = glm.mat4()
            
            return self.global_transform * ST * S
        else:
            return self.global_transform
    
    def update_global_transform(self):
        parent_transform = glm.mat4()
        
        if self.parent != None:
            parent_transform = self.parent.get_global_transfrom()
        
        Rx = glm.rotate(self.local_rotation.x, glm.vec3(1, 0, 0))
        Ry = glm.rotate(self.local_rotation.y, glm.vec3(0, 1, 0))
        Rz = glm.rotate(self.local_rotation.z, glm.vec3(0, 0, 1))
        
        Tx = glm.translate(glm.vec3(self.local_position.x, 0, 0))
        Ty = glm.translate(glm.vec3(0, self.local_position.y, 0))
        Tz = glm.translate(glm.vec3(0, 0, self.local_position.z))
        
        M = glm.translate(glm.vec3(self.offset.x, self.offset.y, self.offset.z))
        
        for c in self.channels:
            if c is ChannelType.XPOSITION:
                M = M * Tx
            
            elif c is ChannelType.YPOSITION:
                M = M * Ty
                
            elif c is ChannelType.ZPOSITION:
                M = M * Tz
                
            elif c is ChannelType.XROTATION:
                M = M * Rx
                
            elif c is ChannelType.YROTATION:
                M = M * Ry
                
            elif c is ChannelType.ZROTATION:
                M = M * Rz
                
        S = glm.scale(glm.vec3(self.local_scale.x, self.local_scale.y, self.local_scale.z))
        
        self.global_transform = parent_transform * S * M
        
        for c in self.children:
            c.update_global_transform()
                
        return self.global_transform
    
    def print_hierarchy(self, depth:int):
        print("  " * depth + f"---{self.name} {np.radians(self.anim_frames[0])}")
        
        for c in self.children:
            
            c.print_hierarchy(depth + 1)
        