#!/usr/bin/env python3

import asyncio
import os
import time
import pytest

dir = os.path.split(os.path.realpath(__file__))[0]

# @pytest.fixture(scope="module")
# def restart():
#     os.system("docker restart syncd")
#     f = os.popen("docker ps", 'r')
#     res = f.read(500)
#     while True:
#         time.sleep(5)
#         if "syncd" in res:
#             break


class TestNRSDS:
    def work(self):
        # f = os.popen(f"docker exec -ti syncd python3 /usr/bin/Non_Reside_SDS.py dump_temperatures", 'r')
        f = os.popen(f'python3 /usr/bin/NRSDS/Non_Reside_SDS.py dump_temperatures', 'r')
        # time.sleep(1)
        print(f.read(1000))
        print("\n")
        assert f.read(1000) is not None

    async def work_async(self):
        # f = os.popen(f'docker exec -ti syncd python3 /usr/bin/Non_Reside_SDS.py dump_temperatures', 'r')
        f = os.popen(f'python3 /usr/bin/NRSDS/Non_Reside_SDS.py dump_temperatures', 'r')
        # time.sleep(1)
        print(f.read(1000))
        print("\n")
        assert f.read(1000) is not None

    @pytest.mark.asyncio
    async def test_coroutine(self):
        print("test1\n")
        event = []
        loop = asyncio.get_event_loop()
        for i in range(5):
            event.append(asyncio.create_task(self.work_async()))
        loop.call_soon(asyncio.gather(*event))

    def test_continuous(self):
        print("test2\n")
        for i in range(5):
            self.work()
