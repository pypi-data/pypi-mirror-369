
from NGPIris.hcp import HCPHandler
from NGPIris.hcp.helpers import check_mounted


class HCPStatistics(HCPHandler):
    def __init__(self, credentials_path: str, use_ssl: bool = False, proxy_path: str = "", custom_config_path: str = "") -> None:
        super().__init__(credentials_path, use_ssl, proxy_path, custom_config_path)

    @check_mounted
    def get_namespace_settings(self) -> dict:
        return self.get_response("/namespaces/" + self.bucket_name) #type: ignore

    @check_mounted
    def get_namespace_statistics(self) -> dict:
        return self.get_response("/namespaces/" + self.bucket_name + "/statistics") #type: ignore

    @check_mounted
    def get_namespace_permissions(self) -> dict:
            return self.get_response("/namespaces/" + self.bucket_name + "/permissions") #type: ignore
