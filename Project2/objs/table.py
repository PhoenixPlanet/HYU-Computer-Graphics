import os

import numpy as np

import utils
from .anim_obj import AnimObj
from .dish import Dish
from .candles import CandleStick
from .burger import BunBottum

class Table(AnimObj):
    def __init__(self, name: str, context: utils.ContextBase) -> None:
        super().__init__(
            name, 
            context, 
            utils.VertexObjectHelper.from_obj_file(
                os.path.join(".", "models", "WoodenTable.obj")
            )
        )
        
        self.local_scale = utils.Vec3D(4, 4, 4)
        self.local_rotation = utils.Vec3D(0, np.pi / 2, 0)
        self.material_color = utils.Color(0.6, 0.45, 0)
        
        self.dish = Dish("dish", context)
        self.dish.pre_scale = utils.Vec3D(2, 1, 1)
        
        self.add_children(self.dish)
        
        self.candles = CandleStick("candle_stick", context)
        self.add_children(self.candles)
        
        self.burgers = []
        for i in range(2):
            b = BunBottum(f"burger{i}", context, True if i % 2 == 0 else False)
            b.local_scale = utils.Vec3D(2, 2, 2)
            b.local_position.x = -3 + i * 6
            b.local_position.y = 0.75
            self.dish.add_children(b)
            self.burgers.append(b)
            
        self.local_position.x = 2
        
        self.context.start_coroutine(self.anim_seq)
            
    def anim_seq(self):
        while True:
            self.anim_position(utils.Vec3D(2,0,0), utils.Vec3D(-2, 0, 0), 5)
            yield utils.CoroutineWaitForSeconds(self.context, 5)
            
            self.anim_position(utils.Vec3D(-2,0,0), utils.Vec3D(2, 0, 0), 5)
            yield utils.CoroutineWaitForSeconds(self.context, 5)
        
    
        