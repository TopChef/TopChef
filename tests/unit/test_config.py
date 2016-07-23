from topchef.config import Config


def test_config():
    environment = {'DEBUG': 'False'}

    config = Config(environment)

    assert not config.DEBUG