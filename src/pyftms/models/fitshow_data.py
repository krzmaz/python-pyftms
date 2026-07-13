# Copyright 2024, Sergey Dudanov
# SPDX-License-Identifier: Apache-2.0

import dataclasses as dc
from typing import Optional

from .common import BaseModel, model_meta


@dc.dataclass(frozen=True)
class FITSHOWData(BaseModel):
    """
    Custom data model for FITSHOW FS-BT-T4 treadmill.
    
    UUID: 0000fff1-0000-1000-8000-00805f9b34fb
    Format: 17-byte flat structure with single-byte fields
    """
    
    mask: int = dc.field(
        metadata=model_meta(format="u2"),
    )
    """Mask field indicating data presence."""
    
    time_elapsed: int = dc.field(
        metadata=model_meta(format="u2"),
    )
    """Elapsed time in seconds (bytes 5-6, little-endian)."""
    
    distance_total: int = dc.field(
        metadata=model_meta(format="u2"),
    )
    """Total distance in meters (bytes 7-8, little-endian)."""
    
    step_count: int = dc.field(
        metadata=model_meta(format="u2"),
    )
    """Step count (bytes 11-12, little-endian)."""
    
    # Reserved bytes for potential expansion
    reserved_1: bytes = dc.field(
        metadata=model_meta(format="2s"),
    )
    """Reserved bytes (indices 2-3)."""
    
    reserved_2: bytes = dc.field(
        metadata=model_meta(format="s2"),
    )
    """Reserved bytes (indices 8-9)."""
    
    reserved_3: bytes = dc.field(
        metadata=model_meta(format="2s"),
    )
    """Reserved bytes (indices 12-13)."""
    
    reserved_4: bytes = dc.field(
        metadata=model_meta(format="2s"),
    )
    """Reserved bytes (indices 14-15)."""
    
    termination_marker: int = dc.field(
        metadata=model_meta(format="u1"),
    )
    """Termination marker (byte 16)."""
    
    @property
    def speed_instant(self) -> float:
        """Calculate speed from distance and time."""
        if self.time_elapsed > 0:
            return (self.distance_total * 3.6) / self.time_elapsed
        return 0.0
