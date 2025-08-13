import array
from datetime import datetime
from pytz import UTC  # type: ignore[import-untyped]
import struct
from typing import BinaryIO, Union, Tuple, Optional

import numpy as np

from kestrelgrid.raw_reader.types import (
    DataCorruptionError,
    RawHeader,
    Frame,
    RawData,
    HEADER_LENGTH_BYTES,
    SUB_HEADER_BYTES,
)


def read_raw(
    fname: str,
    scale_data: bool = True,
    start_time: Optional[Union[float, datetime]] = None,
    end_time: Optional[Union[float, datetime]] = None,
) -> Tuple[Union[RawData, None], bool]:
    """Read a XMU raw data file

    Args:
        fname (str): Path to the raw data file
        scale_data (bool): If true, multiply data by scale factor defined in header
        start_time (float or datetime, optional): Optional start time for data range
        end_time (float or datetime, optional): Optional end time for data range

    Returns:
        Tuple[Union[RawData, None], bool]: A ist of frames if frames are found
        and a boolean indicating if the file is corrupted.
    """

    start_time, end_time = check_and_convert_start_and_end_time(
        start_time, end_time, set_defaults=False
    )

    corrupted = False
    frames = []
    try:
        with open(fname, "rb") as f:
            while True:
                frame = read_frame(
                    f, scale_data=scale_data, start_time=start_time, end_time=end_time
                )
                if frame:
                    frames.append(frame)

    except EOFError:
        pass

    except DataCorruptionError as e:
        print(e)  # TODO change to logging
        corrupted = True

    if len(frames) > 0:
        return frames, corrupted
    else:
        return None, corrupted


