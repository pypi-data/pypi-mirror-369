from methodkit.utils.conditional import package_installed


def test_package_installation_detection() -> None:
    assert not package_installed("never_install_this"), "package installation detection failed"
