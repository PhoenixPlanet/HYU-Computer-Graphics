from .load import load_shaders

from OpenGL.GL import *

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

g_vertex_shader_src2 = \
'''
    #version 330 core

    layout (location = 0) in vec3 vin_pos; 
    layout (location = 1) in vec3 vin_normal; 

    out vec3 vout_surface_pos;
    out vec3 vout_normal;

    uniform mat4 MVP;
    uniform mat4 M;

    void main()
    {
        vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);
        gl_Position = MVP * p3D_in_hcoord;

        vout_surface_pos = vec3(M * vec4(vin_pos, 1));
        vout_normal = normalize( mat3(inverse(transpose(M)) ) * vin_normal);
    }
'''

g_fragment_shader_src2 = \
'''
    #version 330 core

    in vec3 vout_surface_pos;
    in vec3 vout_normal;

    out vec4 FragColor;

    uniform vec3 view_pos;
    uniform vec3 material_color;

    void main()
    {
        // light and material properties
        vec3 light_pos = vec3(6,4,5);
        vec3 light_color = vec3(0.7,0.9,0.6);
        // vec3 material_color = vec3(0.5,0.5,0.9);
        float material_shininess = 64.0;
        
        vec3 light_pos2 = vec3(-4,4,-4);
        vec3 light_color2 = vec3(0.6,0.1,0.3);

        // light components
        vec3 light_ambient = 0.1*light_color;
        vec3 light_diffuse = light_color;
        vec3 light_specular = light_color;
        
        vec3 light_ambient2 = 0.1*light_color2;
        vec3 light_diffuse2 = light_color2;
        vec3 light_specular2 = light_color2;

        // material components
        vec3 material_ambient = material_color;
        vec3 material_diffuse = material_color;
        vec3 material_specular = light_color;  // for non-metal material
        
        vec3 material_specular2 = light_color2;

        // ambient
        vec3 ambient = light_ambient * material_ambient;
        
        vec3 ambient2 = light_ambient2 * material_ambient;

        // for diffiuse and specular
        vec3 normal = normalize(vout_normal);
        vec3 surface_pos = vout_surface_pos;
        vec3 light_dir = normalize(light_pos - surface_pos);
        
        vec3 light_dir2 = normalize(light_pos2 - surface_pos);

        // diffuse
        float diff = max(dot(normal, light_dir), 0);
        vec3 diffuse = diff * light_diffuse * material_diffuse;
        
        float diff2 = max(dot(normal, light_dir2), 0);
        vec3 diffuse2 = diff2 * light_diffuse2 * material_diffuse;

        // specular
        vec3 view_dir = normalize(view_pos - surface_pos);
        vec3 reflect_dir = reflect(-light_dir, normal);
        float spec = pow( max(dot(view_dir, reflect_dir), 0.0), material_shininess);
        vec3 specular = spec * light_specular * material_specular;
        
        vec3 reflect_dir2 = reflect(-light_dir2, normal);
        float spec2 = pow( max(dot(view_dir, reflect_dir2), 0.0), material_shininess);
        vec3 specular2 = spec * light_specular2 * material_specular;

        vec3 color = ambient + diffuse + specular + ambient2 + diffuse2 + specular2;
        FragColor = vec4(color, 1.);
    }
'''

def get_shader_program():
    # with open(vertex_file_path, mode='r') as f:
    #     g_vertex_shader_src = f.read()

    # with open(fragment_file_path, mode='r') as f:
    #     g_fragment_shader_src = f.read()
    
    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)
    return shader_program

class Shader():
    def __init__(self, vertex_shader_src, frag_shader_src, uniform_vars) -> None:
        self.program = None
        self.vertex_shader_src = vertex_shader_src
        self.frag_shader_src = frag_shader_src
        
        self.uniform_vars = uniform_vars
        self.uniform_var_locs = {}
            
    def get_uniform_loc(self, name):
        return self.uniform_var_locs[name]
    
    def init_shader(self):
        self.program = load_shaders(self.vertex_shader_src, self.frag_shader_src)
        
        for uv in self.uniform_vars:
            self.uniform_var_locs[uv] = glGetUniformLocation(self.program, uv)
        
            
frame_shader = Shader(g_vertex_shader_src, g_fragment_shader_src, ['MVP'])
phong_shader = Shader(g_vertex_shader_src2, g_fragment_shader_src2, ['MVP',"M","view_pos", "material_color"])