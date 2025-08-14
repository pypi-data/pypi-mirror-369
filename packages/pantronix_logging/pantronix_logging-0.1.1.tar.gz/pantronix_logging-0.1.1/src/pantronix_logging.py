import pathlib
import re
import time
import typer
import socket
import os
import rich.console


def mainapp(target_host: str = "localhost", target_port: int = 19021, rtt_search_start_address: str = "0x20000000", rtt_search_size: str = "0x10000", regex: str = ".", logfile: pathlib.Path = os.devnull):
    """Connect to a Segger RTT server and display log messages.

    This supports filtering using python style regular expressions.
    The location of the RTT buffer needs to be specified by the rtt_address parameter, autodetection and searching is not supported.

    """
    try:
        rtt_search_start_address = int(rtt_search_start_address, 0)
        rtt_search_size = int(rtt_search_size, 0)
        s, f = connect_to_datasource(target_host, target_port, rtt_search_start_address, rtt_search_size)

        regex = re.compile(regex)

        with open(logfile, 'w') as log_file:
            while True:
                try:
                    line = f.readline().strip()
                    if line and (regex is None or bool(regex.search(line))):
                        print(line)
                        log_file.write(line + os.linesep)
                except socket.timeout:
                    f = s.makefile('r')
                except ConnectionResetError:
                    print("Connection reset. This is normal if the debugging session has ended.")
                    print("trying to reconnect...")
                    while True:
                        try:
                            s, f = connect_to_datasource(target_host, target_port, rtt_search_start_address, rtt_search_size)
                            break
                        except ConnectionRefusedError:
                            time.sleep(0.25)
    except KeyboardInterrupt:
        print("Exiting on keyboard interrupt.")
    except re.error:
        console = rich.console.Console()
        console.print("[yellow]Invalid regex pattern:[/yellow]")
        print(f"{regex}")
    except Exception as e:
        print(f"An error occurred: {e}")

def connect_to_datasource(target_host, target_port, rtt_search_start_address, rtt_search_size):
    s = socket.socket()
    s.connect((target_host, target_port))
    f = s.makefile('r')
    for _ in range(3):
        initLine = f.readline().strip()
        print(initLine)
    s.send(f"$$SEGGER_TELNET_ConfigStr=RTTCh;0;SetRTTSearchRanges;0x{rtt_search_start_address:0x} 0x{rtt_search_size:0x};$$\n".encode('utf-8'))
    s.settimeout(0.25)
    return s, f


def main():
    typer.run(mainapp)

if __name__ == "__main__":
    main()
