from dataclasses import dataclass, astuple # module
from typing import List, Tuple, Union # module
from enum import Flag, auto, Enum

from OpenGL.GL import *
from glfw.GLFW import *
import glm

from ..struct import Color, Point, ObjectFaces, Vertex3D, Vec3D
from .obj_loader import OBJLoader

class VertexAttribute(Flag):
    VERTEX = auto()
    COLOR = auto()
    NORMAL = auto()
    
    def __len__(self) -> int:
        return bin(self._value_).count('1')
    
class ShaderType(Enum):
    BASIC = 0
    FRAME = 1
    PHONG = 2

@dataclass
class VertexObjectInfo():
    vertices_arr:glm.array
    vertices_num:int
    dimension:int
    type:Constant
    enabled_attr:VertexAttribute=VertexAttribute(0)
    VAO:Union[int, None]=None
    shader_type:ShaderType=ShaderType.BASIC
    

class VertexObjectHelper():
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def points(points: List[Point], has_color: bool=False, drawtype: Constant=GL_POINTS):
        if (len(points) == 0):
            raise Exception("No points in parameter")
        
        points_vertex_arr = glm.array(glm.float32, *(points[0].data(has_color))) # type: ignore
        for p in points[1:]:
            points_vertex_arr = points_vertex_arr.concat(glm.array(glm.float32, *(p.data(has_color))))
            
        vertex_obj_info = VertexObjectInfo (
            vertices_arr=points_vertex_arr,
            vertices_num=len(points),
            dimension=3,
            type=drawtype,
            enabled_attr=VertexAttribute.VERTEX | VertexAttribute.COLOR if has_color else VertexAttribute.VERTEX
        )
        
        return vertex_obj_info
    
    @staticmethod
    def line(x1, y1, z1, x2, y2, z2, has_color: bool=True, color=Color.WHITE()):
        line_vertices = VertexObjectHelper.points(
            [
                Point(x1, y1, z1, color),
                Point(x2, y2, z2, color)
            ],
            has_color=has_color,
            drawtype=GL_LINES
        )
        return line_vertices
    
    @staticmethod
    def gridline(plane:Vec3D, width:float, height:float, gap:float, drop_center:bool=False):
        """return VertexObjectInfo instace of grid vertices. grid size is (width) x (height)

        Parameters
        ----------
        plane : Vec3D
            which plane are you going to draw grid? (eg. x == 1 -> y, z plane)
        width : float
            width of grid plane
        height : float
            height of grid plane
        gap : float
            gab between lines
        drop_center : bool, optional
            lines in center of grid won't contain if this attribute is True, by default False
        """
        width_line_num = int(width/gap)
        if width_line_num % 2 == 0:
            width_line_num += 1
        height_line_num = int(height/gap)
        if  height_line_num % 2 == 0:
            height_line_num += 1
        
        width_start = -int(width_line_num / 2) * gap
        height_start = -int(height_line_num / 2) * gap
        
        points = []
        for i in range(width_line_num):
            if (drop_center and i == int(width_line_num / 2)):
                continue
            
            if int(plane.x) == 1:
                points.append(Point(0, -height/2, width_start + (i * gap)))
                points.append(Point(0, height/2, width_start + (i * gap)))
            
            if int(plane.y) == 1:
                points.append(Point(width_start + (i * gap), 0, -height/2))
                points.append(Point(width_start + (i * gap), 0, height/2))
            
            if int(plane.z) == 1:
                points.append(Point(width_start + (i * gap), -height/2, 0))
                points.append(Point(width_start + (i * gap), height/2, 0))
                
        for i in range(height_line_num):
            if (drop_center and i == int(height_line_num / 2)):
                continue
            
            if int(plane.x) == 1:
                points.append(Point(0, height_start + (i * gap), -width/2))
                points.append(Point(0, height_start + (i * gap), width/2))
            
            if int(plane.y) == 1:
                points.append(Point(-width/2, 0, height_start + (i * gap)))
                points.append(Point(width/2, 0, height_start + (i * gap)))
            
            if int(plane.z) == 1:
                points.append(Point(-width/2, height_start + (i * gap), 0))
                points.append(Point(width/2, height_start + (i * gap), 0))
                
        grid_vertices = VertexObjectHelper.points(
            points,
            has_color=True,
            drawtype=GL_LINES
        )
        return grid_vertices
    
    @staticmethod
    def from_obj_file(file_path):
        obj_faces = OBJLoader.parse_opj_file(file_path)
        vertices = OBJLoader.obj_to_vertices(obj_faces)
        
        shader_type = ShaderType.BASIC if vertices[0].normal == None else ShaderType.PHONG
        
        vertex_arr = None
        v_value = []
        
        if shader_type == ShaderType.BASIC:
            v_value.extend(vertices[0].position.data())
            v_value.extend(list(astuple(Color.WHITE())))
            for v in vertices[1:]:
                v_value.extend(v.position.data())
                v_value.extend(list(astuple(Color.WHITE())))
            vertex_arr = glm.array(glm.float32, *v_value) # type: ignore
                
        elif shader_type == ShaderType.PHONG:
            v_value.extend(vertices[0].position.data())
            v_value.extend(vertices[0].normal.data()) # type: ignore
            for v in vertices[1:]:
                v_value.extend(v.position.data())
                v_value.extend(v.normal.data()) # type: ignore
            vertex_arr = glm.array(glm.float32, *v_value) # type: ignore
                
        else:
            v_value.extend(vertices[0].position.data())
            v_value.extend(list(astuple(Color.WHITE())))
            for v in vertices[1:]:
                v_value.extend(v.position.data())
                v_value.extend(list(astuple(Color.WHITE())))
            vertex_arr = glm.array(glm.float32, *v_value) # type: ignore
                
        vertex_obj_info = VertexObjectInfo (
            vertices_arr=vertex_arr,
            vertices_num=len(vertices),
            dimension=3,
            type=GL_TRIANGLES,
            enabled_attr=VertexAttribute.VERTEX | VertexAttribute.COLOR if shader_type != ShaderType.PHONG else VertexAttribute.VERTEX | VertexAttribute.NORMAL,
            shader_type=shader_type
        )
        
        return vertex_obj_info
    
    
    