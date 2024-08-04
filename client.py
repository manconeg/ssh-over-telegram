from security import get_client
import paramiko
from paramiko.channel import ChannelStdinFile, ChannelFile, ChannelStderrFile
import threading
import asyncio
import signal
import logging

log = logging.getLogger("ssh-client")

class Client:
    client: paramiko.SSHClient = None
    connection_info = None
    stdin: ChannelStdinFile = None
    stdout: ChannelFile = None
    stderr: ChannelStderrFile = None
    listenStdin: threading.Thread
    listenStderr: threading.Thread
    buffer = ""
    running: bool = True
    timeout = .01
    toSend = False

    def __init__(self, client_info):
        self.connection_info = client_info
        self.client = get_client(client_info)
        self.stdin, self.stdout, self.stderr = self.client.exec_command("/bin/bash")
        self.listenStdin = threading.Thread(target=self._listenStdin)
        self.listenStderr = threading.Thread(target=self._listenStderr)
        self.sendMessage = asyncio.create_task(self._sendMessage())
        self.listenStdin.daemon = True
        self.listenStderr.daemon = True
        self.listenStdin.start()
        self.listenStderr.start()
        signal.signal(signal.SIGINT, self._close)

    def _close(self):
        self.client.close()
        self.running = False
        self.thread.join()

    def _listenStdin(self):
        log.info("listening to stdin")
        while self.running and (newLine := self.stdout.readline()):
            self.buffer += newLine
        log.info("stopping stdin")

    def _listenStderr(self):
        log.info("listen stderr")
        while self.running and (newLine := self.stderr.readline()):
            self.buffer += newLine
        log.info("stopping stderr")

    async def _sendMessage(self):
        log.info("watching for messages")
        localBuffer = ""
        lastBuffer = ""
        while self.running:
            log.info("running")

            while not localBuffer or (lastBuffer != localBuffer):
                lastBuffer = localBuffer
                if self.buffer:
                    newLine = self.buffer
                    self.buffer = ""
                    localBuffer += newLine
                await asyncio.sleep(.2)

            log.info(f"sending message {localBuffer}")
            self.toSend = localBuffer
            localBuffer = ""
        log.info("stopping messager")

    async def send(self, command) -> str:
        log.info(f'got command {command}')
        self.stdin.write(command + '\n')
        self.stdin.flush()
        while (self.toSend is False):
            await asyncio.sleep(.2)
        send = self.toSend
        self.toSend = False
        return send
