from abc import ABC, abstractmethod
import wszst_yaz0
import sarc

class DataWrapper(ABC):
    def __init__(self):
        self._cache = None
    
    @abstractmethod
    def get_data(self):
        if not self._cache:
            self._cache = "do something"
        return self._cache
    
    def get_data_clear(self):
        buf = self.get_data()
        self.clear()
        return buf
    
    def clear(self):
        self._cache = None

class FileWrapper(DataWrapper):
    def __init__(self, path):
        self.path = path
        self._cache = None
    
    def get_data(self):
        if not self._cache:
            self._cache = self.path.read_bytes()
        return self._cache

class FileInSARCWrapper(DataWrapper):
    def __init__(self, sarc_wrapper, path_in_sarc):
        self._sarc_wrapper = sarc_wrapper
        self._path_in_sarc = path_in_sarc
        self._cache = None
    
    def get_data(self):
        if not self._cache:
            self._cache = self._sarc_wrapper.get_subfile_data(self._path_in_sarc)
        return self._cache
    
class Yaz0Wrapper(DataWrapper):
    def __init__(self, data_wrapper):
        self._data_wrapper = data_wrapper
        self._cache = None
    
    def get_data(self):
        if not self._cache:
            buf = self._data_wrapper.get_data_clear()
            if buf[:4] == b"Yaz0":
                buf = wszst_yaz0.decompress(buf)
            self._cache = buf
        return self._cache

class SARCWrapper():
    def __init__(self, data_wrapper):
        self._data_wrapper = data_wrapper
        self._archive = None
        self._leading_slash = False
    
    def get_archive(self):
        if not self._archive:
            buf = self._data_wrapper.get_data_clear()
            self._archive = sarc.SARC(buf)
            if list(self._archive.list_files())[0].startswith("/"):
                self._leading_slash = True
        return self._archive
    
    def get_subfile_data(self, path_in_sarc):
        path_str = str(path_in_sarc).replace("\\", "/")
        if self._leading_slash:
            path_str = "/" + path_str
        return bytes(self._archive.get_file_data(path_str))