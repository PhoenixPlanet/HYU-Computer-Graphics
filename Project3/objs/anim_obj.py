import utils
from utils.context import ContextBase
from utils.object.vertex_object import VertexObjectInfo

class AnimObj(utils.BaseObject):
    def __init__(self, name: str, context: ContextBase, vertices_info: VertexObjectInfo) -> None:
        super().__init__(name, context, vertices_info)
        
        self.anim_timestamp = 0
        self.anim_interval = 3
        self.do_anim = False
        self.do_anim_pos = False
        self.do_anim_rot = False
        
        self.start_pos:utils.Vec3D = utils.Vec3D(0, 0, 0)
        self.end_pos:utils.Vec3D = utils.Vec3D(0, 0, 0)
        
        self.start_rot:utils.Vec3D = utils.Vec3D(0, 0, 0)
        self.end_rot:utils.Vec3D = utils.Vec3D(0, 0, 0)
        
    def animation(self):
        t_i = (self.context.get_time() - self.anim_timestamp) / self.anim_interval
        t = utils.BezierInterpolate.cubic_bezier(0.5, 0, 0.5, 1, t_i)[1]
        s = 1 - t
        
        if self.do_anim_pos:
            self.local_position = utils.Vec3D (
                self.start_pos.x * s + self.end_pos.x * t,
                self.start_pos.y * s + self.end_pos.y * t,
                self.start_pos.z * s + self.end_pos.z * t
            )
            
        if self.do_anim_rot:
            self.local_rotation = utils.Vec3D (
                self.start_rot.x * s + self.end_rot.x * t,
                self.start_rot.y * s + self.end_rot.y * t,
                self.start_rot.z * s + self.end_rot.z * t
            )
        
    def anim_position(self, start_pos, end_pos, duration):
        self.anim_timestamp = self.context.get_time()
        self.anim_interval = duration
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.do_anim = True
        self.do_anim_pos = True
        
    def anim_rotation(self, start_rot, end_rot, duration):
        self.anim_timestamp = self.context.get_time()
        self.anim_interval = duration
        self.start_rot = start_rot
        self.end_rot = end_rot
        self.do_anim = True
        self.do_anim_rot = True
        
    def update(self):
        super().update()
        
        if self.do_anim:
            if self.anim_interval + self.anim_timestamp <= self.context.get_time():
                self.do_anim = False
                self.do_anim_pos = False
                self.do_anim_rot = False
                
            self.animation()