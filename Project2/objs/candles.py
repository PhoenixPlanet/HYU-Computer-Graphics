import os

import numpy as np

import utils
from .anim_obj import AnimObj
        
class Candle(AnimObj):
    def __init__(self, name: str, context: utils.ContextBase, offset, path) -> None:
        super().__init__(
            name, 
            context, 
            utils.VertexObjectHelper.from_obj_file(
                os.path.join(".", "models", "candle", path)
            )
        )
        
        self.local_scale = utils.Vec3D(0.1, 0.1, 0.1)
        
        self.move_vel_offset = offset
        
    def fixed_update(self):
        super().fixed_update()
        
        t = self.context.get_time() * 0.7
        vel = t + self.move_vel_offset
        
        self.local_position = \
            utils.Vec3D(
                np.cos(vel) * 0.5, 
                np.sin(t*2) * 0.2 + 0.7, 
                -np.sin(t) * 0.5
            )
        
class CandleStick(AnimObj):
    def __init__(self, name: str, context: utils.ContextBase) -> None:
        super().__init__(
            name, 
            context, 
            utils.VertexObjectHelper.from_obj_file(
                os.path.join(".", "models", "candle", "candle_stick.obj")
            )
        )
        
        self.candle1 = Candle("candle0", context, np.pi, "candle_short.obj")
        self.candle2 = Candle("candle1", context, 0, "candle_long.obj")
        
        self.pre_scale = utils.Vec3D(0.02, 0.02, 0.02)
        
        self.add_children(self.candle1)
        self.add_children(self.candle2)
        
    def fixed_update(self):
        super().fixed_update()
        
        vel = self.context.get_time() * 0.3
        
        self.local_position = \
            utils.Vec3D(
                np.cos(vel) * 2, 
                np.sin(vel*2) * 0.5 + 0.4, 
                -np.sin(vel) * 2
            )