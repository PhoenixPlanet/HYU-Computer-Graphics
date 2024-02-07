import os

import numpy as np

import utils
from .anim_obj import AnimObj

class Dish(AnimObj):
    def __init__(self, name: str, context: utils.ContextBase) -> None:
        super().__init__(
            name, 
            context, 
            utils.VertexObjectHelper.from_obj_file(
                os.path.join(".", "models", "dish.obj")
            )
        )
        
        self.down_pos = utils.Vec3D(-0.3, 0.75, 0)
        self.up_pos = utils.Vec3D(-0.3, 1.4, 0)
        
        self.local_scale = utils.Vec3D(0.07, 0.07, 0.07)
        self.local_position = self.down_pos
        
    def move_up(self):
        self.anim_position(self.down_pos, self.up_pos, 0.5)
        yield utils.CoroutineWaitForSeconds(self.context, 0.6)
        
    def move_down(self):
        self.anim_position(self.up_pos, self.down_pos, 0.5)
        yield utils.CoroutineWaitForSeconds(self.context, 0.6)
        
    def fixed_update(self):
        super().fixed_update()
        
        self.local_position.x = np.sin(self.context.get_time() * 0.3)