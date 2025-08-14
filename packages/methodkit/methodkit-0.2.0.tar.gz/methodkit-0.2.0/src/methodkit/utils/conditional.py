import importlib.metadata


def package_installed(package_name: str) -> bool:
    try:
        _ = importlib.metadata.distribution(package_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False
