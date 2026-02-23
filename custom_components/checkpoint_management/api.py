import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class CheckPointApiClient:
    def __init__(self, host, port, username, password, verify_ssl=False):
        self.base_url = f"https://{host}:{port}/web_api"
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.sid = None

    async def _request(self, endpoint, payload=None):
        headers = {"Content-Type": "application/json"}
        if self.sid:
            headers["X-chkp-sid"] = self.sid

        connector = aiohttp.TCPConnector(verify_ssl=self.verify_ssl)
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                async with session.post(f"{self.base_url}/{endpoint}", json=payload or {}, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                _LOGGER.error(f"Error calling {endpoint}: {e}")
                return None

    async def login(self):
        payload = {"user": self.username, "password": self.password}
        data = await self._request("login", payload)
        if data and "sid" in data:
            self.sid = data["sid"]
            return True
        return False

    async def logout(self):
        if self.sid:
            await self._request("logout")
            self.sid = None

    async def get_packages(self):
        data = await self._request("show-packages", {"limit": 100})
        if data and "packages" in data:
            return [pkg["name"] for pkg in data["packages"]]
        return []

    async def _get_layer(self, package):
        data = await self._request("show-package", {"name": package, "details-level": "standard"})
        if data and "access-layers" in data and len(data["access-layers"]) > 0:
            return data["access-layers"][0]["name"]
        return "Network"

    async def get_object_count(self, endpoint, package=None):
        payload = {"limit": 500} 
        
        if endpoint == "show-access-rulebase":
            layer = await self._get_layer(package)
            payload = {"offset": 0, "limit": 1, "name": layer, "details-level": "standard"}
            
        elif endpoint == "show-nat-rulebase":
            payload = {"offset": 0, "limit": 1, "package": package, "details-level": "standard"}
            
        data = await self._request(endpoint, payload)
        if data and "total" in data:
            return data["total"]
        return 0

    async def get_all_access_rules(self, package):
        layer = await self._get_layer(package)
        payload = {
            "name": layer, 
            "details-level": "standard", 
            "limit": 500, 
            "offset": 0,
            "show-hits": True
        }
        data = await self._request("show-access-rulebase", payload)
        rules = []
        if data and "rulebase" in data:
            rules = self._extract_rules(data["rulebase"])
        return rules

    def _extract_rules(self, rulebase):
        rules = []
        for item in rulebase:
            if "rulebase" in item:
                rules.extend(self._extract_rules(item["rulebase"]))
            elif "rule-number" in item:
                rules.append(item)
        return rules

    async def set_access_rule_state(self, uid, package, enabled: bool):
        layer = await self._get_layer(package)
        payload = {"uid": uid, "layer": layer, "enabled": enabled}
        return await self._request("set-access-rule", payload)

    async def publish(self):
        return await self._request("publish", {})

    async def install_policy(self, package):
        payload = {"policy-package": package, "access": True, "threat-prevention": False}
        data = await self._request("install-policy", payload)
        return data is not None

    async def get_gateways_and_servers(self):
        data = await self._request("show-gateways-and-servers", {"details-level": "standard", "limit": 500})
        gateways_data = {"types": {}, "mgmt_servers": []}
        
        if data and "objects" in data:
            for obj in data["objects"]:
                obj_type = obj.get("type", "Unknown")
                gateways_data["types"][obj_type] = gateways_data["types"].get(obj_type, 0) + 1
                if obj_type == "CpmiHostCkp":
                    gateways_data["mgmt_servers"].append(obj.get("name"))
                    
        return gateways_data

    async def install_database(self, targets):
        payload = {"targets": targets}
        data = await self._request("install-database", payload)
        return data is not None

    async def verify_management_license(self):
        return await self._request("verify-management-license", {})

    async def show_cloud_services(self):
        return await self._request("show-cloud-services", {})
