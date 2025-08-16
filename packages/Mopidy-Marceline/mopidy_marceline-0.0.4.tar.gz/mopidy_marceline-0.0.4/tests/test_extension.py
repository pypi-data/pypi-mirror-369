from mopidy_marceline import Extension


def test_get_default_config() -> None:
    ext = Extension()

    config = ext.get_default_config()

    assert "[marceline]" in config
    assert "enabled = true" in config
