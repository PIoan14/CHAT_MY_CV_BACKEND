import toml

def get_config():
    config = toml.load("config.toml")
    return config

