import os

from glfw.GLFW import *

import utils
import objs

def main():
    manager = utils.GraphicsManager(800, 800, "(2019039843)", 60)    
    
    main_context = utils.BVHContext(manager)
    
    manager.run(main_context)

    manager.exit()

if __name__ == "__main__":
    main()