import sys
import time
import logging
import hid
from enum import IntEnum
from functools import wraps


def requires_device(func):
    """Decorator to ensure an HID device is attached before calling the method."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.device:
            logging.warning("No device attached.")
            return False
        return func(self, *args, **kwargs)
    return wrapper


class Command(IntEnum):
    """HID command codes for the EVT02 device."""
    CLEAR_OUTPUT_PORT = 0x00
    SET_OUTPUT_PORT = 0x01
    SET_OUTPUT_LINES = 0x02
    SET_OUTPUT_LINE = 0x03
    PULSE_OUTPUT_LINES = 0x04
    PULSE_OUTPUT_LINE = 0x05
    SEND_LAST_OUTPUT_BYTE = 0x0A
    CONVEY_EVENT_TO_OUTPUT = 0x14
    CONVEY_EVENT_TO_OUTPUT_EX = 0x15
    CANCEL_CONVEY_EVENT_TO_OUTPUT = 0x16
    CANCEL_EVENT_REROUTES = 0x1E
    REROUTE_EVENT_INPUT = 0x1F
    SETUP_ROTARY_CONTROLLER = 0x28
    SET_ROTARY_CONTROLLER_POSITION = 0x29
    CONFIGURE_DEBOUNCE = 0x32
    SET_WS2811_RGB_LED_COLOR = 0x3C
    SEND_LED_COLORS = 0x3D
    SWITCH_ALL_LINES_EVENT_DETECTION = 0x64
    SWITCH_LINE_EVENT_DETECTION = 0x65
    SET_ANALOG_INPUT_DETECTION = 0x66
    REROUTE_ANALOG_INPUT = 0x67
    SET_ANALOG_EVENT_STEP_SIZE = 0x68
    SWITCH_DIAGNOSTIC_MODE = 0xC8
    SWITCH_EVENT_TEST = 0xC9
    RESET = 0xFF


class EventExchanger:
    """Class for communicating with EVT02 devices over HID."""

    RX_BUF_SIZE = 1
    AXIS_MULTIPLIER = 256

    def __init__(self, log_level=logging.CRITICAL):
        """
        Initialize the EventExchanger.

        Args:
            log_level (int): Logging level (default: CRITICAL).
        """
        self.device = None
        self._axis_value = 0
        logging.basicConfig(stream=sys.stderr, level=log_level)

    # -------------------------------------------------------------------------
    # DEVICE MANAGEMENT
    # -------------------------------------------------------------------------

    def scan(self, matching_key="EventExchanger"):
        """Scan for plugged-in EVT devices.

        Args:
            matching_key (str): Substring to match in product name.

        Returns:
            list[dict]: Matching HID device info.
        """
        devices = hid.enumerate()
        found = [
            d for d in devices
            if matching_key.lower() in (d.get("product_string") or "").lower()
        ]
        for d in found:
            logging.info(
                "Device found: %s (s/n: %s)",
                d.get("product_string"), d.get("serial_number")
            )
        return found

    def attach_name(self, matching_key="EventExchanger"):
        """Attach EVT device by matching part of its product name."""
        for d in hid.enumerate():
            if matching_key.lower() in (d.get("product_string") or "").lower():
                try:
                    self.device = hid.device()
                    self.device.open_path(d["path"])
                    self.device.set_nonblocking(True)
                    logging.info("Attached device: %s (s/n: %s)",
                                 d.get("product_string"), d.get("serial_number"))
                    return True
                except IOError as e:
                    logging.error("Failed to attach device: %s", e)
                    return False
        logging.warning("No device matches the product name '%s'", matching_key)
        return False

    def attach_id(self, path):
        """Attach EVT device by matching its unique path."""
        for d in hid.enumerate():
            if path in d["path"]:
                try:
                    self.device = hid.device()
                    self.device.open_path(d["path"])
                    self.device.set_nonblocking(True)
                    logging.info("Attached device: %s (s/n: %s)",
                                 d.get("product_string"), d.get("serial_number"))
                    return True
                except IOError as e:
                    logging.error("Failed to attach device: %s", e)
                    return False
        logging.warning("No device found with matching path.")
        return False

    @requires_device
    def close(self):
        """Close the currently attached EVT device."""
        self.device.close()
        logging.info("Device successfully detached.")
        return True

    @requires_device
    def reset(self):
        """Reset EVT device and disconnect from USB."""
        self.device.write([0, Command.RESET, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.device.close()
        logging.info("Device successfully reset and detached.")
        return True

    # -------------------------------------------------------------------------
    # DATA I/O METHODS
    # -------------------------------------------------------------------------

    @requires_device
    def wait_for_event(self, allowed_event_lines, timeout_ms):
        """Wait for incoming digital events based on polling.

        Args:
            allowed_event_lines (int): Bit mask [0–255] for digital inputs.
            timeout_ms (int | None): Timeout in ms (None = infinite).

        Returns:
            tuple[int, int]: (event_code, elapsed_ms) or (-1, elapsed_ms) on timeout.
        """
        bit_mask = int(allowed_event_lines) if allowed_event_lines is not None else 0
        t_start = time.time()

        # Flush buffer
        while self.device.read(self.RX_BUF_SIZE):
            pass

        # Poll for event
        while True:
            last_event = self.device.read(self.RX_BUF_SIZE)
            t_elapsed = int((time.time() - t_start) * 1000)

            if last_event and (last_event[0] & bit_mask) > 0:
                return last_event[0], t_elapsed

            if timeout_ms is not None and t_elapsed >= timeout_ms:
                return -1, t_elapsed

    @requires_device
    def get_axis(self):
        """Get axis data from device."""
        while self.device.read(1):
            pass
        time.sleep(0.01)
        value_list = self.device.read(3)
        if value_list:
            self._axis_value = value_list[1] + (self.AXIS_MULTIPLIER * value_list[2])
        return self._axis_value

    # -------------------------------------------------------------------------
    # DEVICE COMMANDS
    # -------------------------------------------------------------------------

    @requires_device
    def write_lines(self, value):
        """Set output lines with a bit pattern [0–255]."""
        try:
            self.device.write([0, Command.SET_OUTPUT_LINES, value] + [0] * 8)
            return True
        except IOError as e:
            logging.error("Error sending data: %s", e)
            return False

    @requires_device
    def pulse_lines(self, value, duration_ms):
        """Pulse output lines."""
        self.device.write([
            0, Command.PULSE_OUTPUT_LINES, value,
            duration_ms & 255, duration_ms >> 8
        ] + [0] * 6)
        return True

    @requires_device
    def clear_lines(self):
        """Clear all output lines (set low)."""
        try:
            self.device.write([0, Command.SET_OUTPUT_LINES, 0] + [0] * 8)
            return True
        except IOError as e:
            logging.error("Error sending data: %s", e)
            return False

    @requires_device
    def set_analog_event_step_size(self, samples_per_step):
        """Set analog event step size."""
        self.device.write([
            0, Command.SET_ANALOG_EVENT_STEP_SIZE, samples_per_step
        ] + [0] * 8)
        return True

    @requires_device
    def renc_init(self, encoder_range, min_value, position, input_change, pulse_divider):
        """Initialize rotary encoder."""
        self._axis_value = position
        self.device.write([
            0, Command.SETUP_ROTARY_CONTROLLER,
            encoder_range & 255, encoder_range >> 8,
            min_value & 255, min_value >> 8,
            position & 255, position >> 8,
            input_change, pulse_divider, 0
        ])
        return True

    @requires_device
    def renc_set_pos(self, position):
        """Set rotary encoder position."""
        self._axis_value = position
        self.device.write([
            0, Command.SET_ROTARY_CONTROLLER_POSITION,
            position & 255, position >> 8
        ] + [0] * 7)
        return True

    @requires_device
    def set_led_rgb(self, red, green, blue, led_number, mode):
        """Set RGB LED color."""
        self.device.write([
            0, Command.SET_WS2811_RGB_LED_COLOR,
            red, green, blue, led_number, mode
        ] + [0] * 5)
        return True

    @requires_device
    def send_led_rgb(self, num_leds, mode):
        """Send LED color data."""
        self.device.write([
            0, Command.SEND_LED_COLORS, num_leds, mode
        ] + [0] * 7)
        return True

