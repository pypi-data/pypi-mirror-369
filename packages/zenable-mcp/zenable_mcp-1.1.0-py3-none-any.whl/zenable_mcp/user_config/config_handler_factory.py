def get_local_config_handler():
    """
    Factory function to create the default local config handler.
    """
    raise NotImplementedError

    # zenable_context = trace_context.zenable_context
    # config_file_name = "zenable_config"

    # file_provider = _LocalFileProvider()
    # config_parsers = [_UserTomlConfigParser(), _UserYamlConfigParser()]
    # config_handler = _FileConfigHandler(file_provider, config_parsers, config_file_name)

    # return config_handler
