"""
OpenTTD Save File Parser

High-level save file parsing following OpenTTD's exact loading sequence.
"""

import struct
import lzma
from typing import Dict, List, Any, Optional, Tuple

from .binary_reader import BinaryReader, ChunkType, SaveLoadType
from .data_formatters import (
    convert_date_to_year,
    convert_date_to_ymd,
    format_inflation_value,
    format_company_data,
)


class SaveLoader:
    """OpenTTD save loader"""

    def __init__(self, filename: str, silent: bool = True):
        self.filename = filename
        self.silent = silent
        self.data: bytes = b""
        self.save_version: int = 0
        self.minor_version: int = 0
        self.reader: Optional[BinaryReader] = None
        self.__post_init__()

    def debug_print(self, message: str) -> None:
        """Print debug message only if not in silent mode"""
        if not self.silent:
            print(message)

    def __post_init__(self) -> None:
        """Initialize state variables after object creation"""
        self.block_mode: ChunkType = ChunkType.CH_RIFF
        self.array_index: int = 0
        self.obj_len: int = 0
        self.next_offs: int = 0
        self.expect_table_header: bool = False

    def load_and_decompress(self) -> None:
        """Load and decompress save file"""
        with open(self.filename, "rb") as f:
            header = f.read(8)
            tag = header[:4]
            version_data = header[4:]

            # Parse version (big endian)
            version_int = struct.unpack(">I", version_data)[0]
            self.save_version = (version_int >> 16) & 0xFFFF
            self.minor_version = (version_int >> 8) & 0xFF

            print(f"OpenTTD Save Version: {self.save_version}")
            print(f"Format: {tag.decode('ascii', errors='replace')}")

            if tag == b"OTTX":
                compressed_data = f.read()
                self.data = lzma.decompress(compressed_data, format=lzma.FORMAT_AUTO)
                print(f"Decompressed LZMA data: {len(self.data):,} bytes")
            else:
                self.data = f.read()
                print(f"Raw data: {len(self.data):,} bytes")

        # Create binary reader
        self.reader = BinaryReader(self.data)

    def sl_iterate_array(self) -> Optional[int]:
        """SlIterateArray implementation"""
        if not self.reader:
            return None

        # After reading in the whole array inside the loop we must have read in all the data,
        # so we must be at end of current block.
        if self.next_offs != 0 and self.reader.pos != self.next_offs:
            print(
                f"Warning: Invalid chunk size iterating array - expected to be at position {self.next_offs}, actually at {self.reader.pos}"
            )

        # for (;;) { - infinite loop until length == 0
        while True:
            try:
                # uint length = SlReadArrayLength();
                if self.reader.pos >= len(self.reader.data):
                    print(f"  SlIterateArray: reached end of data at pos 0x{self.reader.pos:x}")
                    return None

                start_pos = self.reader.pos
                length = self.reader.sl_read_simple_gamma()
                print(f"  SlIterateArray: read length={length} at pos 0x{start_pos:x}")

                # if (length == 0) {
                if length == 0:
                    print(f"  SlIterateArray: length=0, ending iteration")
                    self.next_offs = 0
                    return None  # return -1 in C++

                # _sl.obj_len = --length;
                self.obj_len = length - 1

                # _next_offs = _sl.reader->GetSize() + length;
                # In C++ GetSize() returns bytes read so far, which is our current position
                self.next_offs = self.reader.pos + self.obj_len

                print(f"  SlIterateArray: obj_len={self.obj_len}, next_offs=0x{self.next_offs:x}")

                # if (_sl.expect_table_header) {
                if hasattr(self, "expect_table_header") and self.expect_table_header:
                    print(f"  SlIterateArray: returning table header sentinel")
                    self.expect_table_header = False
                    return 2147483647  # INT32_MAX

                # switch (_sl.block_mode) {
                if self.block_mode in (ChunkType.CH_SPARSE_TABLE, ChunkType.CH_SPARSE_ARRAY):
                    # index = (int)SlReadSparseIndex();
                    index = self.reader.sl_read_simple_gamma()
                    print(f"  SlIterateArray: sparse index={index}")
                elif self.block_mode in (ChunkType.CH_TABLE, ChunkType.CH_ARRAY):
                    # index = _sl.array_index++;
                    index = self.array_index
                    self.array_index += 1
                    print(f"  SlIterateArray: array index={index}")
                else:
                    print("SlIterateArray error")
                    return None

                # if (length != 0) return index;
                if self.obj_len != 0:  # obj_len = length - 1
                    print(f"  SlIterateArray: returning index={index} with obj_len={self.obj_len}")
                    return index
                # Otherwise continue the loop (empty object)
                print(f"  SlIterateArray: empty object, continuing loop")

            except Exception as e:
                print(f"Exception in sl_iterate_array: {e}")
                import traceback

                traceback.print_exc()
                return None

    def sl_table_header(self) -> List[Tuple[str, int]]:
        """SlTableHeader implementation"""
        if not self.reader:
            return []

        saveloads = []

        print(f"  Starting table header at pos 0x{self.reader.pos:x}")

        while True:
            # Read field type
            if self.reader.pos >= len(self.reader.data):
                raise ValueError("End of data while reading table header")

            field_type = self.reader.read_byte()
            print(f"    Read field_type: 0x{field_type:02x} at pos 0x{self.reader.pos-1:x}")

            # Check for end marker
            if field_type == SaveLoadType.SLE_FILE_END:
                print(f"    Found SLE_FILE_END, ending table header")
                break

            # Read field name
            field_name = self.reader.sl_std_string_exact()
            print(f"    Field name: '{field_name}' (len={len(field_name)})")

            # Add the field as found in the save file
            # We accept all fields from the save file and will handle unknown ones during loading
            saveloads.append((field_name, field_type))
            print(f"    Added field: '{field_name}' type=0x{field_type:02x}")

            # Handle nested structures
            if (field_type & SaveLoadType.SLE_FILE_TYPE_MASK) == SaveLoadType.SLE_FILE_STRUCT:
                print(
                    f"    Field '{field_name}' is a struct - recursively processing struct table header"
                )
                # The C++ code calls SlTableHeader recursively for struct fields
                struct_fields = self.sl_table_header()  # Process the nested struct table header
                print(
                    f"    Struct '{field_name}' table header processed: {len(struct_fields)} fields"
                )

        print(f"  Table header processed: {len(saveloads)} valid fields")
        return saveloads

    def sl_object(self, index: int, fields: List[Tuple[str, int]]) -> Dict[str, Any]:
        """SlObject implementation"""
        if not self.reader:
            return {}

        # Explicitly type as Any so different shapes are allowed
        obj: Dict[str, Any] = {"index": index}
        start_pos = self.reader.pos

        print(
            f"    SlObject: reading object {index} at pos 0x{start_pos:x}, obj_len={self.obj_len}"
        )
        print(f"    Expected to read until pos 0x{self.next_offs:x}")

        field_count = 0
        for field_name, field_type in fields:
            if self.reader.pos >= self.next_offs:
                print(f"    Reached object boundary at field '{field_name}', stopping")
                break

            field_count += 1
            try:
                print(
                    f"    [{field_count:2d}] Reading field '{field_name}' (type=0x{field_type:02x}) at pos 0x{self.reader.pos:x}"
                )

                if field_type == SaveLoadType.SLE_FILE_STRUCT:
                    obj[field_name] = {"<struct>": "nested processing required"}

                elif field_name == "yearly_expenses" and (
                    field_type & SaveLoadType.SLE_FILE_HAS_LENGTH_FIELD
                ):
                    array_length = self.reader.sl_read_simple_gamma()
                    print(f"      yearly_expenses array length: {array_length}")
                    expenses: List[int] = []
                    for i in range(array_length):
                        if self.reader.pos + 8 <= self.next_offs:
                            expense = self.reader.sl_read_uint64_signed()
                            expenses.append(expense)
                        else:
                            break
                    obj[field_name] = expenses
                    print(f"      Read {len(expenses)} expense entries")

                else:
                    value = self.reader.sl_save_load_conv(field_type)
                    obj[field_name] = value

                    if isinstance(value, str) and len(value) > 50:
                        print(f"      {field_name} = '{value[:50]}...' (truncated)")
                    else:
                        print(f"      {field_name} = {value}")

            except Exception as e:
                obj[field_name] = f"<error: {e}>"
                print(f"      Error reading field '{field_name}': {e}")
                continue

        # Ensure we're positioned correctly at the end of this object
        if self.reader.pos < self.next_offs:
            remaining = self.next_offs - self.reader.pos
            print(f"    Skipping {remaining} remaining bytes to reach object boundary")
            self.reader.read_bytes(remaining)
        elif self.reader.pos > self.next_offs:
            print(
                f"    Warning: Read past object boundary by {self.reader.pos - self.next_offs} bytes"
            )

        print(f"    SlObject completed: {field_count} fields processed")
        return obj

    def parse_maps_chunk(self) -> Dict[str, Any]:
        """Parse MAPS chunk"""
        if not self.reader:
            return {}

        pos = self.reader.find_chunk(b"MAPS")
        if pos is None:
            return {}

        print(f"\\nParsing MAPS chunk at 0x{pos:x}")

        # Set position and chunk mode
        self.reader.pos = pos + 4  # Skip chunk ID
        chunk_type = self.reader.read_byte()
        self.block_mode = ChunkType(chunk_type & 0x0F)
        print(f"Read chunk type byte: 0x{chunk_type:02x}, block_mode: {self.block_mode.name}")

        print(f"Chunk type: {self.block_mode.name}")

        # For table chunks, skip the length field before the table header
        if self.block_mode == ChunkType.CH_TABLE:
            table_length = self.reader.sl_read_simple_gamma()
            print(f"Table length: {table_length}")

        # Reset array index
        self.array_index = 0

        # Read table header (SlCompatTableHeader calls SlTableHeader for CH_TABLE)
        fields = self.sl_table_header()

        # Read the single map data entry
        index = self.sl_iterate_array()
        if index is None:
            return {}

        print(f"Reading map data at index {index}")

        # Read map fields
        result = {}
        for field_name, field_type in fields:
            try:
                value = self.reader.sl_save_load_conv(field_type)
                result[field_name] = value
                print(f"  {field_name} = {value}")
            except Exception as e:
                print(f"Error reading field {field_name}: {e}")
                break

        return result

    def parse_companies_chunk(self) -> List[Dict[str, Any]]:
        """Parse PLYR"""
        if not self.reader:
            return []

        pos = self.reader.find_chunk(b"PLYR")
        if pos is None:
            return []

        print(f"\\nParsing PLYR chunk at 0x{pos:x}")

        # Set position and chunk mode
        self.reader.pos = pos + 4  # Skip chunk ID
        chunk_type = self.reader.read_byte()
        self.block_mode = ChunkType(chunk_type & 0x0F)

        # Skip the table length field
        table_length = self.reader.sl_read_simple_gamma()
        print(f"Table length: {table_length}")

        # SlCompatTableHeader(_company_desc, _company_sl_compat)
        fields = self.sl_table_header()
        print(f"Table header parsed: {len(fields)} fields")

        # while ((index = SlIterateArray()) != -1) {
        self.array_index = 0
        self.next_offs = 0
        companies = []

        print(f"Starting company iteration at pos 0x{self.reader.pos:x}")

        iteration_count = 0
        while True:
            index = self.sl_iterate_array()
            if index is None:
                break

            iteration_count += 1
            print(
                f"\\nIteration {iteration_count}: index={index}, obj_len={self.obj_len}, pos=0x{self.reader.pos:x}"
            )

            # Based on OpenTTD code, ALL objects should be processed with SlObject
            # The nested structures are handled within SlObject, not skipped
            print(f"  Processing object with obj_len={self.obj_len}")

            # SlObject(c, slt) - read object using the field list
            try:
                company = self.sl_object(index, fields)

                # Only add to companies list if it has actual company data
                name = company.get("name", "")
                # A company is valid if it has any of: name, money data, or AI status
                has_financial_data = "money" in company or "current_loan" in company
                has_basic_data = "name_1" in company or "name_2" in company

                if has_financial_data or has_basic_data:
                    companies.append(company)
                    is_ai = company.get("is_ai", False)
                    money = company.get("money", 0)
                    display_name = name if name else f"Company #{company.get('index', '?')}"
                    print(f"  Company: {display_name} (AI: {is_ai}, Money: ${money:,})")
                else:
                    print(f"  Schema/nested structure processed")

            except Exception as e:
                print(f"  Error reading object {index}: {e}")
                # Skip remaining data for this object to continue iteration
                if self.obj_len > 0:
                    remaining = self.next_offs - self.reader.pos
                    if remaining > 0:
                        self.reader.read_bytes(remaining)
                continue

        print(
            f"\\nTable iteration ended at pos 0x{self.reader.pos:x}, found {len(companies)} companies"
        )
        return companies

    def parse_date_chunk(self) -> Dict[str, Any]:
        """Parse DATE"""
        if not self.reader:
            return {}

        pos = self.reader.find_chunk(b"DATE")
        if pos is None:
            return {}

        print(f"\nParsing DATE chunk at 0x{pos:x}")

        # Set position and chunk mode
        self.reader.pos = pos + 4  # Skip chunk ID
        chunk_type = self.reader.read_byte()
        self.block_mode = ChunkType(chunk_type & 0x0F)
        print(f"Read chunk type byte: 0x{chunk_type:02x}, block_mode: {self.block_mode.name}")

        # For table chunks, skip the length field before the table header
        if self.block_mode == ChunkType.CH_TABLE:
            table_length = self.reader.sl_read_simple_gamma()
            print(f"Table length: {table_length}")

        # Reset array index
        self.array_index = 0

        # Read table header
        fields = self.sl_table_header()

        # Read the single date data entry
        index = self.sl_iterate_array()
        if index is None:
            return {}

        print(f"Reading date data at index {index}")

        # Read date fields
        result = {}
        for field_name, field_type in fields:
            try:
                value = self.reader.sl_save_load_conv(field_type)
                result[field_name] = value
                print(f"  {field_name} = {value}")
            except Exception as e:
                print(f"Error reading field {field_name}: {e}")
                break

        return result

    def parse_economy_chunk(self) -> Dict[str, Any]:
        """Parse ECMY"""
        if not self.reader:
            return {}

        pos = self.reader.find_chunk(b"ECMY")
        if pos is None:
            return {}

        print(f"\nParsing ECMY chunk at 0x{pos:x}")

        # Set position and chunk mode
        self.reader.pos = pos + 4  # Skip chunk ID
        chunk_type = self.reader.read_byte()
        self.block_mode = ChunkType(chunk_type & 0x0F)
        print(f"Read chunk type byte: 0x{chunk_type:02x}, block_mode: {self.block_mode.name}")

        # For table chunks, skip the length field before the table header
        if self.block_mode == ChunkType.CH_TABLE:
            table_length = self.reader.sl_read_simple_gamma()
            print(f"Table length: {table_length}")

        # Reset array index
        self.array_index = 0

        # Read table header
        fields = self.sl_table_header()

        # Read the single economy data entry
        index = self.sl_iterate_array()
        if index is None:
            return {}

        print(f"Reading economy data at index {index}")

        # Read economy fields
        result = {}
        for field_name, field_type in fields:
            try:
                value = self.reader.sl_save_load_conv(field_type)
                result[field_name] = value
                print(f"  {field_name} = {value}")
            except Exception as e:
                print(f"Error reading field {field_name}: {e}")
                break

        return result

    def parse_settings_chunk(self) -> Dict[str, Any]:
        """Parse OPTS"""
        if not self.reader:
            return {}

        pos = self.reader.find_chunk(b"OPTS")
        if pos is None:
            return {}

        print(f"\nParsing OPTS chunk at 0x{pos:x}")

        # OPTS is marked as CH_READONLY, meaning it's a legacy chunk
        # For now, return empty dict and rely on economy data
        return {}

    def parse_save_file(self) -> Dict[str, Any]:
        """Parse save file"""
        self.load_and_decompress()

        # Parse chunks in the exact order OpenTTD does
        map_data = self.parse_maps_chunk()
        date_data = self.parse_date_chunk()
        economy_data = self.parse_economy_chunk()
        settings_data = self.parse_settings_chunk()
        companies = self.parse_companies_chunk()

        # Get current game date and max loan from parsed data
        current_date = date_data.get("date", 0)
        economy_date = date_data.get("economy_date", 0)
        current_year = convert_date_to_year(current_date) if current_date else 1950
        global_max_loan = settings_data.get(
            "difficulty.max_loan", economy_data.get("max_loan", 300000)
        )

        # Combine raw date with parsed date info
        calendar_date_info = convert_date_to_ymd(current_date) if current_date else None
        economy_date_info = convert_date_to_ymd(economy_date) if economy_date else None

        # Create merged date fields
        merged_calendar_date = (
            {"date": current_date, **calendar_date_info}
            if calendar_date_info
            else {"date": current_date}
        )

        merged_economy_date = (
            {"date": economy_date, **economy_date_info}
            if economy_date_info
            else {"date": economy_date}
        )

        # Merge raw and parsed inflation data
        inflation_prices = economy_data.get("inflation_prices", 65536)
        inflation_payment = economy_data.get("inflation_payment", 65536)
        inflation_prices_info = format_inflation_value(inflation_prices)
        inflation_payment_info = format_inflation_value(inflation_payment)

        # Create merged inflation fields
        merged_inflation_prices = {"raw_value": inflation_prices, **inflation_prices_info}
        merged_inflation_payment = {"raw_value": inflation_payment, **inflation_payment_info}

        # Format company data with readable names and values
        map_size_x = map_data.get("dim_x", 256)
        formatted_companies = format_company_data(
            companies, map_size_x, current_year, global_max_loan
        )

        # Clean date_data by removing duplicates
        clean_date_data = {}
        for key, value in date_data.items():
            if key not in [
                "date",
                "economy_date",
            ]:  # Skip raw dates as they're now in merged fields
                clean_date_data[key] = value

        # Clean economy_data by removing duplicates
        clean_economy_data = {}
        for key, value in economy_data.items():
            if key not in [
                "inflation_prices",
                "inflation_payment",
            ]:  # Skip raw values as they're now in merged fields
                clean_economy_data[key] = value

        result = {
            "meta": {
                "filename": self.filename,
                "save_version": self.save_version,
                "minor_version": self.minor_version,
                "openttd_version": "14.1",  # TODO: add proper version detection
            },
            "game": {
                "date": {
                    "calendar_date": merged_calendar_date,
                    "economy_date": merged_economy_date,
                    **clean_date_data,
                },
                "economy": {
                    "inflation_prices": merged_inflation_prices,
                    "inflation_payment": merged_inflation_payment,
                    **clean_economy_data,
                },
                "settings": {
                    "max_loan": global_max_loan,
                    "interest_rate": economy_data.get("interest_rate", 2),
                },
            },
            "map": map_data,
            "companies": formatted_companies,
            "statistics": {
                "companies_count": len(formatted_companies),
                "map_size": f"{map_data.get('dim_x', 0)}x{map_data.get('dim_y', 0)}",
            },
        }

        return result


def load_save_file(filepath: str, silent: bool = True) -> Dict[str, Any]:
    """Load and parse an OpenTTD save file"""
    loader = SaveLoader(filepath, silent=silent)
    return loader.parse_save_file()
