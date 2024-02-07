from dataclasses import dataclass, astuple # module
from typing import List, Union # module

from OpenGL.GL import *
from glfw.GLFW import *
import glm

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


@dataclass
class VertexObjectInfo():
    vertices_arr:glm.array
    vertices_num:int
    attr_num:int
    size:int
    type:Constant
    VAO:Union[int, None]=None
    

class VertexObjectHelper():
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def points(points: List[Point], has_color: bool=False, drawtype: Constant=GL_POINTS):
        if (len(points) == 0):
            raise Exception("No points in parameter")
        
        points_vertex_arr = glm.array(glm.float32, *(points[0].data(has_color)))
        for p in points[1:]:
            points_vertex_arr = points_vertex_arr.concat(glm.array(glm.float32, *(p.data(has_color))))
            
        vertex_obj_info = VertexObjectInfo (
            vertices_arr=points_vertex_arr,
            vertices_num=len(points),
            attr_num=(2 if has_color else 1),
            size=3,
            type=drawtype
        )
        
        return vertex_obj_info
    
    @staticmethod
    def polygon(points: List[Point], has_color):
        vertex_obj_info = VertexObjectHelper.points(points, has_color, GL_POLYGON)
        
    @staticmethod
    def lines(points: List[Point], has_color):
        vertex_obj_info = VertexObjectHelper.points(points, has_color, GL_LINES)
        
    @staticmethod
    def grid(gap:float, width:float, height:float):
        pass