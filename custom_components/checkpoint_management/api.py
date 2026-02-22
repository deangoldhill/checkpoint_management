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

    async def get_object_count(self, endpoint, package=None):
        payload = {"limit": 500} # As requested
        if package and endpoint in ["show-access-rulebase", "show-nat-rulebase"]:
            payload["name"] = package
            
        data = await self._request(endpoint, payload)
        if data and "total" in data:
            return data["total"]
        return 0

    async def install_policy(self, package):
        payload = {"policy-package": package, "access": True}
        data = await self._request("install-policy", payload)
        return data is not None
