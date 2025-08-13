# tests/test.py

import sys
import os

# 添加 PySFS 到 sys.path，确保可以导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySFS.api_get import SFSGetAPI

def test_api():
    api = SFSGetAPI()
    print(api.rockets())  # 应输出 "API response"

if __name__ == "__main__":
    test_api()
