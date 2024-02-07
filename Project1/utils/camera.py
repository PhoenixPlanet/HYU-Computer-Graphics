from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np


class SphericalEyePos():
    INITIAL_EYE_POINT_VEC = glm.vec3(0, 0, 1)
    
    def __init__(self) -> None:
        self.azimuth:float = 0 # degree angle
        self.elevation:float = 0 # degree angle
        self.radius:float = 1
        self.is_opposite = False
        self.up = glm.vec3(0, 1, 0)
        self.alter_up = glm.vec3(0, 0, -1)
        
        self.move_base_azimuth = 0
        self.move_base_elevation = 0
        self.move_base_radius = 1
        self.move_base_opposite = False
        
    def set(self, azimuth, elevation, radius):
        self.azimuth = azimuth
        self.elevation = elevation
        self.radius = radius
        
    def set_move_base(self):
        self.move_base_azimuth = self.azimuth
        self.move_base_elevation = self.elevation
        self.move_base_radius = self.radius
        self.move_base_opposite = self.is_opposite
        
    def get_w_vec(self):
        x = np.cos(np.radians(self.elevation)) * np.sin(np.radians(self.azimuth))
        y = np.sin(np.radians(self.elevation))
        z = np.cos(np.radians(self.elevation)) * np.cos(np.radians(self.azimuth))
        
        w_vec = glm.vec3(x, y, z)
        return w_vec
    
    def get_camera_vec(self):
        w = self.get_w_vec()
        u = glm.normalize(glm.cross(w, self.up))
        v = glm.cross(w, u)
        
        return (w, u, v)
    
    def get_panning_vec(self, x, y):
        w, u, v = self.get_camera_vec()
        
        if self.move_base_opposite:
            return - (u * x) - (v * y)
        else:
            return (u * x) + (v * y)
        
    def get_eye_point_vec(self):
        eye_point_vec = self.get_w_vec() * self.radius
        return eye_point_vec
    
    def get_eye_point(self, target_point):
        eye_point_vec = self.get_eye_point_vec()
        return target_point + eye_point_vec
    
    def get_up(self):
        if self.elevation == 90:
            return self.alter_up
        elif self.elevation == -90:
            return -self.alter_up
        elif self.is_opposite:
            return -self.up
        else:
            return self.up
    
    def set_azimuth(self, theta):
        # -360 < azimuth < 360
        self.azimuth = theta - int(theta / 360) * 360 
    
    def change_azimuth(self, theta):
        self.set_azimuth(self.azimuth + theta)
    
    def set_elevation(self, phi):
        # -180 < elevation < 180
        e = phi - int(phi / 360) * 360
        if e > 180:
            e -= 360
        if e < -180:
            e += 360
            
        self.elevation = e 
        if e > 90 or e < -90:
            self.is_opposite = True
        else:
            self.is_opposite = False
    
    def change_elevation(self, phi):
        self.set_elevation(self.elevation + phi)
        
    def change_azimuth_by_base(self, theta):
        if self.move_base_opposite:
            self.set_azimuth(self.move_base_azimuth - theta)
        else:
            self.set_azimuth(self.move_base_azimuth + theta)
    
    def change_elevation_by_base(self, phi):
        self.set_elevation(self.move_base_elevation + phi)
        
    def change_radius(self, r):
        self.radius += r
        if (self.radius < 0.01):
            self.radius = 0.01


class CameraHelper():
    def __init__(self) -> None:
        self.elevation = 0
        self.azimuth = 0
        self.eye_point = SphericalEyePos()
        self.target_point = glm.vec3(0, 0, 0)
        
        self.move_base_target_point = glm.vec3(0, 0, 0)
        
    def set_move_base(self):
        self.move_base_target_point = glm.vec3(self.target_point.x, self.target_point.y, self.target_point.z)
        self.eye_point.set_move_base()
    
    def change_azimuth(self, angle_degree: float):
        self.eye_point.change_azimuth(angle_degree)
        
    def change_azimuth_by_base(self, angle_degree: float):
        self.eye_point.change_azimuth_by_base(angle_degree)
        
    def change_elevation(self, angle_degree: float):
        self.eye_point.change_elevation(angle_degree)
        
    def change_elevation_by_base(self, angle_degree: float):
        self.eye_point.change_elevation_by_base(angle_degree)
        
    def change_radius(self, radius):
        self.eye_point.change_radius(radius)
    
    def pan_u(self, x: float):
        w, u, v = self.eye_point.get_camera_vec()
        
        self.target_point = self.target_point + (u * x)
        
    def pan_v(self, y: float):
        w, u, v = self.eye_point.get_camera_vec()
        
        self.target_point = self.target_point + (v * y)
        
    def pan_by_base(self, x: float, y: float):
        self.target_point = self.move_base_target_point + self.eye_point.get_panning_vec(x, y)
        
    def get_view_matrix(self):
        v_mat = glm.lookAt(self.eye_point.get_eye_point(self.target_point), self.target_point, self.eye_point.get_up())
        
        found_nan = False
        for vec in v_mat.to_tuple():
            for i in vec:
                if glm.isnan(i):
                    w_d = self.target_point.z - self.eye_point.get_eye_point(self.target_point).z
                    w_d = 1 if w_d > 0 else -1
                    v_mat = glm.lookAt(self.eye_point.get_eye_point(self.target_point), self.target_point, w_d * self.eye_point.alter_up)
                    found_nan = True
                    break
            if found_nan:
                break
                
        return v_mat