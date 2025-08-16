# Copyright 2025 Lordseriouspig
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import src.pi24_monitor

class TestPi24Monitor:
    def test_get_monitor(self):
        result = src.pi24_monitor.get_monitor("192.168.1.190", 8754)
        print(result)
        assert "error" not in result
    def test_get_flights(self):
        result = src.pi24_monitor.get_flights("192.168.1.190", 8754)
        print(result)
        assert "error" not in result
    def test_monitor_filter(self):
        result = src.pi24_monitor.get_monitor("192.168.1.190", 8754, filter="shutdown")
        print(result)
        assert "error" not in result
        assert all("shutdown" in item for item in result)