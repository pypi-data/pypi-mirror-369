# THIS FILE HAS BEEN GENERATED AUTOMATICALLY BY capnpy
# do not edit by hand
# generated on 2025-08-12 17:09
# cython: language_level=2

from capnpy import ptr as _ptr
from capnpy.struct_ import Struct as _Struct
from capnpy.struct_ import check_tag as _check_tag
from capnpy.struct_ import undefined as _undefined
from capnpy.enum import enum as _enum, fill_enum as _fill_enum
from capnpy.enum import BaseEnum as _BaseEnum
from capnpy.type import Types as _Types
from capnpy.segment.segment import Segment as _Segment
from capnpy.segment.segment import MultiSegment as _MultiSegment
from capnpy.segment.builder import SegmentBuilder as _SegmentBuilder
from capnpy.list import List as _List
from capnpy.list import PrimitiveItemType as _PrimitiveItemType
from capnpy.list import BoolItemType as _BoolItemType
from capnpy.list import TextItemType as _TextItemType
from capnpy.list import TextUnicodeItemType as _TextUnicodeItemType
from capnpy.list import StructItemType as _StructItemType
from capnpy.list import EnumItemType as _EnumItemType
from capnpy.list import VoidItemType as _VoidItemType
from capnpy.list import ListItemType as _ListItemType
from capnpy.anypointer import AnyPointer as _AnyPointer
from capnpy.util import text_bytes_repr as _text_bytes_repr
from capnpy.util import text_unicode_repr as _text_unicode_repr
from capnpy.util import data_repr as _data_repr
from capnpy.util import float32_repr as _float32_repr
from capnpy.util import float64_repr as _float64_repr
from capnpy.util import extend_module_maybe as _extend_module_maybe
from capnpy.util import check_version as _check_version
from capnpy.util import encode_maybe as _encode_maybe
__capnpy_id__ = 0xd435b037af9f8800
__capnpy_version__ = '0.11.1'
__capnproto_version__ = '1.0.1'
_check_version(__name__, __capnpy_version__)
from capnpy.schema import CodeGeneratorRequest as _CodeGeneratorRequest
from capnpy.annotate import Options as _Options
from capnpy.reflection import ReflectionData as _ReflectionData
class _std_msg_ReflectionData(_ReflectionData):
    request = _CodeGeneratorRequest.from_buffer(_Segment(b'\x00\x00\x00\x00\x00\x00\x04\x00\x11\x00\x00\x00\xb7\x00\x00\x00\x05\x01\x00\x00\x1f\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\xd9\x00\x00\x007\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x08\x00\x00\x00\x05\x00\x06\x00\x00\x88\x9f\xaf7\xb05\xd4\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00A\x00\x00\x00\x02\x01\x00\x00M\x00\x00\x00\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e\x92\x11h\t%<\xe2 \x00\x00\x00\x01\x00\x00\x00\x00\x88\x9f\xaf7\xb05\xd4\x01\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x005\x00\x00\x00:\x01\x00\x00E\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00A\x00\x00\x00?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00src/simpleros/msg/std_msg.capnp\x00\x04\x00\x00\x00\x01\x00\x01\x00e\x92\x11h\t%<\xe2\x01\x00\x00\x00:\x00\x00\x00String\x00\x00src/simpleros/msg/std_msg.capnp:String\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x04\x00\x00\x00\x03\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x00*\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x03\x00\x01\x00\x14\x00\x00\x00\x02\x00\x01\x00data\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x01\x00\x02\x00e\x92\x11h\t%<\xe2\x00\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x00\x0f\x00\x00\x00\x00\x88\x9f\xaf7\xb05\xd4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x01\x00\x02\x00\x00\x88\x9f\xaf7\xb05\xd4\x05\x00\x00\x00\x02\x01\x00\x00\x11\x00\x00\x00\x07\x00\x00\x00src/simpleros/msg/std_msg.capnp\x00\x00\x00\x00\x00\x01\x00\x01\x00'), 8, 0, 4)
    default_options = _Options.from_buffer(_Segment(b'\x03\x00\x02\x00\x02\x00\x03\x00'), 0, 1, 0)
    pyx = False
_reflection_data = _std_msg_ReflectionData()

#### FORWARD DECLARATIONS ####

class String(_Struct): pass
String.__name__ = 'String'


#### DEFINITIONS ####

@String.__extend__
class String(_Struct):
    __capnpy_id__ = 0xe23c250968119265
    __static_data_size__ = 0
    __static_ptrs_size__ = 1
    
    
    @property
    def data(self):
        # no union check
        return self._read_text_unicode(0)
    
    def get_data(self):
        return self._read_text_unicode(0, default_=b"")
    
    def has_data(self):
        ptr = self._read_fast_ptr(0)
        return ptr != 0
    
    @staticmethod
    def __new(data=None):
        builder = _SegmentBuilder()
        pos = builder.allocate(8)
        builder.alloc_text(pos + 0, _encode_maybe(data))
        return builder.as_string()
    
    def __init__(self, data=None):
        _buf = String.__new(data)
        self._init_from_buffer(_buf, 0, 0, 1)
    
    def shortrepr(self):
        parts = []
        if self.has_data(): parts.append("data = %s" % _text_unicode_repr(self.get_data()))
        return "(%s)" % ", ".join(parts)

_String_list_item_type = _StructItemType(String)


_extend_module_maybe(globals(), modname=__name__)