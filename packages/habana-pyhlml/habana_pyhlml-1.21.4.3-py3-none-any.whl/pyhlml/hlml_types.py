"""
Python bindings for HLML types
"""

import ctypes

class HLML_DEVICE:
    TYPE                                    = ctypes.c_void_p

class HLML_DEFINE:
    PCI_DOMAIN_LEN                          = 9
    PCI_ADDR_LEN                            = ( PCI_DOMAIN_LEN + 10 )
    PCI_LINK_INFO_LEN                       = 10
    HL_FIELD_MAX_SIZE                       = 32
    PORTS_ARR_SIZE                          = 2
    HLML_DEVICE_ROW_RPL_MAX                 = 32
    HLML_DEVICE_MAC_MAX_ADDRESSES           = 48
    HLML_EVENT_ECC_ERR                      = ( 1 << 0 )
    HLML_EVENT_ECC_DERR                     = ( 1 << 0 )
    HLML_EVENT_CRITICAL_ERR                 = ( 1 << 1 )
    HLML_EVENT_CLOCK_RATE                   = ( 1 << 2 )
    HLML_EVENT_DRAM_ERR                     = ( 1 << 3 )
    HLML_EVENT_DRAM_DERR                    = ( 1 << 3 )
    HLML_EVENT_ECC_SERR                     = ( 1 << 4 )
    HLML_EVENT_DRAM_SERR                    = ( 1 << 5 )
    HLML_CLOCKS_THROTTLE_REASON_POWER       = ( 1 << 0 )
    HLML_CLOCKS_THROTTLE_REASON_THERMAL     = ( 1 << 1 )
    HLML_AFFINITY_SCOPE_NODE                = 0
    HLML_AFFINITY_SCOPE_SOCKET              = 1

class COMMON_DEFINE:
    VERSION_MAX_LEN                         = 128
    ETHER_ADDR_LEN                          = 6
    HABANA_LINK_CNT_MAX_NUM                 = 256
    STATUS_MAX_LEN                          = 30

class HLML_AFFINITY_SCOPE:
    TYPE                                    = ctypes.c_uint
    HLML_AFFINITY_SCOPE_NODE                = 0
    HLML_AFFINITY_SCOPE_SOCKET              = 1

class HLML_RETURN:
    TYPE                                    = ctypes.c_uint
    HLML_SUCCESS                            = 0
    HLML_ERROR_UNINITIALIZED                = 1
    HLML_ERROR_INVALID_ARGUMENT             = 2
    HLML_ERROR_NOT_SUPPORTED                = 3
    HLML_ERROR_ALREADY_INITIALIZED          = 5
    HLML_ERROR_NOT_FOUND                    = 6
    HLML_ERROR_INSUFFICIENT_SIZE            = 7
    HLML_ERROR_DRIVER_NOT_LOADED            = 9
    HLML_ERROR_TIMEOUT                      = 10
    HLML_ERROR_AIP_IS_LOST                  = 15
    HLML_ERROR_MEMORY                       = 20
    HLML_ERROR_NO_DATA                      = 21
    HLML_ERROR_UNKNOWN                      = 49

class HLML_CLOCK_TYPE:
    TYPE                                    = ctypes.c_uint
    HLML_CLOCK_SOC                          = 0
    HLML_CLOCK_IC                           = 1
    HLML_CLOCK_MME                          = 2
    HLML_CLOCK_TPC                          = 3
    HLML_CLOCK_COUNT                        = 4

class HLML_TEMP_SENS:
    TYPE                                    = ctypes.c_uint
    HLML_TEMPERATURE_ON_AIP                 = 0
    HLML_TEMPERATURE_ON_BOARD               = 1
    HLML_TEMPERATURE_OTHER                  = 2
    HLML_TEMPERATURE_HBM                    = 3
    HLML_TEMPERATURE_VRM                    = 4
    HLML_TEMPERATURE_CTEMP                  = 5

class HLML_TEMP_THRESH:
    TYPE                                    = ctypes.c_uint
    HLML_TEMPERATURE_THRESHOLD_SHUTDOWN     = 0
    HLML_TEMPERATURE_THRESHOLD_SLOWDOWN     = 1
    HLML_TEMPERATURE_THRESHOLD_MEM_MAX      = 2
    HLML_TEMPERATURE_THRESHOLD_GPU_MAX      = 3
    HLML_TEMPERATURE_THRESHOLD_COUNT        = 4

class HLML_ENABLE_STATE:
    TYPE                                    = ctypes.c_uint
    HLML_FEATURE_DISABLED                   = 0
    HLML_FEATURE_ENABLED                    = 1

