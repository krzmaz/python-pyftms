# Copyright 2024, Sergey Dudanov
# SPDX-License-Identifier: Apache-2.0

import io
from typing import cast

from .serializer import Serializer


FITSHOW_CUSTOM_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"


class FITSHOWSerializer(Serializer):
    """Serializer for FITSHOW custom characteristic data format."""
    
    def __init__(self) -> None:
        self._custom_uuid = FITSHOW_CUSTOM_UUID
    
    @property
    def uuid(self) -> str:
        return self._custom_uuid
    
    def _deserialize(self, src: io.IOBase) -> dict:
        # Read the full 17-byte structure
        data = src.read(17)
        if len(data) < 17:
            raise ValueError(f"Invalid FITSHOW data length: {len(data)}")
        
        result = {}
        
        # Parse mask (bytes 0-1, little-endian)
        mask = int.from_bytes(data[0:2], byteorder="little")
        result["mask"] = mask
        
        # Fixed byte positions based on empirical analysis
        # Time elapsed: bytes 5-6 (u2, little-endian)
        time_val = int.from_bytes(data[5:7], byteorder="little")
        if time_val > 0:
            result["time_elapsed"] = time_val
        
        # Distance: bytes 7-8 (u2, little-endian)
        dist_val = int.from_bytes(data[7:9], byteorder="little")
        if dist_val > 0:
            result["distance_total"] = dist_val
        
        # Step count: bytes 11-12 (u2, little-endian)
        step_val = int.from_bytes(data[11:13], byteorder="little")
        if step_val > 0:
            result["step_count"] = step_val
        
        # Reserved fields
        result["reserved_1"] = data[2:4]
        result["reserved_2"] = data[8:10]
        result["reserved_3"] = data[12:14]
        result["reserved_4"] = data[14:16]
        result["termination_marker"] = data[16]
        
        return result
    
    def deserialize(self, data: bytearray) -> dict:
        """Deserialize FITSHOW data."""
        bio = io.BytesIO(data)
        return self._deserialize(bio)
    
    def serialize(self, writer: io.IOBase, value: dict) -> int:
        # Not implemented - FITSHOW is read-only
        raise NotImplementedError("FITSHOW characteristic is read-only")
    
    def get_size(self) -> int:
        return 17
