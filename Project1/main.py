from OpenGL.GL import *
from glfw.GLFW import *

from utils import GraphicsManager, VertexObjectHelper, Point, Color


def main(vertex_file, fragment_file):
    manager = GraphicsManager(800, 800, "(2019039843)")
    manager.load_shader_program(vertex_file, fragment_file)
    #glfwSetInputMode(manager.window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)
    
    vertices_obj = VertexObjectHelper.points(
        [
            Point(0, 0, -2),
            Point(0, 0, 2)
        ],
        has_color=True,
        drawtype=GL_LINES
    )
    
    manager.add_vertex_object("grid", vertices_obj)
    
    manager.init_uniform_MVP()

    # loop until the user closes the window
    while not glfwWindowShouldClose(manager.window):
        with manager.render_update():
            manager.draw_grid("grid", 0.1, 20)

    # terminate glfw
    glfwTerminate()

if __name__ == "__main__":
    vert = './vertex.vert'
    frag = './fragment.frag'
    main(vert, frag)
