# Copyright 2024, Sergey Dudanov
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import ClassVar

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from ...models import FITSHOWData, RealtimeData, TreadmillData
from ...serializer import FITSHOWSerializer, get_serializer
from ..client import FitnessMachine
from ..const import TREADMILL_DATA_UUID
from ..custom.detector import FITSHOWDetector
from ..machines import Treadmill
from ..properties import MachineType

_LOGGER = logging.getLogger(__name__)


FITSHOW_CUSTOM_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"


class FITSHOWTreadmill(Treadmill):
    """
    FITSHOW-specific Treadmill class.
    
    Supports both standard FTMS and FITSHOW custom characteristics.
    Combines data from both sources for a unified interface.
    """
    
    _machine_type: ClassVar[MachineType] = MachineType.TREADMILL
    _data_model: ClassVar[type[RealtimeData]] = TreadmillData
    _data_uuid: ClassVar[str] = TREADMILL_DATA_UUID
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fitshow_data = {}
        self._fitshow_serializer = FITSHOWSerializer()
        self._use_custom_characteristics = False
    
    async def _connect(self) -> None:
        await super()._connect()
        
        # Check if this is a FITSHOW device and subscribe to custom characteristic
        device_info = getattr(self, "_device_info", {})
        if FITSHOWDetector.is_fitshow_device(device_info):
            self._use_custom_characteristics = True
            _LOGGER.info("FITSHOW device detected - enabling custom characteristic support")
            await self._subscribe_to_custom_characteristics()
    
    async def _subscribe_to_custom_characteristics(self) -> None:
        """Subscribe to FITSHOW custom characteristic."""
        if not self._use_custom_characteristics:
            return
        
        try:
            if svc := self._cli.services.get_service(FITSHOW_CUSTOM_UUID):
                if char := svc.get_characteristic(FITSHOW_CUSTOM_UUID):
                    await self._cli.start_notify(
                        char,
                        self._on_fitshow_notify,
                    )
                    _LOGGER.info("Subscribed to FITSHOW custom characteristic")
        except Exception as e:
            _LOGGER.error("Error subscribing to FITSHOW characteristic: %s", e)
    
    def _on_fitshow_notify(self, c: BleakGATTCharacteristic, data: bytearray) -> None:
        """Handle notifications from FITSHOW custom characteristic."""
        _LOGGER.debug("Received FITSHOW notify: %s", data.hex(" ").upper())
        
        try:
            fitshow_result = self._fitshow_serializer.deserialize(data)
            
            # Update internal state
            self._fitshow_data = fitshow_result
            
            # Create combined event with both standard and custom data
            combined_data = {
                **self._properties,
                "time_elapsed": fitshow_result.get("time_elapsed"),
                "distance_total": fitshow_result.get("distance_total"),
                "step_count": fitshow_result.get("step_count"),
            }
            
            # Fire update event
            from ..backends import UpdateEvent
            
            update = UpdateEvent(event_id="update", event_data=combined_data)
            self._on_event(update)
            
        except Exception as e:
            _LOGGER.error("Error parsing FITSHOW data: %s", e)
    
    @property
    def fitshow_step_count(self) -> int | None:
        """Get step count from FITSHOW custom characteristic."""
        return self._fitshow_data.get("step_count")
    
    @property
    def fitshow_distance_total(self) -> int | None:
        """Get distance from FITSHOW custom characteristic."""
        return self._fitshow_data.get("distance_total")
    
    @property
    def fitshow_time_elapsed(self) -> int | None:
        """Get elapsed time from FITSHOW custom characteristic."""
        return self._fitshow_data.get("time_elapsed")
