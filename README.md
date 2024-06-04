# NTFS MFT Analyzer

This tool analyzes the Master File Table (MFT) structure used by the NTFS file system. It displays the name, type, size, and timestamp information of files within the MFT. Additionally, it lists the physical location and permissions of each file.

## Installation and Usage

To run this code, you'll need Python 3 and the [pytsk3](https://github.com/py4n6/pytsk) library installed.

Installation steps:

1. Install Python 3: [Python Download Page](https://www.python.org/downloads/)
2. Install the pytsk3 library: `pip install pytsk3`
3. Run the code: `python mft_parser.py`

After running the code, the program will prompt you to select a disk or disk image and then proceed to analyze the MFT structure.

## Contributions

Contributions and feedback are welcomed. Please refer to the [Contribution Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the [MIT License]. See the license file for details.
