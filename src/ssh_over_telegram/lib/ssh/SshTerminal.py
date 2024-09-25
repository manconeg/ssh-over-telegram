import logging
import signal
import sys
import threading
import time
from types import FrameType

import paramiko
from paramiko.channel import ChannelStdinFile, ChannelFile, ChannelStderrFile
from typing_extensions import override

from .Security import get_client
from ...interface.Terminal import Terminal

log = logging.getLogger('ssh-client')


class SshTerminal(Terminal):
    client: paramiko.SSHClient = None
    connection_info = None
    stdin: ChannelStdinFile = None
    stdout: ChannelFile = None
    stderr: ChannelStderrFile = None
    listenStdin: threading.Thread
    listenStderr: threading.Thread
    input_buffer = ''
    output_buffer = False
    running: bool = True
    timeout = .01

    def __init__(self, client_info):
        self.connection_info = client_info
        self.client = get_client(client_info)
        self.stdin, self.stdout, self.stderr = self.client.exec_command('bash')
        self.listenStdin = threading.Thread(target=self._listen_stdin)
        self.listenStderr = threading.Thread(target=self._listen_stderr)
        self.sendMessage = threading.Thread(target=self._buffer_output)
        self.listenStdin.daemon = True
        self.listenStderr.daemon = True
        self.listenStdin.start()
        self.listenStderr.start()
        self.sendMessage.start()
        signal.signal(signal.SIGINT, self._close)

    def _close(self, sig: int, frame_type: FrameType):
        log.info('closed')
        self.running = False
        self.client.close()
        self.listenStdin.join()
        self.listenStderr.join()
        self.sendMessage.join()
        sys.exit(0)

    def _listen_stdin(self):
        log.info('listening to stdin')
        while self.running and (new_line := self.stdout.readline()):
            self.input_buffer += new_line
        log.info('stdin stopped')

    def _listen_stderr(self):
        log.info('listen stderr')
        while self.running and (new_line := self.stderr.readline()):
            self.input_buffer += new_line
        log.info(f'stderr stopped')

    def _buffer_output(self):
        log.info(f'watching for messages')
        local_buffer = ''
        last_buffer = ''
        while self.running:
            log.info(f'running')

            while self.running and (not local_buffer or (last_buffer != local_buffer)):
                last_buffer = local_buffer
                if self.input_buffer is not False:
                    new_line = self.input_buffer
                    self.input_buffer = ''
                    local_buffer += new_line
                time.sleep(.1)

            log.info(f'sending message {local_buffer}')
            self.output_buffer = local_buffer
            local_buffer = ''
        log.info(f'stopping messenger')

    @override
    async def send(self, command) -> str:
        log.info(f'got command {command}')
        self.stdin.write(f'{command}; echo **EXECUTION COMPLETE**\n')
        self.stdin.flush()
        while self.output_buffer is False:
            time.sleep(.1)
        output = self.output_buffer
        self.output_buffer = False
        return output
