from tinytree import Tree
from pathlib import Path
import wszst_yaz0
import sarc

def get_class_from_name(name):
    if not "." in name:
        return DirectoryNode
    elif ".sbactorpack" in name:
        return SARCNode
    else:
        return FileNode

class NamedNode(Tree):
    def __init__(self, name, children=None):
        self.name = name
        super().__init__(children)
    
    def __repr__(self):
        return self.name
    
    def get_path(self):
        path = Path()
        for node in self.pathToRoot():
            if "name" in dir(node):
                path = Path(node.name) / path
        return path
    
    def get_path_in_sarc(self):
        path = Path()
        for node in self.pathToRoot():
            if isinstance(node, SARCNode):
                break
            if "name" in dir(node):
                path = Path(node.name) / path
        return path
    
    def get_abs_path(self):
        return self.getRoot().abs_path / self.get_path()

class RootNode(Tree):
    def __init__(self, abs_path, children=None):
        self.abs_path = abs_path
        super().__init__(children)
    
    def __repr__(self):
        return repr({self.abs_path: self.children})
        
    def build_children(self):
        if self.children:
            print("Can't build children because object already has children!")
            return None
        
        for abs_path in self.abs_path.iterdir():
            name = abs_path.name
            child_class = get_class_from_name(name)
            self.addChild(child_class(name))
        return self.children
    
    def build_all_children(self, stop_at_sarc=True):
        for node in self.build_children():
            if stop_at_sarc and isinstance(node, SARCNode): continue
            if not isinstance(node, DirectoryNode): continue
            node.build_all_children(stop_at_sarc)

class FileNode(NamedNode):
    def __init__(self, name):
        self.raw_data = None
        self.data = None
        super().__init__(name, None)
    
    def addChild(self, node):
        s = "This object is a file node that cannot have children: %s"%repr(self)
        raise ValueError(s)
    
    def get_data(self):
        return self.data or self.load_data()
    
    def load_data(self):
        if not self.raw_data:
            self.raw_data = self.get_abs_path().read_bytes()
        if self.raw_data[:4] == b"Yaz0":
            self.data = wszst_yaz0.decompress(self.raw_data)
        else:
            self.data = self.raw_data
        return self.data

class DirectoryNode(NamedNode):
    def __init__(self, name, children=None):
        super().__init__(name, children)

    def __repr__(self):
        return repr({self.name: self.children})
    
    def build_children(self):
        if self.children:
            print("Can't build children because object already has children!")
            return None
        
        for node in self.pathToRoot():
            if isinstance(node, SARCNode):
                return None
        else:
            for abs_path in self.get_abs_path().iterdir():
                name = abs_path.name
                child_class = get_class_from_name(name)
                self.addChild(child_class(name))
            return self.children
    
    def build_all_children(self, stop_at_sarc=True):
        for node in self.build_children():
            if stop_at_sarc and isinstance(node, SARCNode): continue
            if not isinstance(node, DirectoryNode): continue
            node.build_all_children(stop_at_sarc)

class SARCNode(DirectoryNode):
    def __init__(self, name, children=None):
        self.raw_data = None
        super().__init__(name, children)
        
    def build_children(self):
        if self.children:
            print("Can't build children because object already has children!")
            return None
        
        if not self.raw_data:
            self.raw_data = self.get_abs_path().read_bytes()
        if self.raw_data[:4] == b"Yaz0":
            data = wszst_yaz0.decompress(self.raw_data)
        else:
            data = self.raw_data
        
        archive = sarc.SARC(data)
        path_to_node_dict = {}
        return_nodes = []
        for path_in_archive_str in archive.list_files():
            path_in_archive = Path(path_in_archive_str)
            name = path_in_archive.name
            child_class = get_class_from_name(name)
            node = child_class(name)
            node.raw_data = bytes(archive.get_file_data(path_in_archive_str))
            return_nodes.append(node)
            print(node.name)
                        
            path = path_in_archive.parent
            while path != Path():
                if path in path_to_node_dict:
                    path_to_node_dict[path].addChild(node)
                    break
                else:
                    node = DirectoryNode(path.name, [node])
                    path_to_node_dict[path] = node
                    path = path_in_archive.parent
            else:
                self.addChild(node)
        
        return return_nodes