"""
Binary Reader for OpenTTD Save Files

Low-level binary reading.
"""

import struct
from typing import Any, Optional
from enum import IntEnum


class SaveLoadType(IntEnum):
    SLE_FILE_END = 0
    SLE_FILE_I8 = 1
    SLE_FILE_U8 = 2
    SLE_FILE_I16 = 3
    SLE_FILE_U16 = 4
    SLE_FILE_I32 = 5
    SLE_FILE_U32 = 6
    SLE_FILE_I64 = 7
    SLE_FILE_U64 = 8
    SLE_FILE_STRINGID = 9
    SLE_FILE_STRING = 10
    SLE_FILE_STRUCT = 11

    SLE_FILE_TYPE_MASK = 0x0F
    SLE_FILE_HAS_LENGTH_FIELD = 0x10


class ChunkType(IntEnum):
    CH_RIFF = 0
    CH_ARRAY = 1
    CH_SPARSE_ARRAY = 2
    CH_TABLE = 3
    CH_SPARSE_TABLE = 4


class BinaryReader:
    """Low-level binary reader"""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_byte(self) -> int:
        """SlReadByte implementation"""
        if self.pos >= len(self.data):
            raise ValueError("End of data")
        val = self.data[self.pos]
        self.pos += 1
        return val

    def read_bytes(self, count: int) -> bytes:
        """Read multiple bytes"""
        if self.pos + count > len(self.data):
            raise ValueError(f"Not enough data: need {count}, have {len(self.data) - self.pos}")
        result = self.data[self.pos : self.pos + count]
        self.pos += count
        return result

    def sl_read_uint16(self) -> int:
        """SlReadUint16"""
        x = self.read_byte() << 8
        return x | self.read_byte()

    def sl_read_uint16_signed(self) -> int:
        """Read uint16 and convert to signed int16"""
        val = self.sl_read_uint16()
        if val > 32767:
            return val - 65536
        return val

    def sl_read_uint32(self) -> int:
        """SlReadUint32"""
        x = self.sl_read_uint16() << 16
        return x | self.sl_read_uint16()

    def sl_read_uint32_signed(self) -> int:
        """Read uint32 and convert to signed int32"""
        val = self.sl_read_uint32()
        if val > 2147483647:
            return val - 4294967296
        return val

    def sl_read_uint64(self) -> int:
        """SlReadUint64"""
        x = self.sl_read_uint32()
        y = self.sl_read_uint32()
        return (x << 32) | y

    def sl_read_uint64_signed(self) -> int:
        """Read uint64 and convert to signed int64"""
        val = self.sl_read_uint64()
        if val > 9223372036854775807:
            return val - 18446744073709551616
        return val

    def sl_read_simple_gamma(self) -> int:
        """SlReadSimpleGamma"""
        i = self.read_byte()
        if i & 0x80:  # HasBit(i, 7)
            i &= ~0x80
            if i & 0x40:  # HasBit(i, 6)
                i &= ~0x40
                if i & 0x20:  # HasBit(i, 5)
                    i &= ~0x20
                    if i & 0x10:  # HasBit(i, 4)
                        i &= ~0x10
                        if i & 0x08:  # HasBit(i, 3)
                            raise ValueError("Unsupported gamma")
                        i = self.read_byte()  # 32 bits only
                    i = (i << 8) | self.read_byte()
                i = (i << 8) | self.read_byte()
            i = (i << 8) | self.read_byte()
        return i

    def sl_save_load_conv(self, var_type: int) -> Any:
        """SlSaveLoadConv"""
        file_type = var_type & SaveLoadType.SLE_FILE_TYPE_MASK
        has_length = bool(var_type & SaveLoadType.SLE_FILE_HAS_LENGTH_FIELD)

        # Handle length field if present
        length = None
        if has_length:
            length = self.sl_read_simple_gamma()
            print(f"    Has length field: {length} bytes")

        if file_type == SaveLoadType.SLE_FILE_I8:
            return struct.unpack("<b", self.read_bytes(1))[0]
        elif file_type == SaveLoadType.SLE_FILE_U8:
            return self.read_byte()
        elif file_type == SaveLoadType.SLE_FILE_I16:
            return self.sl_read_uint16_signed()
        elif file_type == SaveLoadType.SLE_FILE_U16:
            return self.sl_read_uint16()
        elif file_type == SaveLoadType.SLE_FILE_I32:
            return self.sl_read_uint32_signed()
        elif file_type == SaveLoadType.SLE_FILE_U32:
            return self.sl_read_uint32()
        elif file_type == SaveLoadType.SLE_FILE_I64:
            return self.sl_read_uint64_signed()
        elif file_type == SaveLoadType.SLE_FILE_U64:
            return self.sl_read_uint64()
        elif file_type == SaveLoadType.SLE_FILE_STRINGID:
            return self.sl_read_uint16()
        elif file_type == SaveLoadType.SLE_FILE_STRING:
            if has_length and length is not None:
                if length == 0:
                    return ""
                string_data = self.read_bytes(length)
                return string_data.decode("utf-8", errors="replace")
            else:
                return self.sl_std_string()
        elif file_type == SaveLoadType.SLE_FILE_STRUCT:
            if has_length:
                struct_length = self.sl_read_simple_gamma()
                self.read_bytes(struct_length)
                return {"<struct>": f"skipped {struct_length} bytes"}
            return {"<struct>": "no length specified"}
        else:
            raise ValueError(f"Unknown file type: {file_type} (var_type=0x{var_type:02x})")

    def sl_std_string(self) -> str:
        """SlStdString"""
        length_pos = self.pos
        length = self.sl_read_simple_gamma()
        print(f"      String length: {length} (read from pos 0x{length_pos:x} to 0x{self.pos:x})")

        if length == 0:
            return ""

        string_pos = self.pos
        string_data = self.read_bytes(length)
        print(
            f"      String data: {string_data[:50]!r}{'...' if len(string_data) > 50 else ''} (read from pos 0x{string_pos:x} to 0x{self.pos:x})"
        )
        return string_data.decode("utf-8", errors="replace")

    def sl_std_string_exact(self) -> str:
        """SlStdString"""
        length = self.sl_read_simple_gamma()
        print(f"      String length: {length}")

        if length == 0:
            return ""

        string_data = self.read_bytes(length)
        print(f"      String data: {string_data[:50]!r}{'...' if len(string_data) > 50 else ''}")
        return string_data.decode("utf-8", errors="replace")

    def find_chunk(self, chunk_id: bytes) -> Optional[int]:
        """Find chunk by ID"""
        return self.data.find(chunk_id) if chunk_id in self.data else None
