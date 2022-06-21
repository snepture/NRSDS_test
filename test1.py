#!/usr/bin/env python3
import pytest
import os

dir = os.path.split(os.path.realpath(__file__))[0]
# def test_one():
#     print("test_one")
#     assert 1
#
#
# class TestClass:
#     def test_two(self):
#         print("Test_two")
#         assert 1
#
#     def test_three(self):
#         f = os.popen(f'python3 {dir}/test.py', 'r')
#         res = f.read(500)
#         assert res

if __name__ == '__main__':
    # os.system("ifconfig")
    f = os.popen("ifconfig",'r')
    print(f.read(500))