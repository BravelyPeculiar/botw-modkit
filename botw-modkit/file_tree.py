from abc import ABC
from tinytree import Tree
from pathlib import Path
from wrappers import *
import resource

def make_node_from_name(name):
    name = str(name)
    if not "." in name:
        return DirectoryNode(name)
    elif name.endswith(".sbactorpack"):
        return SARCNode(name)
    else:
        return FileNode(name)

def split_paths_gen(path):
    while path != Path():
        yield path
        path = path.parent

class TreeNode(Tree, ABC):
    def __init__(self, name):
        Tree.__init__(self)
        ABC.__init__(self)
        self.name = name
    
    def get_res_path(self):
        path = Path()
        for node in self.pathToRoot():
            path = node.name / path
        return path
    
    def get_abs_path(self):
        return self.getRoot().abs_path / self.get_res_path()
    
    def get_containing_sarc(self):
        for node in self.pathToRoot():
            if node != self and isinstance(node, SARCNode):
                return node
        else:
            return None 

class DirectoryNode(TreeNode):
    def __init__(self, name):
        super().__init__(name)
    
    def build_children_from_fs(self):
        self.clear()
        child_list = []
        for path in self.get_abs_path().iterdir():
            self.addChild(make_node_from_name(path.name))
        return self.children
    
    def build_children_from_fs_recursive(self, enter_sarcs=False):
        nodes = self.build_children_from_fs()
        for node in nodes:
            if isinstance(node, SARCNode) and not enter_sarcs:
                break
            if isinstance(node, DirectoryNode):
                node.build_children_from_fs_recursive(enter_sarcs)
    
    def get_children(self):
        if self.children == []:
            self.build_children_from_fs_recursive()
        return self.children

class RootNode(DirectoryNode):
    def __init__(self, abs_path):
        super().__init__("")
        self.abs_path = abs_path
        self.res_manager = resource.ResourceManager()
    
    def get_res_path(self):
        return Path(self)
    
    def get_abs_path(self):
        return self.abs_path
    
    def get_containing_sarc(self):
        return None

class FileNode(TreeNode):
    def __init__(self, name):
        super().__init__(name)
        self._wrapper = None
        self._resource = None
    
    @property
    def wrapper(self):
        if not self._wrapper:
            sarc_node = self.get_containing_sarc()
            if sarc_node:
                relative_path = self.get_res_path().relative_to(sarc_node.get_res_path())
                data_wrapper = FileInSARCWrapper(sarc_node.wrapper, relative_path)
            else:
                data_wrapper = FileWrapper(self.get_abs_path())
            self._wrapper = Yaz0Wrapper(data_wrapper)
        return self._wrapper
        
    @wrapper.setter
    def wrapper(self, wrapper):
        self._wrapper = wrapper
    
    @property
    def resource(self):
        if not self._resource:
            self._resource = self.getRoot().res_manager.get_resource(self.name)
        return self._resource
    
    @resource.setter
    def resource(self, resource):
        self._resource = resource
    
    def get_data(self):
        if not self.resource.data:
            self.resource.data = self.wrapper.get_data()
        return self.resource.data

class SARCNode(DirectoryNode):
    def __init__(self, name):
        super().__init__(name)
        self._wrapper = None
    
    @property
    def wrapper(self):
        if not self._wrapper:
            sarc_node = self.get_containing_sarc()
            if sarc_node:
                relative_path = self.get_res_path().relative_to(sarc_node.get_res_path())
                data_wrapper = FileInSARCWrapper(sarc_node.wrapper, relative_path)
            else:
                data_wrapper = FileWrapper(self.get_abs_path())
            yaz0_wrapper = Yaz0Wrapper(data_wrapper)
            self._wrapper = SARCWrapper(yaz0_wrapper)
        return self._wrapper
        
    @wrapper.setter
    def wrapper(self, wrapper):
        self._wrapper = wrapper
    
    def build_children_from_fs(self):
        self.clear()
        archive = self.wrapper.get_archive()
        
        dir_nodes_dict = {}
        bottom_children = []
        for path_str in archive.list_files():
            if path_str.startswith("/"):
                path_str = path_str[1:]
            split_path_list = list(split_paths_gen(Path(path_str)))
            node = make_node_from_name(split_path_list.pop(0).name)
            bottom_children.append(node)
            for path in split_path_list:
                if path in dir_nodes_dict:
                    dir_nodes_dict[path].addChild(node)
                    break
                else:
                    parent = make_node_from_name(path.name)
                    dir_nodes_dict[path] = parent
                    parent.addChild(node)
                    node = parent
            self.addChild(node)
        return bottom_children