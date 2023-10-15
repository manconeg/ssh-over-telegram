from security import get_client
import paramiko
from paramiko.channel import ChannelStdinFile, ChannelFile, ChannelStderrFile
import threading
import asyncio
import signal

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
    callback = False

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
        print("listening to stdin")
        while self.running and (newLine := self.stdout.readline()):
            self.buffer += newLine
        print("stopping stdin")

    def _listenStderr(self):
        print("listen stderr")
        while self.running and (newLine := self.stderr.readline()):
            self.buffer += newLine
        print("stopping stderr")

    async def _sendMessage(self):
        print("watching for messages")
        localBuffer = ""
        lastBuffer = ""
        while self.running:
            print("running")

            while not localBuffer or (lastBuffer != localBuffer):
                lastBuffer = localBuffer
                if self.buffer:
                    newLine = self.buffer
                    self.buffer = ""
                    localBuffer += newLine
                await asyncio.sleep(.2)

            print (f"sending message {localBuffer}")
            await self.callback(localBuffer)
            localBuffer = ""
        print("stopping messager")

    def send(self, command) -> None:
        print(f'got command {command}')
        self.stdin.write(command + '\n')
        self.stdin.flush()