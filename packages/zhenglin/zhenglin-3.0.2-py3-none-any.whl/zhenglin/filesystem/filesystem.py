import os
import sys
import shutil

from os.path import join, exists, isdir, isfile, split, splitext, basename, dirname
from os import listdir, makedirs, remove, rmdir, walk

from tqdm import tqdm

'''
https://www.notion.so/aidenpan/Zhenlin-Package-Filesystem-1ff1fd8a2cba800d81a5ed87834f2da5?pvs=4
'''

'''
TODO List
---state read---
---state write---
1. save file
---state convert---
1. file_system_convert
---state delete---


'''

class FileSystem():
    def __init__(self,):
        '''Args:
            project (str): project name, e.g., 'project', or a directory path. './path/to/project'
            sub (str): subject name, e.g., 'sks', the file will be saved in the directory './path/to/project/sks'
            file_system (str): file system type, choose one from 'T3', 'T2', 'F3', 'F2', 'A1'
        '''
        self.project = None
        self.sub = None
        self.file_system = None
        self.overwrite = False

    def init(self, project=None, sub='', file_system='T3', overwrite=False):
        self.project = project
        self.sub = sub
        self.file_system = file_system
        self.overwrite = overwrite

    def new(self, path_ref, index=None):
        
        if self.file_system == 'T3':
            _, fname = split(path_ref)
            if index is None:
                vname, iname = fname.split(':')
            else:
                vname = fname
                iname = f'{index:06d}.png' if isinstance(index, int) else index
            path_new = join(self.project, self.sub, vname, iname)

        elif self.file_system == 'T2':
            _, fname = split(path_ref)
            path_new = join(self.project, self.sub, fname)
        
        elif self.file_system == 'F3':
            _, fname = split(path_ref)
            if index is None:
                vname, iname = fname.split(':')
            else:
                vname = fname
                iname = f'{index:06d}.png' if isinstance(index, int) else index
            path_new = join(self.project, vname, self.sub, iname)
        
        elif self.file_system == 'F2':
            _, fname = split(path_ref)
            path_new = join(self.project, fname, self.sub)
        
        elif self.file_system == 'A1':
            raise NotImplementedError("File system 'A1' is not implemented yet.")
        
        else:
            raise ValueError(f"Unknown file system type: {self.file_system}")
        
        os.makedirs(dirname(path_new), exist_ok=True)
        return path_new

    @staticmethod
    def convert(action, root_src, root_dst):
        if action == 'F3->T3':
            folderlist = listdir(root_src)
            typelist = listdir(join(root_src, folderlist[0]))
            pbar = tqdm(total=len(folderlist) * len(typelist), desc='Converting F3->T3')
            for t in typelist:
                for f in folderlist:
                    src = join(root_src, f, t)
                    dst = join(root_dst, t, f)
                    makedirs(dst, exist_ok=True)
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    pbar.update(1)
        elif action == 'T3->F3':
            typelist = listdir(root_src)
            folderlist = listdir(join(root_src, typelist[0]))
            pbar = tqdm(total=len(folderlist) * len(typelist), desc='Converting T3->F3')
            for folder in folderlist:
                for t in typelist:
                    src = join(root_src, t, folder)
                    dst = join(root_dst, folder, t)
                    makedirs(dst, exist_ok=True)
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    pbar.update(1)
        else:
            raise NotImplementedError(f"Action '{action}' is not implemented yet.")
    
    def all_files(self):
        from glob import glob
        return glob(join(self.project, self.sub, '**', '*.*'), recursive=True)

    def get_fsdict(self, root):
        from collections import defaultdict

        if self.file_system == 'T3' or 'F3':
            fsdict = defaultdict(dict)
            for folder in listdir(root):
                for fname in listdir(join(root, folder)):
                    fsdict[folder][fname] = join(root, folder, fname)
            return fsdict

        elif self.file_system == 'T2' or 'F2':
            fsdict = defaultdict()
            for fname in listdir(root):
                fsdict[fname] = join(root, fname)
            return fsdict

        elif self.file_system == 'A1':
            for fname in listdir(root):
                return {fname: join(root, fname)}

if __name__=="__main__":
    
    ### example usage

    # # from zhenglin.filesystem import filesystem
    # # fs = filesystem.FileSystem()
    fs = FileSystem()

    ### CASE 1 - NOT TESTED

    import cv2
    import numpy as np

    fs.init(project='project', file_system='F2', overwrite=True,)

    # path_img = r'C:\Users\Lenovo\Desktop\001-POT01_001_0036_37-PAINT-B\gt\0009.png'
    path_img = r'D:\stable-diffusion-webui-master\training-picker\videos\aaa\vid.mp4:0000.png'
    # img = cv2.imread(path_img)

    path_out = fs(path_img)

    print(f'Converted image path: {path_out}')
    # cv2.imwrite(path_out, img)

    ### CASE 2 - NOT TESTED
    
    # dir_src = r'C:\Users\Lenovo\Desktop\test'
    # dir_dst = r'C:\Users\Lenovo\Desktop\test_converted'
    # fs.convert('F3->T3', dir_src, dir_dst)
    # dir_src = r'C:\Users\Lenovo\Desktop\test_converted'
    # dir_dst = r'C:\Users\Lenovo\Desktop\test_back'
    # fs.convert('T3->F3', dir_src, dir_dst)