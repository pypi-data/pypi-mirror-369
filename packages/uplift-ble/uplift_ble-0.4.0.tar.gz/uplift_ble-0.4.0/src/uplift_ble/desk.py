#!/usr/bin/env python3
"""
Module: uplift_ble.desk
Handles connecting to an Uplift BLE desk, sending commands, and logging notifications.
"""
import asyncio
from contextlib import suppress
from enum import Enum
import functools
import logging
from typing import Any, Callable, Dict, Optional
from bleak import BleakClient

from uplift_ble.ble_characteristics import (
    BLE_CHAR_UUID_DIS_FIRMWARE_REV,
    BLE_CHAR_UUID_DIS_HARDWARE_REV,
    BLE_CHAR_UUID_DIS_MANUFACTURER_NAME,
    BLE_CHAR_UUID_DIS_MODEL_NUMBER,
    BLE_CHAR_UUID_DIS_PNP_ID,
    BLE_CHAR_UUID_DIS_SERIAL_NUMBER,
    BLE_CHAR_UUID_DIS_SOFTWARE_REV,
    BLE_CHAR_UUID_DIS_SYSTEM_ID,
    BLE_CHAR_UUID_GAP_APPEARANCE,
    BLE_CHAR_UUID_GAP_DEVICE_NAME,
    BLE_CHAR_UUID_GAP_PERIPHERAL_PREFERRED_CONNECTION_PARAMETERS,
    BLE_CHAR_UUID_GAP_PERIPHERAL_PRIVACY_FLAG,
    BLE_CHAR_UUID_UPLIFT_DESK_CONTROL,
    BLE_CHAR_UUID_UPLIFT_DESK_OUTPUT,
)
from uplift_ble.ble_services import (
    BLE_SERVICE_UUID_DEVICE_INFORMATION_SERVICE,
    BLE_SERVICE_UUID_GENERIC_ACCESS_SERVICE,
)
from uplift_ble.packet import (
    PacketNotification,
    create_command_packet,
    parse_notification_packets,
)
from uplift_ble.units import (
    convert_hundredths_mm_to_whole_mm,
    convert_mm_to_in,
)

logger = logging.getLogger(__name__)


class DeskEvent(Enum):
    """Enumeration of desk notification events."""

    HEIGHT = "height"
    RST = "rst"
    CALIBRATION_HEIGHT = "calibration_height"
    HEIGHT_LIMIT_MAX = "height_limit_max"