class HLML_P_STATES:
    TYPE                                    = ctypes.c_uint
    HLML_PSTATE_0                           = 0
    HLML_PSTATE_1                           = 1
    HLML_PSTATE_2                           = 2
    HLML_PSTATE_3                           = 3
    HLML_PSTATE_4                           = 4
    HLML_PSTATE_5                           = 5
    HLML_PSTATE_6                           = 6
    HLML_PSTATE_7                           = 7
    HLML_PSTATE_8                           = 8
    HLML_PSTATE_9                           = 9
    HLML_PSTATE_10                          = 10
    HLML_PSTATE_11                          = 11
    HLML_PSTATE_12                          = 12
    HLML_PSTATE_13                          = 13
    HLML_PSTATE_14                          = 14
    HLML_PSTATE_15                          = 15
    HLML_PSTATE_SENTINEL                    = 16
    HLML_PSTATE_UNKNOWN                     = 32

HLML_PSTATE_NUM_SUPPORTED = HLML_P_STATES.HLML_PSTATE_SENTINEL

class HLML_MEMORY_ERROR:
    TYPE                                    = ctypes.c_uint
    HLML_MEMORY_ERROR_TYPE_CORRECTED        = 0
    HLML_MEMORY_ERROR_TYPE_UNCORRECTED      = 1
    HLML_MEMORY_ERROR_TYPE_COUNT            = 2

class HLML_MEMORY_LOCATION:
    TYPE                                    = ctypes.c_uint
    HLML_MEMORY_LOCATION_SRAM               = 0
    HLML_MEMORY_LOCATION_DRAM               = 1
    HLML_MEMORY_LOCATION_COUNT              = 2

class HLML_ECC_COUNTER:
    TYPE                                    = ctypes.c_uint
    HLML_VOLATILE_ECC                       = 0
    HLML_AGGREGATE_ECC                      = 1
    HLML_ECC_COUNTER_TYPE_COUNT             = 2

class HLML_PCIE_UTIL_COUNTER:
    TYPE                                    = ctypes.c_uint
    HLML_PCIE_UTIL_TX_BYTES                 = 0
    HLML_PCIE_UTIL_RX_BYTES                 = 1
    HLML_PCIE_UTIL_COUNT                    = 2

class HLML_EVENT_SET:
    TYPE                                    = ctypes.c_void_p

class HLML_ROW_REPLACEMENT_CAUSE:
    TYPE                                                      = ctypes.c_uint
    HLML_ROW_REPLACEMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS = 0,
    HLML_ROW_REPLACEMENT_CAUSE_DOUBLE_BIT_ECC_ERROR           = 1,
    HLML_ROW_REPLACEMENT_CAUSE_COUNT                          = 2

class HLML_PERF_POLICY:
    TYPE                                    = ctypes.c_uint
    HLML_PERF_POLICY_POWER                  = 0,
    HLML_PERF_POLICY_THERMAL                = 1,
    HLML_PERF_POLICY_COUNT                  = 0

class _struct_c_hlml_unit(ctypes.Structure):
    pass # opaque handle

class HLML_UNIT:
    TYPE                                    = _struct_c_hlml_unit

class _PrintS(ctypes.Structure):
    """
    Produces nicer __str__ output than ctypes.Structure.

    e.g. instead of:

    > print str(obj)
    <class_name object at 0x7fdf82fef9e0>

    this class will print...

    > print str(obj)
    class_name(field_name: formatted_value, field_name: formatted_value)
    _fmt_ dictionary of <str _field_ name> -> <str format>

    Default formatting string for all fields can be set with key "<default>" like:
      _fmt_ = {"<default>" : "%d MHz"} # e.g all values are numbers in MHz.

    If not set it's assumed to be just "%s"

    e.g. class that has _field_ 'hex_value', c_uint could be formatted with
      _fmt_ = {"hex_value" : "%08X"}
    to produce nicer output.
    """
    _fmt_ = {}
    def __str__(self):
        result = []
        for x in self._fields_:
            key = x[0]
            value = getattr(self, key)
            fmt = "%s"
            if key in self._fmt_:
                fmt = self._fmt_[key]
            elif "<default>" in self._fmt_:
                fmt = self._fmt_["<default>"]
            result.append(("%s: " + fmt) % (key, value))
        return self.__class__.__name__ + "(" +  ", ".join(result) + ")"

class c_hlml_pci_cap(_PrintS):
    _fields_ = [("link_speed", ctypes.c_char * HLML_DEFINE.PCI_LINK_INFO_LEN),
                ("link_width",ctypes.c_char * HLML_DEFINE.PCI_LINK_INFO_LEN),
                ("link_max_speed", ctypes.c_char * HLML_DEFINE.PCI_LINK_INFO_LEN),
                ("link_max_width",ctypes.c_char * HLML_DEFINE.PCI_LINK_INFO_LEN)
               ]

