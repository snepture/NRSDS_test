#!/usr/bin/env python3
# BEGIN_LEGAL
#
# Copyright (c) 2019-current, Cisco Systems, Inc. ("Cisco"). All Rights Reserved.
#
# This file and all technical concepts, proprietary knowledge, algorithms and
# intellectual property rights it contains (collectively the "Confidential Information"),
# are the sole propriety information of Cisco and shall remain at Cisco's ownership.
# You shall not disclose the Confidential Information to any third party and you
# shall use it solely in connection with operating and/or maintaining of Cisco's
# products and pursuant to the terms and conditions of the license agreement you
# entered into with Cisco.
#
# THE SOURCE CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
# IN NO EVENT SHALL CISCO BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH
# THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# END_LEGAL

# Sai debug shell (sds) utility.
# This is the client side of the non-reside sai debug shell utility.


import asyncio
import os
import re
import sys
import ParseTemplate
import yaml

SAI_DEBUG_SHELL_URI = '/var/run/sai_debug_shell.sock'
LEABA_VALIDATION_PATH = '/usr/lib/cisco/pylib/leaba/debug_tools/hw_tables/lpm'
LEABA_SDK_PATH = '/usr/lib/cisco/pylib/leaba'

HOST = '127.0.0.1'
PORT = 12345


class SocketClient(object):
    def __init__(self):
        self.writer = None
        self.reader = None

    async def connect_with_port(self, host, port):
        self.reader, self.writer = await asyncio.open_connection(host, port)
        print("Connected to {}:{}".format(host, port))

    async def connect_with_unix(self, unix_file):
        self.reader, self.writer = await asyncio.open_unix_connection(unix_file)
        print("Connected to {}".format(unix_file))

    async def read(self):
        res = ""
        if self.reader:
            data = await self.reader.readline()
            if data.decode('utf-8').startswith('>>>'):
                res = data.decode('utf-8').replace('>>>', '').strip()
            else:
                res = data.decode('utf-8')
        return res

    def write(self, message):
        if self.writer:
            message = message + '\n'
            # print("send:{}".format(message))
            self.writer.write(message.encode('utf-8'))
            # await self.writer.drain()

    async def close(self):
        self.writer.close()


async def connect(socketclient):
    basename = os.path.splitext(os.path.basename(SAI_DEBUG_SHELL_URI))[0]
    output = os.popen('netstat -an').read()
    for line in output.splitlines():
        if re.match("unix.*%s.*" % basename, line):
            try:
                if await asyncio.wait_for(socketclient.connect_with_unix(SAI_DEBUG_SHELL_URI), timeout=2):
                    return True
            except asyncio.TimeoutError:
                print("Timeout connecting unix.")

        if re.match("tcp.*12345.*LISTEN", line):
            try:
                if await asyncio.wait_for(socketclient.connect_with_port(HOST, PORT), timeout=2):
                    return True
            except asyncio.TimeoutError:
                print("Timeout connecting port.")


async def buf_read(socketclient):
    while True:
        msg = await socketclient.read()
        print(msg)


async def check_init(socketclient):
    f = open('config.yaml', 'r', encoding='utf-8')
    cont = f.read()
    x = yaml.safe_load(cont).get("default")
    LEABA_SDK_PATH = x.get("LEABA_SDK_PATH")
    LEABA_VALIDATION_PATH = x.get("LEABA_VALIDATION_PATH")
    init_pack = f"""
                import sys\n \
                import os\n \
                sys.path.append(\"{LEABA_SDK_PATH}/..\")\n \
                sys.path.append(\"{LEABA_SDK_PATH}\")\n   \
                sys.path.append(\"{LEABA_SDK_PATH}/debug_tools\")\n   \
                sys.path.append(\"{LEABA_SDK_PATH}/debug_tools/hw_tables/lpm\")\n \
                sys.LEABA_SDK_PATH=\"{LEABA_SDK_PATH}\"\n \
                sys.LEABA_VALIDATION_PATH=\"{LEABA_VALIDATION_PATH}\"\n    \
                sys.path.append(sys.LEABA_VALIDATION_PATH)\n    \
                sys.path.append(sys.LEABA_SDK_PATH)\n   \
                from leaba import sdk\n \
                la_device = sdk.la_get_device(0)\n  \
                from leaba_val import *\n   \
                os.environ['BASE_OUTPUT_DIR'] = \"/opt/cisco/silicon-one/\"\n   \
                set_dev(la_device)\n    \
                from leaba.debug_api import *\n \
                dapi = DebugApi()\n \
                from leaba.dbg import *\n   \
                dbg=dbg_dev(la_device)\n    \
                """

    eg = f"print('{LEABA_SDK_PATH}/debug_tools' in sys.path)\n"
    try:
        socketclient.write(eg)
    except Exception as e:
        print("Error: " + str(e))
    while True:
        res = await socketclient.read()
        if "True" in res or "sys" in res:
            break

    if "True" in res:
        print("Packets are already loaded.")
    else:
        for line in init_pack.split('\n'):
            command = line.strip() + '\n'
            socketclient.write(command)
        print("***First time run***\nPlease wait for a moment until packets are loaded...")
        while True:
            await socketclient.reader.readline()
        # await asyncio.sleep(10)


async def main():
    parsetemp = ParseTemplate.OperateTemplate()

    command, t = parsetemp.generate_command(sys.argv[1])

    sock = SocketClient()
    await connect(sock)

    try:
        await asyncio.wait_for(check_init(sock), timeout=10)
    except asyncio.TimeoutError:
        print("Loading packet timeout.")

    try:
        sock.write(command)
    except Exception as e:
        print("Error: " + str(e))
    try:
        await asyncio.wait_for(buf_read(sock), timeout=t)
    except asyncio.TimeoutError:
        print("Read timeout~ \nIf not load full,please set --settimeout")

    await asyncio.wait_for(sock.close(), timeout=5)


if __name__ == '__main__':
    asyncio.run(main())
