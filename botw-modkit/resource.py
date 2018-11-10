from tinytree import Tree
from pathlib import Path

def get_class_from_abs_path(abs_path):
    if abs_path.is_dir():
        return DirectoryNode
    else:
        return FileNode

class RootNode(Tree):
    def __init__(self, abs_path, children=None):
        self.abs_path = abs_path
        super().__init__(children)
    
    def __repr__(self):
        return repr(self.children)
    
    def build_children(self):
        if self.children:
            print("Can't build children because object already has children!")
            return None
        
        for abs_path in self.abs_path.iterdir():
            class_name = get_class_from_abs_path(abs_path)
            self.addChild(class_name(abs_path.name))
        return self.children
    
    def build_all_children(self, stop_at_sarc=True):
        for node in self.build_children():
            if stop_at_sarc and isinstance(node, SARCNode): continue
            if not isinstance(node, DirectoryNode): continue
            node.build_all_children(stop_at_sarc)

class NamedNode(Tree):
    def __init__(self, name, children=None):
        self.name = name
        super().__init__(children)
    
    def get_path(self):
        path = Path()
        for node in self.pathToRoot():
            if "name" in dir(node):
                path = Path(node.name) / path
        return path
    
    def get_abs_path(self):
        return self.getRoot().abs_path / self.get_path()
    
class DirectoryNode(NamedNode):
    def __repr__(self):
        return repr({self.name: self.children})
        
    def build_children(self):
        if self.children:
            print("Can't build children because object already has children!")
            return None
        
        for node in self.pathToRoot():
            if isinstance(node, SARCNode):
                self.addChildrenFromList(node.build_children_of_child(self))
                return self.children
        # Not in a SARC
        for abs_path in self.get_abs_path().iterdir():
            class_name = get_class_from_abs_path(abs_path)
            self.addChild(class_name(abs_path.name))
        return self.children
    
    def build_all_children(self, stop_at_sarc=True):
        for node in self.build_children():
            if stop_at_sarc and isinstance(node, SARCNode): continue
            if not isinstance(node, DirectoryNode): continue
            node.build_all_children(stop_at_sarc)

class FileNode(NamedNode):
    def __init__(self, name, children=None):
        self.data = None
        super().__init__(name, children)
    
    def __repr__(self):
        return self.name
    
    def addChild(self, node):
        s = "This object is a file node that cannot have children: %s"%repr(self)
        raise ValueError(s)
    
    def get_data(self):
        return self.data or self.load_data()
    
    def load_data(self):
        for node in self.pathToRoot():
            if isinstance(node, SARCNode):
                self.data = node.load_data_of_child(self)
                return self.data
        # Not in a SARC
        self.data = self.get_abs_path().read_bytes()
        return self.data

class SARCNode(DirectoryNode, FileNode):
    pass