def command_writer(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Ensure BLE client is connected.
        if not self._connected:
            await self.connect()

        # If we need to send a wake command first, do so here, avoiding recursive case.
        is_wake_func = func.__name__ == "wake"
        if self.requires_wake and not is_wake_func:
            # Send a flurry of wake commands in rapid succession.
            for i in range(3):
                await self.wake()
                await asyncio.sleep(0.1)

        # Build and send packet.
        packet: bytes = func(self, *args, **kwargs)
        logger.debug(f"{func.__name__}(): sending {len(packet)} bytes: {packet.hex()}")
        await self._client.write_gatt_char(self.char_uuid_control, packet)

        # Allow time for any notifications to arrive.
        if not is_wake_func:
            logger.debug(
                f"Waiting up to {self._notification_timeout}s for notifications..."
            )
            await asyncio.sleep(self._notification_timeout)
        return packet

    return wrapper


class Desk:
    """
    BLE controller for standing desk.
    """

    def __init__(
        self,
        address: str,
        requires_wake: bool = False,
        char_uuid_control: str = BLE_CHAR_UUID_UPLIFT_DESK_CONTROL,
        char_uuid_output: str = BLE_CHAR_UUID_UPLIFT_DESK_OUTPUT,
        notification_timeout: float = 5.0,
        bleak_options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Desk adapter

        Args:
            address: The Bluetooth address of the desk adapter
            requires_wake: **DEPRECATED**
                Whether the desk requires wake commands before other commands.
                Deprecated as it should be the caller's responsibility to send wake packets with wake().
                Implementers are encouraged to set this as `False` for now.
            char_uuid_control: UUID of the control characteristic
            char_uuid_output: UUID of the output/notification characteristic
            notification_timeout: Time to wait for notifications after sending commands
            bleak_options: Optional dictionary of additional options to pass to BleakClient
        """
        self.address = address
        self.requires_wake = requires_wake
        self.char_uuid_control = char_uuid_control
        self.char_uuid_output = char_uuid_output
        self._notification_timeout = notification_timeout

        self._client = BleakClient(
            address_or_ble_device=address, **(bleak_options or {})
        )
        self._connected = False
        self._last_known_height_mm: int | None = None
        self._listeners = {}

    def on(self, event: DeskEvent, handler: Callable) -> None:
        """Register an event handler."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)

    def off(self, event: DeskEvent, handler: Callable) -> None:
        """Remove an event handler."""
        if event in self._listeners:
            try:
                self._listeners[event].remove(handler)
            except ValueError:
                pass

    def remove_all_listeners(self, event: Optional[DeskEvent] = None) -> None:
        """Remove all listeners for a specific event or all events."""
        if event:
            self._listeners.pop(event, None)
        else:
            self._listeners.clear()

    def _emit(self, event: DeskEvent, *args) -> None:
        """Emit an event to all registered handlers."""
        for handler in self._listeners.get(event, []):
            try:
                handler(*args)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {e}")

    async def connect(self):
        if not self._connected:
            logger.info(f"Connecting to {self.address}…")
            await self._client.connect()
            self._connected = True
            logger.info("Connected.")
            logger.info(f"Subscribing to notifications on {self.char_uuid_output}.")
            await self._client.start_notify(
                self.char_uuid_output, self._notification_handler
            )
            logger.info("Subscribed.")

    async def disconnect(self):
        if self._connected:
            logger.info("Disconnecting…")
            # BlueZ adapters have been known to throw an EOFError exception when the bus closes.
            with suppress(EOFError):
                await self._client.disconnect()
            self._connected = False
            logger.info("Disconnected.")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    def _notification_handler(self, sender: int, data: bytearray):
        """
        Handler for incoming notifications. Logs raw data, updates state, and parses packets.
        """
        logger.debug(f"Received notification from {sender}: {data.hex()}")
        packets = parse_notification_packets(data)
        logger.debug(f"Received {len(packets)} notification packet(s).")
        for p in packets:
            self._process_notification_packet(p)

    async def get_ble_gap_values(self) -> Dict[str, Optional[str]]:
        """
        Read standard BLE Generic Access Service chars and return them by name.
        """
        if not self._connected:
            await self.connect()

        char_uuids: Dict[str, str] = {
            "device_name": BLE_CHAR_UUID_GAP_DEVICE_NAME,
            "appearance": BLE_CHAR_UUID_GAP_APPEARANCE,
            "peripheral_privacy_flag": BLE_CHAR_UUID_GAP_PERIPHERAL_PRIVACY_FLAG,
            "peripheral_preferred_connection_parameters": BLE_CHAR_UUID_GAP_PERIPHERAL_PREFERRED_CONNECTION_PARAMETERS,
        }

        info: Dict[str, Optional[str]] = {}

        try:
            self._client.services.get_service(BLE_SERVICE_UUID_GENERIC_ACCESS_SERVICE)
        except Exception:
            return info

        for name, uuid in char_uuids.items():
            try:
                raw = await self._client.read_gatt_char(uuid)
                if not raw:
                    info[name] = None
                elif name == "appearance":
                    # Appearance is a 16-bit value
                    info[name] = str(int.from_bytes(raw, byteorder="little"))
                elif name == "peripheral_privacy_flag":
                    # Peripheral privacy flag is a single byte (0 or 1)
                    info[name] = str(raw[0])
                elif name == "peripheral_preferred_connection_parameters":
                    # Binary data, return as hex
                    info[name] = raw.hex()
                else:
                    # Device name is UTF-8 string
                    info[name] = raw.decode("utf-8", errors="ignore").rstrip("\x00")
            except Exception:
                info[name] = None

        return info

    async def get_ble_dis_values(self) -> Dict[str, Optional[str]]:
        """
        Read standard BLE Device Information Service chars and return them by name.
        """
        if not self._connected:
            await self.connect()

        char_uuids: Dict[str, str] = {
            "manufacturer_name": BLE_CHAR_UUID_DIS_MANUFACTURER_NAME,
            "model_number": BLE_CHAR_UUID_DIS_MODEL_NUMBER,
            "serial_number": BLE_CHAR_UUID_DIS_SERIAL_NUMBER,
            "hardware_revision": BLE_CHAR_UUID_DIS_HARDWARE_REV,
            "firmware_revision": BLE_CHAR_UUID_DIS_FIRMWARE_REV,
            "software_revision": BLE_CHAR_UUID_DIS_SOFTWARE_REV,
            "system_id": BLE_CHAR_UUID_DIS_SYSTEM_ID,
            "pnp_id": BLE_CHAR_UUID_DIS_PNP_ID,
        }

        info: Dict[str, Optional[str]] = {}

        try:
            self._client.services.get_service(
                BLE_SERVICE_UUID_DEVICE_INFORMATION_SERVICE
            )
        except Exception:
            return info

        for name, uuid in char_uuids.items():
            try:
                raw = await self._client.read_gatt_char(uuid)
                if not raw:
                    info[name] = None
                elif name in ("system_id", "pnp_id"):
                    info[name] = raw.hex()
                else:
                    info[name] = raw.decode("utf-8", errors="ignore").rstrip("\x00")
            except Exception:
                info[name] = None

        return info

    @command_writer
    def wake(self) -> bytes:
        return create_command_packet(opcode=0x00, payload=b"")

    @command_writer
    def move_up(self) -> bytes:
        return create_command_packet(opcode=0x01, payload=b"")

    @command_writer
    def move_down(self) -> bytes:
        return create_command_packet(opcode=0x02, payload=b"")

    @command_writer
    def move_to_height_preset_1(self) -> bytes:
        return create_command_packet(opcode=0x05, payload=b"")

    @command_writer
    def move_to_height_preset_2(self) -> bytes:
        return create_command_packet(opcode=0x06, payload=b"")

    @command_writer
    def request_height_limits(self) -> bytes:
        return create_command_packet(opcode=0x07, payload=b"")

    @command_writer
    def set_calibration_offset(self, calibration_offset: int) -> bytes:
        if not 0 <= calibration_offset <= 0xFFFF:
            raise ValueError("calibration_offset not in range [0,65535]")
        payload = calibration_offset.to_bytes(2, "big")
        return create_command_packet(opcode=0x10, payload=payload)

    @command_writer
    def set_height_limit_max(self, max_height: int) -> bytes:
        if not 0 <= max_height <= 0xFFFF:
            raise ValueError("max_height not in range [0,65535]")
        payload = max_height.to_bytes(2, "big")
        return create_command_packet(opcode=0x11, payload=payload)

    @command_writer
    def move_to_specified_height(self, height: int) -> bytes:
        if not isinstance(height, int) or not 0 <= height <= 0xFFFF:
            raise ValueError("height must be an integer in range [0,65535]")
        payload = height.to_bytes(2, "big")
        return create_command_packet(opcode=0x1B, payload=payload)

    @command_writer
    def set_current_height_as_height_limit_max(self) -> bytes:
        return create_command_packet(opcode=0x21, payload=b"")

    @command_writer
    def set_current_height_as_height_limit_min(self) -> bytes:
        return create_command_packet(opcode=0x22, payload=b"")

    @command_writer
    def clear_height_limit_max(self) -> bytes:
        return create_command_packet(opcode=0x23, payload=bytes([0x01]))

    @command_writer
    def clear_height_limit_min(self) -> bytes:
        return create_command_packet(opcode=0x23, payload=bytes([0x02]))

    @command_writer
    def stop_movement(self) -> bytes:
        return create_command_packet(opcode=0x2B, payload=b"")

    @command_writer
    def set_units_to_centimeters(self) -> bytes:
        return create_command_packet(opcode=0x0E, payload=bytes([0x00]))

    @command_writer
    def set_units_to_inches(self) -> bytes:
        return create_command_packet(opcode=0x0E, payload=bytes([0x01]))

    @command_writer
    def reset(self) -> bytes:
        return create_command_packet(opcode=0xFE, payload=b"")

    async def get_current_height(self) -> int | None:
        """
        Requests a height update and returns the last observed desk height in mm.
        """
        await self.request_height_limits()
        return self._last_known_height_mm

    def _process_notification_packet(self, p: PacketNotification):
        if p.opcode == 0x01:
            hundredths_of_mm = int.from_bytes(p.payload, byteorder="big", signed=False)
            mm = convert_hundredths_mm_to_whole_mm(hundredths_of_mm)
            inches = convert_mm_to_in(mm)
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, current height: {mm} mm (~{inches} in)"
            )
            # Important! Update the class state with this most-recently reported height.
            self._last_known_height_mm = mm
            # Emit event.
            self._emit(DeskEvent.HEIGHT, mm)

        elif p.opcode == 0x04:
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, desk is reporting an error state (RST) and likely needs to be manually reset"
            )
            # Emit event.
            self._emit(DeskEvent.RST)

        elif p.opcode == 0x10:
            mm = int.from_bytes(p.payload, byteorder="big", signed=False)
            inches = convert_mm_to_in(mm)
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, calibration height: {mm} mm (~{inches} in)"
            )
            # Emit event.
            self._emit(DeskEvent.CALIBRATION_HEIGHT, mm)

        elif p.opcode == 0x11:
            mm = int.from_bytes(p.payload, byteorder="big", signed=False)
            inches = convert_mm_to_in(mm)
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, height limit max: {mm} mm (~{inches} in)"
            )
            # Emit event.
            self._emit(DeskEvent.HEIGHT_LIMIT_MAX, mm)

        elif p.opcode == 0x12:
            # Avoid running the command with the 0x12 opcode!
            # The 0x12 command takes a 2-byte payload, but setting it to various values causes strange and potentially dangerous behavior.
            # For example, some payloads make the desk movement jerky, other payloads make the desk move quickly.
            # If you do change this value, anecdotally, a payload of [0x01, 0x00] restores normal behavior.
            # It also appears to affect the scaling used for the height display.
            # Until its behavior is better understood, we recommend avoiding it!
            raw = p.payload.hex()
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, internal configuration value. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        elif p.opcode == 0x25:
            raw = p.payload.hex()
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, height preset 1. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        elif p.opcode == 0x26:
            raw = p.payload.hex()
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, height preset 2. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        elif p.opcode == 0x27:
            raw = p.payload.hex()
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, height preset 3. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        elif p.opcode == 0x28:
            raw = p.payload.hex()
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, height preset 4. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        else:
            logger.debug(
                f"- Received packet, opcode=0x{p.opcode:02X}, unknown opcode. Please make a PR if you know what this is."
            )
