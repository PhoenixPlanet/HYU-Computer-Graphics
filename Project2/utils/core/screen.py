from enum import Enum

import glm
from OpenGL.GL import *

class ProjectionType(Enum):
    ORTHOGONAL = 0
    PERSPECTIVE = 1

class Screen:
    class Projection():
        def projection_matrix(self) -> glm.mat4x4:
            if self.type == ProjectionType.ORTHOGONAL:
                ortho_height = 10.
                orhto_width = ortho_height * (self.screen.width / self.screen.height)
                return glm.ortho(-orhto_width * .5, orhto_width * .5, -ortho_height * .5, ortho_height * .5, -10, 10)
            else:
                return glm.perspective(45, (self.screen.width / self.screen.height), 0.1, 200)
            
        def __init__(self, screen) -> None:
            self.screen = screen
            
            self.set_projection_type(ProjectionType.PERSPECTIVE)
            
        def set_projection_type(self, type):
            self.type = type
            self.matrix: glm.mat4x4 = self.projection_matrix()
            
        def toggle_projection_type(self):
            if self.type == ProjectionType.ORTHOGONAL:
                self.type = ProjectionType.PERSPECTIVE
            else:
                self.type = ProjectionType.ORTHOGONAL
            
            self.matrix = self.projection_matrix()
            
        
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        
        self.projection = Screen.Projection(self)
        
    def on_viewport_size_change(self, window, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, self.width, self.height)
        self.projection.set_projection_type(self.projection.type)
        
    def toggle_projection_type(self):
        self.projection.toggle_projection_type()
        
    def get_projection_matrix(self):
        return self.projection.matrix