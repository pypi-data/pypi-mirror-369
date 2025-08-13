import requests
from packaging.version import Version

def get_latest_django_versions(package_name, limit=5):
    url= f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        all_versions = list(data["releases"].keys())
        
        stable_versions = [
            v for v in all_versions
            if not any(suffix in v for suffix in ['a', 'b', 'rc', 'dev'])
        ]
        
        stable_versions = sorted(stable_versions, key=Version, reverse=True)
        
        return stable_versions[:limit]
    except Exception as e:
        print("Error")
        return ["5.0.4", "4.2.11", "manual input..."]