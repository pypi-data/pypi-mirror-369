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

import requests

def get_monitor(ip,port=8754,filter=None):
    try:
        r = requests.get(f"http://{ip}:{port}/monitor.json")
        r.raise_for_status()
        if filter:
            return [item for item in r.json() if filter in item]
        else:
            return {"success": True, "data": r.json()}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_flights(ip,port=8754):
    try:
        r = requests.get(f"http://{ip}:{port}/flights.json")
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def exists(ip,port=8754):
    try:
        r = requests.get(f"http://{ip}:{port}/monitor.json")
        r.raise_for_status()
        assert "feed_status" in r.json()
        return {"exists": True}
    except requests.RequestException:
        return {"exists": False, "status": "cannot_connect"}
    except AssertionError:
        return {"exists": False, "status": "not_found"}
    except Exception:
        return {"exists": False, "status": "unknown"}