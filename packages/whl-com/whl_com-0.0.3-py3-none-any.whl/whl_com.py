#!/usr/bin/env python3
"""com.py
"""
import re
import signal
import sys
import threading
import time

import click
import serial

VERSION = '0.0.3'

stop_event = threading.Event()


def recv(conn, *args, **kwargs):
    """Receive data from the serial connection
    """
    while not stop_event.is_set():
        try:
            data = conn.readline()
            if not data:
                continue
            # only print lines starting with $command
            # TODO(prettyprint): not only $command, but also other lines
            if kwargs.get('quiet', False):
                continue
            if kwargs.get('no_output_filter', False):
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
            elif 'filter' in kwargs and kwargs['filter']:
                pattern = re.compile(kwargs['filter'])
                if pattern.search(data):
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
            else:
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            break
        except KeyboardInterrupt:
            print("Keyboard interrupt received, stopping...")
            break


def safe_serial_write(conn, data, retries=10):
    """Attempt to write data to the serial connection with retries."""
    for _ in range(retries):
        try:
            conn.write(data)
            return True
        except serial.SerialException:
            # wait a while
            time.sleep(0.1)
    return False


@click.command()
@click.option('-D', '--device', required=True, type=str, help='serial device')
@click.option('-b', '--baudrate', type=int, default=460800, help='baudrate')
@click.option('-t',
              '--timeout',
              type=float,
              default=1.0,
              help='timeout in seconds')
@click.option('-f', '--input_file', type=str, help='commands file')
@click.option('--dry_run',
              is_flag=True,
              help='do not send commands, just print them')
@click.option('--no_output_filter',
              is_flag=True,
              help='do not filter output, print everything')
@click.option('--filter', help='filter output by regex pattern')
@click.option('--quiet',
              is_flag=True,
              help='do not print output, only send commands')
@click.option('-i',
              '--interactive',
              is_flag=True,
              help='enter interactive mode after sending commands')
@click.argument('commands', nargs=-1)
def main(**kwargs):
    """whl-com"""
    conn = serial.Serial(kwargs['device'],
                         baudrate=kwargs['baudrate'],
                         timeout=kwargs['timeout'])
    # start reciever
    reciever = threading.Thread(target=recv,
                                daemon=True,
                                args=(conn, ),
                                kwargs={
                                    'quiet': kwargs['quiet'],
                                    'no_output_filter':
                                    kwargs['no_output_filter'],
                                    'filter': kwargs['filter']
                                })
    reciever.start()

    if kwargs['input_file']:
        with open(kwargs['input_file'], 'r', encoding='utf-8') as fin:
            commands = fin.readlines()
            for command in commands:
                command = command.strip()
                # ignore comments and empty lines
                if command and command[0] != '#':
                    if not kwargs['dry_run']:
                        safe_serial_write(conn, (command + '\r\n').encode())
                    print(command)

    else:
        command = ' '.join(kwargs['commands']).strip()
        if command:
            if not kwargs['dry_run']:
                # send command
                safe_serial_write(conn, (command + '\r\n').encode())
            print(command)

    def _exit_handler():
        """Exit handler to stop the receiver thread."""
        stop_event.set()
        reciever.join(timeout=1)
        conn.close()

    signal.signal(signal.SIGINT, lambda s, f: _exit_handler())
    signal.signal(signal.SIGTERM, lambda s, f: _exit_handler())
    signal.signal(signal.SIGQUIT, lambda s, f: _exit_handler())

    if kwargs['interactive']:
        print('Entering interactive mode. '
              'Type commands to send them. and press `Ctrl+D` to exit.')
        # wait for the receiver thread to finish
        for line in sys.stdin:
            line = line.strip()
            safe_serial_write(conn, (line + '\r\n').encode())
        stop_event.set()
        reciever.join()
        return

    # wait for a while to receive feedback
    time.sleep(2)
    stop_event.set()
    reciever.join(timeout=1)

    conn.close()


if __name__ == '__main__':
    main()
