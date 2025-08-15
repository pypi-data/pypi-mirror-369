from zenable_mcp.user_config.file_provider import File, FileProvider


class LocalFileProvider(FileProvider):
    """
    File provider for local files.
    """

    def find_and_get_one_file(self, file_names: list[str]) -> File:
        raise NotImplementedError

    def find_files(self, file_names: list[str]) -> list[str]:
        raise NotImplementedError

    def get_file(self, file_path: str) -> str:
        raise NotImplementedError
