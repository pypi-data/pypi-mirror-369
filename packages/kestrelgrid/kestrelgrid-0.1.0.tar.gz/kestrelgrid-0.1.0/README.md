# kestrelgrid

kestrelgrid is a Python package that provides functions for interacting with data from the Kestrel Grid (aka KGRID, https://kestrelgrid.com/) power system sensor network.

KGRID voltage data is archived in its native, .raw format. This package allows users to interact with the .raw data and export it to other standardized formats.

## Installation

The package is available on PyPI and can be installed via pip:

`pip install kestrelgrid`

## Use (Interacting with KGRID RawData objects)

Raw KGRID data is stored continuously and is broken into frames, each of which are most commonly 16000 samples.

Each Frame contains the raw waveform data (int16) and additional metadata.
- data (np.ndarray): The raw waveform data
- pmu_id (int): Unique identifier for the PMU
- n_samples (int): Number of samples in the packet
- sample_rate (int): Sample rate in kHz
- timestamp (float): Timestamp of the packet in seconds since epoch (UTC)
- scale_factor (float): Scale factor for the data
- fw_vers (int): Firmware version
- time_updated (int): Time updated in seconds since epoch
- boot_count (int): Boot count of the PMU
- gps_locked (bool): Whether the GPS is locked

A .raw file can be read using the raw_reader.read_raw() function, which returns a list of RawData objects, each of which represents a frame.

```python
from kestrelgrid import raw_reader
data,c = raw_reader.read_raw(file_path)
```

## License

MIT

## Development

To develop locally, start by running

```
make init
```

to build the package environment. 

The following commands are available to aid in development

```
make format # uses black for formatting
make lint-check # uses ruff to check linting
make type-check # uses mypy for type checking
make test # uses pytest to run unit tests
make precommit # runs all of the above
```