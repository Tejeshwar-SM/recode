import json
import tempfile
import os
import asyncio
import subprocess
from channels.generic.websocket import AsyncWebsocketConsumer
from concurrent.futures import ThreadPoolExecutor

class CodeRunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pid = self.scope['url_route']['kwargs'].get('pid')
        self.executor = ThreadPoolExecutor()
        await self.accept()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            command = data.get('command')

            if command == 'run':
                files = data.get('files', [])
                entry = data.get('entry', 'main.py')
                self.temp_dir = tempfile.mkdtemp()

                # Write files to temp directory
                for f in files:
                    path = os.path.join(self.temp_dir, f['path'])
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'w') as fp:
                        fp.write(f['content'])

                # Start subprocess
                loop = asyncio.get_running_loop()
                self.proc = subprocess.Popen(
                    ['python', entry],
                    cwd=self.temp_dir,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Stream output
                asyncio.create_task(self.stream_output(loop))

            elif command == 'stdin':
                data_in = data.get('data', '')
                if hasattr(self, 'proc') and self.proc.stdin:
                    self.proc.stdin.write(data_in)
                    self.proc.stdin.flush()

        except Exception as e:
            await self.send_json_safe({'stream': 'error', 'data': str(e)})
            await self.close()

    async def stream_output(self, loop):
        # Read and stream stdout line by line
        def read_stdout():
            for line in self.proc.stdout:
                asyncio.run_coroutine_threadsafe(
                    self.send_json_safe({'stream': 'stdout', 'data': line}),
                    loop
                )

        # Read entire stderr
        def read_stderr():
            error_output = self.proc.stderr.read()
            if error_output:
                asyncio.run_coroutine_threadsafe(
                    self.send_json_safe({'stream': 'stderr', 'data': error_output}),
                    loop
                )

        # Run both in background threads
        await loop.run_in_executor(self.executor, read_stdout)
        await loop.run_in_executor(self.executor, read_stderr)

        return_code = self.proc.wait()
        await self.send_json_safe({'stream': 'exit', 'code': return_code})

    async def disconnect(self, close_code):
        if hasattr(self, 'proc') and self.proc:
            self.proc.kill()
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass

    async def send_json_safe(self, data: dict):
        """
        A helper to send JSON via WebSocket safely
        (can be used inside thread-safe calls).
        """
        try:
            await self.send(text_data=json.dumps(data))
        except Exception as e:
            print(f"Send failed: {e}")
