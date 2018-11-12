class ResourceManager:
    def __init__(self):
        self.resources = []
    
    def get_resource(self, name):
        for res in self.resources:
            if res.name == name:
                return res
        else:
            new_res = Resource(name)
            self.resources.append(new_res)
            return new_res

class Resource:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data