class c_hlml_pci_info(_PrintS):
    """
    /*
        * bus - The bus on which the device resides, 0 to 0xf
        * bus_id - The tuple domain:bus:device.function
        * device - The device's id on the bus, 0 to 31
        * domain - The PCI domain on which the device's bus resides
        * pci_device_id - The combined 16b deviceId and 16b vendor id
        * pci_subsys_device_id - The combined 16b subsys_id and 16b subsys_vendor_id
    */
    """
    _fields_ = [("bus", ctypes.c_uint),
                ("bus_id", ctypes.c_char * HLML_DEFINE.PCI_ADDR_LEN),
                ("device", ctypes.c_uint),
                ("domain", ctypes.c_uint),
                ("pci_device_id", ctypes.c_uint),
                ("caps", c_hlml_pci_cap),
                ("pci_rev", ctypes.c_uint),
                ("pci_subsys_id", ctypes.c_uint)
               ]

class c_hlml_utilization(_PrintS):
    _fields_ = [("aip", ctypes.c_uint),
                ("memory", ctypes.c_uint)
               ]

class c_hlml_process_utilization(_PrintS):
    _fields_ = [("aip_util", ctypes.c_uint)
               ]

class c_hlml_memory(_PrintS):
    _fields_ = [("free", ctypes.c_ulonglong),
                ("total", ctypes.c_ulonglong),
                ("used", ctypes.c_ulonglong)
               ]

class c_hlml_pcb_info(_PrintS):
    _fields_ = [("pcb_ver", ctypes.c_char * HLML_DEFINE.HL_FIELD_MAX_SIZE),
                ("pcb_assembly_ver", ctypes.c_char * HLML_DEFINE.HL_FIELD_MAX_SIZE)
               ]

class c_hlml_event_data(_PrintS):
    _fields_ = [("device", ctypes.c_void_p),
                ("event_type", ctypes.c_ulonglong)
               ]

class c_hlml_mac_info(_PrintS):
    _fields_ = [("addr", ctypes.c_ubyte * COMMON_DEFINE.ETHER_ADDR_LEN), # unsigned char
                ("id", ctypes.c_int)
               ]

class c_hlml_nic_stats_info(_PrintS):
    _fields_ = [("port", ctypes.c_uint32),
                ("str_buf", ctypes.POINTER(ctypes.c_char)),
                ("val_buf", ctypes.POINTER(ctypes.c_uint64)),
                ("num_of_counters_out", ctypes.POINTER(ctypes.c_uint32))
                ]

    def __init__(self, port: int, num_of_counters: int = None):
        num_of_counters = num_of_counters or COMMON_DEFINE.HABANA_LINK_CNT_MAX_NUM
        self.port = port

        str_buf_size = num_of_counters * 32
        self.str_buf = ctypes.cast(ctypes.create_string_buffer(str_buf_size), ctypes.POINTER(ctypes.c_char))

        val_buf_size = num_of_counters * ctypes.sizeof(ctypes.c_uint64)
        self.val_buf = (ctypes.c_uint64 * val_buf_size)()

        self.num_of_counters_out = (ctypes.c_uint32 * 1)()

class c_hlml_violation_time(_PrintS):
    _fields_ = [("reference_time", ctypes.c_ulonglong),
                ("violation_time", ctypes.c_ulonglong)
               ]

class c_hlml_row_address(_PrintS):
    _fields_ = [("hbm_idx", ctypes.c_uint8),
                ("pc", ctypes.c_uint8),
                ("sid", ctypes.c_uint8),
                ("bank_idx", ctypes.c_uint8),
                ("row_addr", ctypes.c_uint16)
               ]

class hlml_ecc_mode(_PrintS):
    _fields_ = [("current", ctypes.c_uint),
                ("pending", ctypes.c_uint)
               ]

## Alternative object
# Allows the object to be printed
# Allows mismatched types to be assigned
#  - like None when the Structure variant requires c_uint

class hlml_friendly_obj(object):
    def __init__(self, dic):
        for x in dic:
            setattr(self, x, dic[x])
    def __str__(self):
        return self.__dict__.__str__()

def hlml_struct_to_friendly(struct):
    dic = {}
    for x in struct._fields_:
        key = x[0]
        value = getattr(struct, key)
        dic[key] = value
    obj = hlml_friendly_obj(dic)
    return obj

def hlml_friendly_to_struct(obj, model):
    for x in model._fields_:
        key = x[0]
        value = obj.__dict__[key]
        setattr(model, key, value)
    return model
