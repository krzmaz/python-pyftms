# Copyright 2024, Sergey Dudanov
# SPDX-License-Identifier: Apache-2.0

from typing import TypedDict


class DeviceInfo(TypedDict, total=False):
    """Device Information"""
    manufacturer: str
    model: str
    serial_number: str
    sw_version: str
    hw_version: str


class FITSHOWDetector:
    """Detector for FITSHOW devices."""
    
    FITSHOW_MANUFACTURER = "FITSHOW"
    FITSHOW_MODEL_PATTERNS = ["FS-BT-T4", "FS-BT-T4-"]
    
    @staticmethod
    def is_fitshow_device(device_info: DeviceInfo) -> bool:
        """Check if device is a FITSHOW device."""
        manufacturer = device_info.get("manufacturer", "").upper()
        model = device_info.get("model", "").upper()
        
        is_fitshow = FITSHOWDetector.FITSHOW_MANUFACTURER in manufacturer
        
        for pattern in FITSHOWDetector.FITSHOW_MODEL_PATTERNS:
            if pattern in model:
                return True
        
        return is_fitshow
    
    @classmethod
    def detect_from_manufacturer(cls, manufacturer_name: str) -> str:
        """Detect manufacturer from name string."""
        mfg_upper = manufacturer_name.upper()
        
        if cls.FITSHOW_MANUFACTURER in mfg_upper:
            return cls.FITSHOW_MANUFACTURER
        return "UNKNOWN"
