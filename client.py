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

    def __init__(self, client_info, callback):
        self.connection_info = client_info
        self.client = get_client(client_info)
        self.stdin, self.stdout, self.stderr = self.client.exec_command("/bin/bash")
        self.callback = callback
        self.listenStdin = threading.Thread(target=self._listenStdin)
        self.listenStderr = threading.Thread(target=self._listenStderr)
        self.sendMessage = asyncio.create_task(self._sendMessage())
        self.stdin._set_mode('b')
        self.stderr._set_mode('b')
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
        print("listen")
        while self.running and (newLine := self.stdout.read(1).decode("utf-8")):
            self.buffer += newLine
        print("stopping listener")

    def _listenStderr(self):
        print("listen")
        while self.running and (newLine := self.stderr.read(1).decode("utf-8")):
            self.buffer += newLine
        print("stopping listener")

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
            try:
                msgs = [localBuffer[i:i + 4096] for i in range(0, len(localBuffer), 4096)]
                for text in msgs:
                    await self.callback(text)
            except Exception as e:
                print(f'Exception {e}')
            localBuffer = ""
        print("stopping messager")

    def send(self, command) -> None:
        print(command)
        self.stdin.write(command + '\n')
        self.stdin.flush()