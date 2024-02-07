from .load import load_shaders

def get_shader_program(vertex_file_path, fragment_file_path):
    # with open(vertex_file_path, mode='r') as f:
    #     g_vertex_shader_src = f.read()

    # with open(fragment_file_path, mode='r') as f:
    #     g_fragment_shader_src = f.read()
    
    g_vertex_shader_src = \
    """
        #version 330 core

        layout (location = 0) in vec3 vin_pos; 
        layout (location = 1) in vec3 vin_color; 

        out vec4 vout_color;

        uniform mat4 MVP;

        void main()
        {
            // 3D points in homogeneous coordinates
            vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);

            gl_Position = MVP * p3D_in_hcoord;

            vout_color = vec4(vin_color, 1.);
        }
    """
    
    g_fragment_shader_src = \
    """
        #version 330 core

        out vec4 FragColor;
        in vec4 vout_color;

        void main()
        {
            FragColor = vout_color;
        }
    """
    
    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)
    return shader_program