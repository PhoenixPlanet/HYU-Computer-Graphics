from __future__ import annotations

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Union, Callable, Generator, Optional, Any, TYPE_CHECKING

from ..coroutine import BaseCoroutineCondtion, CoroutineEnd
if TYPE_CHECKING:
    from ..core import GraphicsManager
    from ..object import BaseObject

class ContextMode(Enum):
        SINGLE = 0
        HIEARARCHI = 1

class ContextBase():
    
    def __init__(self, manager: GraphicsManager) -> None:
        self.manager:GraphicsManager = manager
        self.single_mode_object:Union[BaseObject, None] = None
        self.hierarchy_objects:List[BaseObject] = []
        self.is_updating:bool = False
        self.coroutines:Dict[Generator[BaseCoroutineCondtion, None, None], Optional[BaseCoroutineCondtion]] = {}
        
    def update(self):
        for o in self.hierarchy_objects:
            self.draw(o)
                
    def fixed_update(self):
        for o in self.hierarchy_objects:
            o.fixed_update()

    def pre_update(self):
        self.is_updating = True
        
        for o in self.hierarchy_objects:
            o.update()
            o.update_global_transform()
    
    def post_update(self):
        self.is_updating = False
        
    def coroutine_update(self):
        for generator, condition in list(self.coroutines.items()):
            if condition == None or condition.check():
                next_condition: BaseCoroutineCondtion = next(generator, CoroutineEnd(self))
                if isinstance(next_condition, CoroutineEnd):
                    del self.coroutines[generator]
                    continue
                self.coroutines[generator] = next_condition
            
    def start_coroutine(
        self, 
        c: Union[
            Callable[[Any], Generator[BaseCoroutineCondtion, None, None]], 
            Callable[[], Generator[BaseCoroutineCondtion, None, None]]
        ], 
        *args
    ):
        self.coroutines[c(*args)] = None
    
    def add_object(self, object:BaseObject):
        self.hierarchy_objects.append(object)
        object.parent = None
    
    def set_object(self, object:BaseObject):
        self.hierarchy_objects = [object]
        object.parent = None
        
    def get_time(self):
        return self.manager.time
        
    def draw(self, object:BaseObject):
        if (self.is_updating):
            self.manager.renderer.draw(object)
            
    def draw_grid(self, object, gap:float, line_num:int, drop_center:bool=False):
        if (self.is_updating):
            self.manager.renderer.draw_grid(object, gap, line_num, drop_center)
            
    def print_hierarchy(self):
        for o in self.hierarchy_objects:
            o.print_hierarchy(0)
            
    def set_frame_rate(self, framerate):
        self.manager.framerate = framerate