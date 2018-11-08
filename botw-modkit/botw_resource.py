from typing import Union
import pathlib
import wszst_yaz0
import sarc

class BotwResourceManager:
    def __init__(self, dump_root_path: pathlib.Path):
        self.dump_root_path = dump_root_path
        self.resource_list = []
    
    def get_resource(self, root_path: pathlib.Path, rel_path: pathlib.Path):
        for resource in self.resource_list:
            if (resource.root_path == root_path) and (resource.rel_path == rel_path):
                return resource
        
        #No resource was found in list
        resource = BotwResource(self, root_path, rel_path, self.is_read_only_root_path(root_path))
        self.resource_list.append(resource)
        return resource
    
    def is_read_only_root_path(self, root_path: pathlib.Path):
        return (root_path == self.dump_root_path)

class BotwResource:
    def __init__(self, resource_manager: BotwResourceManager, root_path: pathlib.Path, rel_path: pathlib.Path, read_only: bool = False):
        self.resource_manager = resource_manager
        self.root_path = root_path
        self.rel_path = rel_path
        self.data = None
        self.is_yaz0_file = None
        self.read_only = read_only
        
    def set_data(self, data: Union[bytes, memoryview]):
        if self.read_only:
            print("Can't write to read-only resource!")
            return
        else:
            self.data = bytes(data)
            self.is_yaz0_file = (self.data[4] == b"Yaz0")
    
    def get_data(self):
        if self.data == None:
            self.data = self.load_data()
            if self.data[:4] == b"Yaz0":
                self.data = wszst_yaz0.decompress(self.data)
        return bytes(self.data)
    
    def load_data(self):
        load_path = self.full_path()
        if load_path.is_file():
            return load_path.read_bytes()
        else:
            current_rel_path = self.rel_path
            rel_path_list = []
            while current_rel_path != pathlib.Path("."):
                rel_path_list.append(current_rel_path)
                current_rel_path = current_rel_path.parent
            rel_path_list.reverse()
            
            for current_rel_path in rel_path_list:
                current_path = self.root_path / current_rel_path
                if current_path.is_file():
                    resource = self.resource_manager.get_resource(self.root_path, current_rel_path)
                    if resource.is_sarc():
                        archive = sarc.SARC(resource.get_data())
                        return self.load_data_from_sarc(archive, self.full_path().relative_to(current_path))
    
    def load_data_from_sarc(self, archive: sarc.SARC, path: pathlib.Path):
        current_path = path
        path_list = []
        while current_path != pathlib.Path("."):
            path_list.append(current_path)
            current_path = current_path.parent
        
        for file_name in archive.list_files():
            path_in_sarc = pathlib.Path(file_name)
            if path_in_sarc in path_list:
                data = archive.get_file_data(file_name)
                if path_in_sarc == path:
                    return bytes(data)
                elif data[:4] == b"SARC":
                    return load_data_from_sarc(sarc.SARC(data), path)
    
    def full_path(self):
        return (self.root_path / self.rel_path)
    
    def is_sarc(self):
        return (self.get_data()[:4] == b"SARC")