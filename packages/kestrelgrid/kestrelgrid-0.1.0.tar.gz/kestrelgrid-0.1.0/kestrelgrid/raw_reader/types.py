import struct
from typing import BinaryIO, TypedDict

import numpy as np

HEADER_LENGTH_BYTES = 88
SUB_HEADER_BYTES = 16
MAGIC_NUM = struct.unpack(">h", bytes.fromhex("BEEF"))[0]


class DataCorruptionError(Exception):
    pass


class RawHeader:
    """Parsed Sensor Header Data

    Attributes:
        n_bytes (int): Number of bytes in the packet
        pmu_id (int): Unique identifier for the PMU
        n_samples (int): Number of samples in the packet
        sample_rate (int): Sample rate in kHz
        timestamp (float): Timestamp of the packet in seconds since epoch
        scale_factor (float): Scale factor for the data
        fw_vers (int): Firmware version
        magic_num (int): Magic number for packet validation
        time_updated (int): Time updated in seconds since epoch (UTC)
        boot_count (int): Boot count of the PMU
        gps_locked (bool): Whether the GPS is locked
    """

    def __init__(self, f: BinaryIO):
        """Parses data from the binary stream

        Args:
            f (BinaryIO): File stream to read the data from

        Raises:
            EOFError: If not enough bytes are read from the file stream
            DataCorruptionError: If the magic number does not match the expected value

        """
        header_bytes = f.read(HEADER_LENGTH_BYTES)

        if len(header_bytes) < HEADER_LENGTH_BYTES:
            raise EOFError(
                f"Not enough bytes to be read. Read {len(header_bytes)}, expected {HEADER_LENGTH_BYTES}"
            )

        header_data = struct.unpack("<hhhhddhhhhh54x", header_bytes)

        self.n_bytes = header_data[0]
        self.pmu_id = header_data[1]
        self.n_samples = header_data[2]
        self.sample_rate = header_data[3]
        self.timestamp = header_data[4]
        self.scale_factor = header_data[5]
        self.fw_vers = header_data[6]
        self.magic_num = header_data[7]
        self.time_updated = header_data[8]
        self.boot_count = header_data[9]
        self.gps_locked = bool(header_data[10])

        if self.magic_num != MAGIC_NUM:
            f.seek(-HEADER_LENGTH_BYTES, 1)
            raise DataCorruptionError(f"Packet at byte {f.tell()} is corrupted.")


class Frame(TypedDict):
    """A single frame of data"""

    data: np.ndarray
    pmu_id: int
    sample_rate: int
    start_time: float
    scale_factor: float
    boot_count: int
    gps_locked: bool


RawData = list[Frame]
