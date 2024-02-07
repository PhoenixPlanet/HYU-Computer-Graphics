from __future__ import annotations

from dataclasses import dataclass, astuple # module
from typing import List, Tuple, Union

@dataclass
class Color():
    r:float=0
    g:float=0
    b:float=0
    
    @staticmethod
    def RED():
        return Color(1.0, 0., 0.)
    
    @staticmethod
    def GREEN():
        return Color(0., 1.0, 0.)
        
    @staticmethod
    def BLUE():
        return Color(0., 0., 1.0)
    
    @staticmethod
    def WHITE():
        return Color(1.0, 1.0, 1.0)
    

@dataclass
class Point():
    x:float=0.
    y:float=0.
    z:float=0.
    color:Color=Color.WHITE()
    
    def data(self, has_color):
        if has_color:
            return (self.x, self.y, self.z, *astuple(self.color))
        else:
            return (self.x, self.y, self.z, *astuple(Color.WHITE()))
        
    def coor_data(self):
        return (self.x, self.y, self.z)
        
@dataclass
class PointWithNormal():
    x:float=0.
    y:float=0.
    z:float=0.
    norm:Point = Point()
    
    def data(self):
        return (self.x, self.y, self.z, *self.norm.coor_data())     
        
        
@dataclass
class Vec2D():
    x:float=0.
    y:float=0.
    w:float=0.

@dataclass
class Vec3D():
    x:float=0.
    y:float=0.
    z:float=0.
    w:float=0.
    
    def data(self, contain_w:bool=False):
        if contain_w:
            return [self.x, self.y, self.z, self.w]
        else:
            return [self.x, self.y, self.z]
        
    def point(self):
        return Point(self.x, self.y, self.z) 
    
    
@dataclass
class Face():
    indices: List[Tuple[int, int]]

@dataclass
class TriangleFace():
    a: Tuple[int, int]
    b: Tuple[int, int]
    c: Tuple[int, int]
    
@dataclass
class ObjectFaces():
    ref_vertex_list: List[Vec3D]
    ref_vertex_norm_list: List[Vec3D]
    faces: List[TriangleFace] # List[(vertex inx, vertex normal idx)]
    

@dataclass
class Vertex3D():
    position:Vec3D = Vec3D(0, 0, 0, 1)
    color:Union[Color, None] = None
    normal:Union[Vec3D, None] = None
    