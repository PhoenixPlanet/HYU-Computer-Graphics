from typing import List, Tuple
import os, time
from enum import Enum
from dataclasses import dataclass

from ..struct import Vec3D, Face, TriangleFace, ObjectFaces, Vertex3D
from .bvh_object import BVHObject, ChannelType

class ParsingStep(Enum):
    START = 0
    HIERARCHY = 1
    JOINT = 3
    MOTION = 4
    PARSE_MOTION = 5
    
@dataclass
class BVHAnimInfo:
    bvh_objects: List[BVHObject]
    frames: int
    frame_time: float

class BVHLoader:
    @staticmethod
    def parse_bvh_file(file_path:str, context, print_info:bool = True):
        bvh_objs: List[BVHObject] = []
        bvh_obj_stack: List[BVHObject] = []
        parsed_frame: int = 0
        frame: int = 0
        frametime: float = 0
        parsing_step = ParsingStep.START
        
        start_time = time.time()
        with open(file_path, "r") as bvh_f:
            i = -1
            
            def get_joint_info(j):
                o = None
                c = None
                while True:
                    j = j + 1
                    l = bvh_f.readline()
                    if not l:
                        BVHLoader.parse_error(j, l)
                    if len(l.strip()) == 0 or l.split()[0] == '{':
                        continue
                    
                    v = l.split()
                    
                    if v[0] == "OFFSET":
                        o = Vec3D(float(v[1]), float(v[2]), float(v[3]))
                        continue
                    
                    if v[0] == "CHANNELS":
                        if o == None:
                            BVHLoader.parse_error(j, line)
                            return j, l, None, None
                        
                        c = []
                        for i in range(int(v[1])):
                            c.append(ChannelType[v[2 + i]])
                        
                        return j, l, o, c
            
            while True:
                i = i + 1
                
                line = bvh_f.readline()
                if not line:
                    break
                
                if len(line.strip()) == 0:
                    continue
                
                vars = line.split()
                
                if parsing_step == ParsingStep.START:
                    if vars[0] != "HIERARCHY":
                        BVHLoader.parse_error(i, line)
                    
                    parsing_step = ParsingStep.HIERARCHY
                    continue
            
                elif parsing_step == ParsingStep.HIERARCHY:
                    if vars[0] != "ROOT":
                        BVHLoader.parse_error(i, line)
                    
                    name = vars[1]
                    offset = None
                    chan_list = None
                        
                    i, line, offset, chan_list = get_joint_info(i)
                    if offset is None or chan_list is None:
                        BVHLoader.parse_error(i, line)
                        break

                    joint_obj = BVHObject(name, 0, context, offset, chan_list)
                    bvh_objs.append(joint_obj)
                    bvh_obj_stack.append(joint_obj)
                    
                    parsing_step = ParsingStep.JOINT
                    continue
                
                elif parsing_step == ParsingStep.JOINT:
                    if vars[0] == "JOINT":
                        name = vars[1]
                        offset = None
                        chan_list = None
                        
                        i, line, offset, chan_list = get_joint_info(i)
                        if offset is None or chan_list is None:
                            BVHLoader.parse_error(i, line)
                            break
                        
                        parent = bvh_obj_stack[-1]
                        idx = len(bvh_objs) - 1
                        
                        joint_obj = BVHObject(name, idx, context, offset, chan_list)
                        parent.add_children(joint_obj)
                        parent.add_end_point(offset.point())
                        
                        bvh_objs.append(joint_obj)
                        bvh_obj_stack.append(joint_obj)
                        
                    elif vars[0] == "End":
                        offset = None
                        while True:
                            i = i + 1
                            l = bvh_f.readline()
                            if not l:
                                BVHLoader.parse_error(i, l)
                                
                            if len(l.strip()) == 0 or l.split()[0] == '{':
                                continue
                            
                            v = l.split()
                            
                            if v[0] == "OFFSET":
                                offset = Vec3D(float(v[1]), float(v[2]), float(v[3]))
                                continue
                            
                            if v[0] == "}":
                                if offset is None:
                                    BVHLoader.parse_error(i, l)
                                    break
                                
                                bvh_obj_stack[-1].add_end_point(offset.point())
                                bvh_obj_stack[-1].set_is_end_site(True)
                                break
                    
                    elif vars[0] == "}":
                        bvh_obj_stack.pop()
                        
                    elif vars[0] == "MOTION":
                        if len(bvh_obj_stack) > 0:
                            BVHLoader.parse_error(i, line)
                            
                        parsing_step = ParsingStep.MOTION
                        
                    else:
                        BVHLoader.parse_error(i, line)
                        
                elif parsing_step == ParsingStep.MOTION:
                    if vars[0] == "Frames:":
                        frame = int(vars[1])
                        
                    elif vars[0] == "Frame" and vars[1] == "Time:":
                        if frame == 0:
                            BVHLoader.parse_error(i, line)
                        frametime = float(vars[2])
                        parsing_step = ParsingStep.PARSE_MOTION
                    
                    else:
                        BVHLoader.parse_error(i, line)
                        
                elif parsing_step == ParsingStep.PARSE_MOTION:
                    parsed_frame = parsed_frame + 1
                    data_idx = 0
                    for jo in bvh_objs:
                        chan_num = jo.get_chan_num()
                        chan_data = []
                        for data_i in range(chan_num):
                            chan_data.append(float(vars[data_idx + data_i]))
                        jo.add_frame_data(chan_data)
                        data_idx = data_idx + chan_num 
                        
        end_time = time.time()
        
        if parsed_frame != frame:
            raise Exception(f"frame number {frame} is not matching with actual parsed lines {parsed_frame}\n")
        
        bvh_objs[0].update_global_transform()
        
        min_y = 100000
        max_y = -100000
        for jo in bvh_objs:
            if jo.is_end_site:
                max_y = max(jo.global_transform[3][1], max_y)
                min_y = min(jo.global_transform[3][1], min_y)
                
        height = max_y - min_y
        #print(f"height: {height}")
        
        bvh_objs[0].local_scale = Vec3D(2/height, 2/height, 2/height)
        
        for jo in bvh_objs:
            jo.set_line_vertices(max_y - min_y)
        
        if (print_info):
            print("---------- .bvh file info ----------")
            print(f"File name: {os.path.basename(file_path)}")
            print("")
            print(f"Number of frames: {frame}")
            print(f"FPS: {1/frametime}")
            print(f"Number of joints: {len(bvh_objs)}")
            print(f"List of Names of joints:")
            for jn in list(map(lambda o: o.name, bvh_objs)):
                print(jn)
            print("")
            print(f"Parse time: {end_time - start_time}")
            print("------------------------------------")
        
        return BVHAnimInfo(bvh_objs, frame, frametime)
                
    @staticmethod
    def parse_error(linenum, line):
        raise Exception(f"Invalid bvh file format. line: {linenum}, {line}\n")