import ctypes

from threading import Lock

from pyhlml.hlml_error import HLMLError
from pyhlml.hlml_types import HLML_RETURN

class LibHLML:
    def __init__(self, path="/usr/lib/habanalabs/libhlml.so"):
        self.default_path   = path
        self.lib            = None
        self.lib_load_lock  = Lock()
        self.func_ptr_cache = dict()
        self.ref_count      = 0 # INC on init DEC on dest

        self._load_lib()

    def _load_lib(self):
        with self.lib_load_lock:
            try:
                self.lib = ctypes.CDLL(self.default_path)
            except Exception as e:
                print("Failed to load libhlml")
                raise HLMLError(HLML_RETURN.HLML_ERROR_UNINITIALIZED)

    def inc_ref(self):
        with self.lib_load_lock:
            self.ref_count += 1

    def dec_ref(self):
        if self.ref_count > 0:
            with self.lib_load_lock:
                self.ref_count -= 1

    def get_func_ptr(self, name):
        if self.lib == None:
            raise HLMLError(HLML_RETURN.HLML_ERROR_UNINITIALIZED)

        if name in self.func_ptr_cache:
            return self.func_ptr_cache[name]

        with self.lib_load_lock:
            try:
                self.func_ptr_cache[name] = getattr(self.lib, name)
                return self.func_ptr_cache[name]
            except Exception as e:
                raise HLMLError(HLML_RETURN.HLML_ERROR_INVALID_ARGUMENT)


