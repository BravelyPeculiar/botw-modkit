import pathlib
import wszst_yaz0
import sarc

class WorkspaceManager:
    def __init__(self, dump_workspace_path):
        self.dump_workspace = Workspace(self, dump_workspace_path, readonly=True)
        self.dump_workspace.build()
        self.mod_workspaces = []
    
    def new_mod_workspace(self, path, readonly = False, contents = []):
        workspace = Workspace(path, readonly, contents)
        self.mod_workspaces.append(workspace)
        return workspace

class Workspace():
    def __init__(self, manager, path, readonly=False):
        self.top_dir_res = TopDirectoryResource(self)
        self.manager = manager
        self.path = path
        self.readonly = readonly
    
    def get_res_path(self):
        return ""
    def get_abs_path(self):
        return self.path
    def get_workspace(self):
        return self
            
    def build(self):
        self.top_dir_res.build_contents()
                

class Resource:
    def __init__(self, name, parent=None):
        self.name = name
        self.set_parent(parent)
    
    def set_parent(self, parent):
        if parent:
            self.parent = parent
            parent.contents.append(self)
    
    def get_res_path(self):
        return self.parent.get_res_path() + "/" + self.name
    def get_abs_path(self):
        return self.parent.get_abs_path() / pathlib.Path(self.name)
    def get_workspace(self):
        return self.parent.get_workspace()

class DirectoryResource(Resource):
    def __init__(self, name, parent=None, contents=[]):
        self.contents = contents
        super().__init__(name, parent)
    
    def add_child(self, child):
        child.set_parent(self)
    def load_child_data(self, res_path):
        return self.parent.load_child_data(res_path)
    
    def build_contents(self):
        print("lol")
        new_contents = []
        for path in self.get_abs_path().iterdir():
            if path.is_file():
                new_resource = FileResource(path.name, self)
            if path.is_dir():
                new_resource = DirectoryResource(path.name, self)
                new_resource.build_contents()
            new_contents.append(new_resource)
        contents = new_contents

class TopDirectoryResource(DirectoryResource):
    def __init__(self, workspace, contents=[]):
        self.workspace = workspace
        super().__init__(None, None, contents)
        
    def load_child_data(self, res_path):
        return res_path.read_bytes()
    
    def get_res_path(self):
        return ""
    def get_abs_path(self):
        return self.workspace.path
    def get_workspace(self):
        return self.workspace

class FileResource(Resource):
    def __init__(self, name, parent=None):
        self.data = None
        self.is_yaz0 = None
        super().__init__(name, parent)
    
    def set_data(self, data):
        if self.readonly:
            print("Can't write to read-only resource!")
            return
        else:
            self.data = bytes(data)
    
    def get_data():
        if self.data:
            return self.data
        else:
            return self.load(data)
    
    def load_data():
        return self.parent.load_child_data(self.get_res_path())
    