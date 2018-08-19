# gameboy-tiles-extractor

The main goal of this tool is to programatically extract tiles data contained in a GameBoy (Color) ROM.

## Installation

```bash
(venv) make install
```

## Usage

```bash
(venv) python main.py ${CONFIGURATION_FILE_PATH} ${ROM_FILE_PATH} ${OUTPUT_DIRECTORY_PATH}
```

For example:

```bash
(venv) python main.py ./etc/ZELDA.yml ./ZELDA.gbc ./var/
```
