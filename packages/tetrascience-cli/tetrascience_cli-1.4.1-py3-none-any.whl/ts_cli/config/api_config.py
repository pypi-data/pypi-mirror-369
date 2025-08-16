from ts_cli.config.cli_config import CliConfig


class ApiConfig(CliConfig):
    """
    API configuration.
    Loads API configuration in the following order:
    1. Command line arguments
    2. Config file (from command line arguments)
    3. From the process's environment
    4. From the configuration in the user's home directory
    """

    def __init__(self, args):
        super().__init__(args)
        self._type = "API"
        self.org: str = self.get("org")
        self.api_url: str = self.get("api_url")
        self.auth_token: str = self.get("auth_token")
        self.ignore_ssl: str = self.get("ignore_ssl")
        self.keys = ["org", "api_url", "auth_token", "ignore_ssl"]
        self._print_config_keys(self, self.keys, self._type)
        self.validate(self.keys)

    def to_dict(self) -> dict:
        return {key: self.get(key) for key in self.keys}
