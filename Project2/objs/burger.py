import os

import numpy as np

import utils
from .anim_obj import AnimObj

cheese_obj = \
    utils.VertexObjectHelper.from_obj_file(
        os.path.join(".", "models", "burger", "cheese.obj")
    )

lettuce_obj = \
    utils.VertexObjectHelper.from_obj_file(
        os.path.join(".", "models", "burger", "lettuce.obj")
    )
    
meat_obj = \
    utils.VertexObjectHelper.from_obj_file(
        os.path.join(".", "models", "burger", "meat.obj")
    )
    
tomato_obj = \
    utils.VertexObjectHelper.from_obj_file(
        os.path.join(".", "models", "burger", "tomato.obj")
    )
    
bun_upper_obj = \
    utils.VertexObjectHelper.from_obj_file(
        os.path.join(".", "models", "burger", "bun_upper.obj")
    )

class BurgerIngradient(AnimObj):
    def __init__(self, name: str, context: utils.ContextBase, vertex_obj, base) -> None:
        super().__init__(
            name, 
            context, 
            vertex_obj
        )
        
        self.base = base
        
    def fixed_update(self):
        super().fixed_update()
        
        if (self.local_position.y <= self.base):
            self.acceleration.y = 0
            self.velocity.y = 0
            self.local_position.y = self.base
            
        else:
            self.acceleration = utils.Vec3D(0, -9.8, 0)

class BunBottum(AnimObj):
    def __init__(self, name: str, context: utils.ContextBase, wait_start:bool=False) -> None:
        super().__init__(
            name, 
            context, 
            utils.VertexObjectHelper.from_obj_file(
                os.path.join(".", "models", "burger", "bun_bottom.obj")
            )
        )
        
        self.wait_start = wait_start
        
        self.material_color = utils.Color(0.8, 0.6)
        
        self.cheese = BurgerIngradient("cheese", context, cheese_obj, 0.1)
        self.cheese.material_color = utils.Color(1, 0.8, 0.15)
        self.lettuce = BurgerIngradient("lettuce", context, lettuce_obj, 0.3)
        self.lettuce.material_color = utils.Color(0, 0.8, 0.15)
        self.meat = BurgerIngradient("meat", context, meat_obj, 0.5)
        self.meat.material_color = utils.Color(0.67, 0.35)
        
        self.tomato = BurgerIngradient("tomato", context, tomato_obj, 0.8)
        self.tomato.material_color = utils.Color(1, 0)
        self.tomato.local_position.x = -0.3
        self.tomato.local_position.z = -0.3
        self.tomato2 = BurgerIngradient("tomato", context, tomato_obj, 0.8)
        self.tomato2.material_color = utils.Color(1, 0)
        self.tomato2.local_position.x = 0
        self.tomato2.local_position.z = 0.3
        self.tomato3 = BurgerIngradient("tomato", context, tomato_obj, 0.8)
        self.tomato3.material_color = utils.Color(1, 0)
        self.tomato3.local_position.x = 0.3
        self.tomato3.local_position.z = -0.3
        
        self.bun_upper = BurgerIngradient("bun_upper", context, bun_upper_obj, 1)
        self.bun_upper.material_color = utils.Color(0.8, 0.6)
        
        self.ingradients = [self.cheese, self.lettuce, self.meat, [self.tomato, self.tomato2, self.tomato3], self.bun_upper]
        
        idx = 0
        for i in self.ingradients:
            if idx == 3:
                for ti in i:
                    self.add_children(ti)
            else:
                self.add_children(i)
            idx += 1
        
        self.context.start_coroutine(self.init_pos)
        
    def fixed_update(self):
        super().fixed_update()
        
        if (self.meat.local_position.y <= 0):
            self.meat.acceleration.y = 0
            self.meat.velocity.y = 0
            self.meat.local_position.y = 0
            
        else:
            self.meat.acceleration = utils.Vec3D(0, -9.8, 0)
        
    def init_pos(self):
        if self.wait_start:
            yield utils.CoroutineWaitForSeconds(self.context, 2.5)
            
        while True:
            idx = 0
            for i in self.ingradients:
                if idx == 3:
                    for ti in i:
                        ti.local_position.y = ti.base + 2 + (idx * 0.5)
                else:
                    i.local_position.y = i.base + 2 + (idx * 0.5)
                idx += 1
                
            yield utils.CoroutineWaitForSeconds(self.context, 5)

