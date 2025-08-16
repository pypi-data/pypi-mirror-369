# whl-com

## Installation

```bash
pip install whl-com
```

## Usage

### options

```text
Usage: whl_com.py [OPTIONS] [COMMANDS]...

  whl-com

Options:
  -D, --device TEXT       serial device  [required]
  -b, --baudrate INTEGER  baudrate
  -t, --timeout FLOAT     timeout in seconds
  -f, --input_file TEXT   commands file
  --dry_run               do not send commands, just print them
  --no_output_filter      do not filter output, print everything
  --filter TEXT           filter output by regex pattern
  --quiet                 do not print output, only send commands
  -i, --interactive       enter interactive mode after sending commands
  --help                  Show this message and exit.
```

### send single command

> send `log com1 gpgga ontime 1` to device

```bash
python3 whl_com.py --device /dev/ttyUSB0 --baudrate 460800 log com1 gpgga ontime 1
```

### send multiple commands

> create a file `commands.txt` with the following content:

```text
log com1 gpgga ontime 1
log com1 gpchcx ontime 0.01
saveconfig
```

> specify the file with `--input_file` option:

```bash
python3 whl_com.py --device /dev/ttyUSB0 --baudrate 460800 --input_file commands.txt
```
