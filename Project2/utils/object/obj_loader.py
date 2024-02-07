from typing import List, Tuple
import os, time

from ..struct import Vec3D, Face, TriangleFace, ObjectFaces, Vertex3D


class OBJLoader:
    """OBJLoader has few functions to load .obj file and convert the file
    as ObjectFaces instance to make it easier to use for rendering

    Raises
    ------
    Exception
        Raises when the obj file has invalid format
    """
    @staticmethod
    def parse_opj_file(file_path:str, print_info:bool = True) -> ObjectFaces:
        """Read obj file from given file path and return ObjectFaces instance
    
        Parameters
        -------
        file_path : str
            .obj file path as absolute path
        print_info : bool
            print the information of obj file when this set 'true'

        Returns
        -------
        ObjectFaces
            - Contains vertices and normal vectors of vertices data.
            - Faces in obj file will be automatically converted into triangles
        """
        vertices: List[Vec3D] = []
        vertex_norms: List[Vec3D] = []
        faces: List[Face] = []
        
        vertice3face_num = 0
        vertice4face_num = 0
        vertice_upper_4_face_num = 0
        
        start_time = time.time()
        with open(file_path, "r") as obj_f:
            i = -1
            
            while True:
                i = i + 1
                
                line = obj_f.readline()
                if not line:
                    break
                
                if line[0] == '#':
                    continue
                
                vars = line.split()
                
                argnum = len(vars)
                
                if argnum <= 0:
                    continue
                
                if vars[0] == 'v':
                    v = Vec3D()
                    if argnum != 4 and argnum != 5:
                        print(argnum)
                        OBJLoader.parse_error(i, line)
                    
                    v.x = float(vars[1])
                    v.y = float(vars[2])
                    v.z = float(vars[3])
                    if argnum == 5:
                        v.w = float(vars[4])
                    else:
                        v.w = 1.
                        
                    vertices.append(v)
                    
                elif vars[0] == 'vn':
                    vn = Vec3D()
                    if argnum != 4:
                        OBJLoader.parse_error(i, line)
                        
                    vn.x = float(vars[1])
                    vn.y = float(vars[2])
                    vn.z = float(vars[3])
                    
                    vertex_norms.append(vn)
                    
                elif vars[0] == 'f':
                    f = Face([])
                    
                    if argnum <= 3:
                        OBJLoader.parse_error(i, line)
                        
                    for i in range(1, len(vars)):
                        f_info = vars[i]
                        f_info = f_info.split('/')
                        
                        f_info_num = len(f_info)
                        if f_info_num == 1 or f_info_num == 2:
                            f.indices.append((int(f_info[0]) - 1, -1))
                        elif f_info_num == 3:
                            f.indices.append((int(f_info[0]) - 1, int(f_info[2]) - 1))
                        else:
                            OBJLoader.parse_error(i, line)
                            
                    if argnum == 4:
                        vertice3face_num = vertice3face_num + 1
                    elif argnum == 5:
                        vertice4face_num = vertice4face_num + 1
                    else:
                        vertice_upper_4_face_num = vertice_upper_4_face_num + 1
                    
                    faces.append(f)
                    
                else:
                    continue
        
        end_time = time.time()
        
        if (print_info):
            print("---------- .obj file info ----------")
            print(f"File name: {os.path.basename(file_path)}")
            print("")
            print(f"Total number of faces: {len(faces)}")
            print(f"Number of faces with 3 vertices: {vertice3face_num}")
            print(f"Number of faces with 4 vertices: {vertice4face_num}")
            print(f"Number of faces with more than 4 vertices: {vertice_upper_4_face_num}")
            print("")
            print(f"Parse time: {end_time - start_time}")
            print("------------------------------------")
        
        triangle_faces = OBJLoader.faces_to_triangles(faces)
        
        return ObjectFaces(vertices, vertex_norms, triangle_faces)
                
    @staticmethod
    def parse_error(linenum, line):
        raise Exception(f"Invalid obj file format. line: {linenum}, {line}\n")
    
    @staticmethod
    def faces_to_triangles(faces: List[Face]):
        triangle_faces: List[TriangleFace] = []
        for f in faces:
            for i in range(1, len(f.indices) - 1):
                tf = TriangleFace(f.indices[0], f.indices[i], f.indices[i + 1])
                triangle_faces.append(tf)
        return triangle_faces
                    
    @staticmethod
    def obj_to_vertices(obj_faces: ObjectFaces) -> List[Vertex3D]:
        vertices = []
        
        def get_pos_norm(target: Tuple[int, int]):
            norm = None if target[1] < 0 else obj_faces.ref_vertex_norm_list[target[1]]
            return obj_faces.ref_vertex_list[target[0]], norm
        
        for f in obj_faces.faces:
            for target in [f.a, f.b, f.c]:
                pos, norm = get_pos_norm(target)
                vertices.append(Vertex3D(position=pos, normal=norm))
                
        return vertices