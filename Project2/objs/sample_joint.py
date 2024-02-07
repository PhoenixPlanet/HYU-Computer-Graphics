import os

import numpy as np
import OpenGL.GL

import utils

class Sqaures(utils.BaseObject):
    def __init__(self, name: str, context: utils.ContextBase, color:utils.Color) -> None:
        vertices_obj = utils.VertexObjectHelper.points(
            [
                utils.Point(-1, 1, 0, color),
                utils.Point(-1, -1, 0, color),
                utils.Point(1, -1, 0, color),
                utils.Point(-1, 1, 0, color),
                utils.Point(1, -1, 0, color),
                utils.Point(1, 1, 0, color),
            ],
            has_color=True,
            drawtype=OpenGL.GL.GL_LINES
        )
        
        super().__init__(name, context, vertices_obj)