from topchef.config import Config


def test_config():
    environment = {'DEBUG': 'False'}

    config = Config(environment)

    assert not config.DEBUG


def test_port():
    environment = {"PORT": "12321"}

    config = Config(environment)

    assert config.PORT == 12321
