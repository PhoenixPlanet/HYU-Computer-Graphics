import utils
import OpenGL.GL

class FrameObj(utils.BaseObject):
    def __init__(self, name: str, context) -> None:
        vertices_obj = utils.VertexObjectHelper.points(
            [
                utils.Point(0, 0, 0, utils.Color.RED()),
                utils.Point(10, 0, 0, utils.Color.RED()),
                utils.Point(0, 0, 0, utils.Color.GREEN()),
                utils.Point(0, 10, 0, utils.Color.GREEN()),
                utils.Point(0, 0, 0, utils.Color.BLUE()),
                utils.Point(0, 0, 10, utils.Color.BLUE()),
            ],
            has_color=True,
            drawtype=OpenGL.GL.GL_LINES
        )
        
        super().__init__(name, context, vertices_obj)