def raw_to_tv(
    raw_path: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Reads a raw file and returns the time and voltage data as numpy arrays.

    Args:
        raw_path (str): Path to the raw data file
        start_time (float, optional): Optional start time in epoch time
        end_time (float, optional): Optional end time in epoch time

    Returns:
        Tuple[np.ndarray, np.ndarray]: A tuple containing two numpy arrays:
            - all_t: Timestamps in epoch time
            - all_v: Voltage values in volts
    """
    start_time, end_time = check_and_convert_start_and_end_time(
        start_time, end_time, set_defaults=True
    )

    if start_time is None:
        start_time = 0.0
    if end_time is None:
        end_time = 1e100

    n_samples = get_raw_n_samples(raw_path, start_time, end_time)
    all_v = np.zeros(n_samples, dtype="float32")
    all_t = np.zeros(n_samples, dtype="float64")

    tell = 0
    try:
        with open(raw_path, "rb") as f:
            while True:
                frame = read_frame(
                    f, scale_data=True, start_time=start_time, end_time=end_time
                )
                if frame:
                    t, v, start_time, n = get_t_v_from_frame(frame)
                    all_v[tell : tell + n] = v
                    all_t[tell : tell + n] = t
                    tell += n

    except EOFError:
        pass
    except DataCorruptionError as e:
        print(e)  # TODO change to logging

    return all_t, all_v


def raw_to_csv(
    raw_path: str,
    csv_path: str,
    start_time: Optional[Union[float, datetime]] = None,
    end_time: Optional[Union[float, datetime]] = None,
    include_string_time=False,
):
    """Reads a raw file and writes the time and voltage data to a CSV file.

    Args:
        raw_path (str): Path to the raw data file
        csv_path (str): Path to save the CSV file to
        start_time (float, optional): Optional start time in epoch time
        end_time (float, optional): Optional end time in epoch time
        include_string_time (bool): If True, includes string representation of time in the CSV file
    """
    # Convert start and end time to epoch time if they are datetime objects
    start_time, end_time = check_and_convert_start_and_end_time(
        start_time, end_time, set_defaults=True
    )

    try:
        with open(csv_path, "w") as f_out:
            if include_string_time:
                f_out.write("timestamp_utc,timestamp_epoch,voltage_v\n")
            else:
                f_out.write("timestamp_epoch,voltage_v\n")
            with open(raw_path, "rb") as f:
                while True:
                    frame = read_frame(
                        f, scale_data=True, start_time=start_time, end_time=end_time
                    )

                    if frame:
                        t, v, start_time, n = get_t_v_from_frame(frame)

                        if include_string_time:
                            for t_item, v_item in zip(t, v):
                                timestamp = datetime.fromtimestamp(
                                    t_item, UTC
                                ).strftime("%Y-%m-%d %H:%M:%S.%f")
                                f_out.write(f"{timestamp},{t_item},{v_item}\n")
                        else:
                            tv = np.zeros((n, 2))
                            tv[:, 0] = t
                            tv[:, 1] = v
                            np.savetxt(f_out, tv, fmt="%f,%f")

    except EOFError:
        pass
    except DataCorruptionError as e:
        print(e)  # TODO change to logging


def check_and_convert_start_and_end_time(
    start_time: Optional[Union[float, datetime]] = None,
    end_time: Optional[Union[float, datetime]] = None,
    set_defaults: bool = False,
) -> Tuple[Optional[float], Optional[float]]:
    """Converts start and end time to epoch time if they are datetime objects.

    If start and end times are already floats, they are returned as is. If set_default
    flag is true, then start_time is set to 0 and end_time is set to 1e100.

    Args:
        start_time (float or datetime, optional): Start time in epoch time or datetime object
        end_time (float or datetime, optional): End time in epoch time or datetime object
        set_defaults (bool): If True, sets default values for start_time and end_time if they are None.

    Returns:
        Tuple[float, float]: A tuple containing the start and end times in epoch time.
    """
    if isinstance(start_time, datetime):
        start_time = start_time.timestamp()
    if isinstance(end_time, datetime):
        end_time = end_time.timestamp()

    if set_defaults:
        if start_time is None:
            start_time = 0.0
        if end_time is None:
            end_time = 1e100

    return start_time, end_time


def get_t_v_from_frame(frame: Frame) -> Tuple[np.ndarray, np.ndarray, float, int]:
    """Extracts time and voltage data from a frame.

    Args:
        frame (Frame): A dictionary containing the frame data

    Returns:
        Tuple[np.ndarray, np.ndarray, float, float]: A tuple containing:
            - t: Timestamps in epoch time
            - v: Voltage values in volts
            - start_time: Start time of the frame in epoch time
            - n: Number of samples in the frame
    """
    start_time = frame["start_time"]

    # sample rate is stored a ksps. Convert to sps
    sample_rate = frame["sample_rate"] * 1000
    v = frame["data"]
    n = len(v)

    t = start_time + np.arange(n) / sample_rate

    return t, v, start_time, n


def read_frame(
    f: BinaryIO,
    scale_data=True,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
) -> Optional[Frame]:
    """Read a single frame from a raw data stream.

    Returns none if frame is outside time range specified.

    Args:
        f (BinaryIO): File stream to read the data from
        scale_data (bool): If true, multiply data by scale factor defined in header
        start_time (float, optional): Start time in epoch time
        end_time (float, optional): End time in epoch time

    Returns:
        Frame: A dictionary containing the frame data, or None if frame is outside time range specified.
    """
    header = RawHeader(f)

    if start_time is not None and end_time is not None:
        if header.timestamp < start_time or header.timestamp >= end_time:
            f.seek(header.n_bytes - HEADER_LENGTH_BYTES, 1)
            return None

    if scale_data:
        data = (
            np.array(
                array.array("h", f.read(header.n_bytes - HEADER_LENGTH_BYTES)),
                dtype="float32",
            )
            * header.scale_factor
        )
    else:
        data = np.array(array.array("h", f.read(header.n_bytes - HEADER_LENGTH_BYTES)))

    return Frame(
        {
            "data": data,
            "pmu_id": header.pmu_id,
            "sample_rate": header.sample_rate,
            "start_time": header.timestamp,
            "scale_factor": header.scale_factor,
            "boot_count": header.boot_count,
            "gps_locked": header.gps_locked,
        }
    )


def get_last_frame(fname: str) -> Optional[Frame]:
    """Efficient helper for getting last valid frame of a raw_file

    Args:
        fname (str): Path to the raw data file

    Returns:
        Frame: The last valid frame in the file.

    """
    n_bytes = None
    with open(fname, "rb") as f:
        while True:
            header_bytes = f.read(2)

            if len(header_bytes) < 2:
                if not n_bytes:
                    raise DataCorruptionError(f"{fname} has no valid frames.")
                f.seek(-n_bytes, 1)
                return read_frame(f)

            header_data = struct.unpack("<h", header_bytes)
            n_bytes = header_data[0]
            f.seek(n_bytes - 2, 1)


def seek_frame(f: BinaryIO, t: float):
    """Seeks the file pointer to the start of the frame whose timestamp is equal or greater to the input timestamp.
    Throws an exception if the end of the file is reached without finding a matching timestamp.
    """
    while True:
        header = RawHeader(f)
        if header.timestamp >= t:
            f.seek(-HEADER_LENGTH_BYTES, 1)
            return
        f.seek(header.n_bytes - HEADER_LENGTH_BYTES, 1)


def truncate_raw(raw_file_path: str, output_file_path: str, t: float = 9999999999.0):
    """Creates a truncated file at the specified timestamp, t, or the first corrupt frame, whichever is sooner.

    Args:
        raw_file_path (str): input raw file path
        output_file_path (str): path to save the truncated raw file to
        t (float, optional): epoch timestamp. Defaults to 9999999999.0.
    """
    with open(raw_file_path, "rb") as f:
        try:
            seek_frame(f, t)
        except DataCorruptionError:
            pass
        good_bytes = f.tell()
        f.seek(0)
        data = f.read(good_bytes)
    with open(output_file_path, "wb") as f:
        f.write(data)


def get_raw_n_samples(
    raw_path: str, start_time: Optional[float] = None, end_time: Optional[float] = None
) -> int:
    """Fast method for identifying number of samples in a raw file.

    Args:
        raw_path (str): Path to the raw data file
        start_time (float, optional): Start time in epoch time
        end_time (float, optional): End time in epoch time
    Returns:
        int: Total number of samples in the raw file within the specified time range.

    """

    start_time, end_time = check_and_convert_start_and_end_time(
        start_time, end_time, set_defaults=True
    )

    total_n_samples = 0
    try:
        with open(raw_path, "rb") as f:
            while True:

                # read first 16 bytes
                header_bytes = f.read(SUB_HEADER_BYTES)
                if len(header_bytes) < SUB_HEADER_BYTES:
                    break
                n_bytes, _, n_samples, _, timestamp = struct.unpack(
                    "<hhhhd", header_bytes
                )
                if timestamp > end_time:
                    break
                f.seek(n_bytes - SUB_HEADER_BYTES, 1)
                if timestamp < start_time:
                    continue
                total_n_samples += n_samples

    except EOFError:
        pass
    return total_n_samples
