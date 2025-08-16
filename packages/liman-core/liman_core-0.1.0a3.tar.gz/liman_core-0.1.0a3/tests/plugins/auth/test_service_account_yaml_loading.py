from pathlib import Path

import pytest
from ruamel.yaml.error import YAMLError

from liman_core.errors import InvalidSpecError
from liman_core.plugins.auth import ServiceAccount
from liman_core.registry import Registry

TEST_DATA_PATH = Path(__file__).parent / "data"


@pytest.fixture
def registry() -> Registry:
    return Registry()


def test_from_yaml_path_valid_file(registry: Registry) -> None:
    yaml_path = TEST_DATA_PATH / "valid_service_account.yaml"
    service_account = ServiceAccount.from_yaml_path(str(yaml_path), registry)
    assert service_account.spec.name == "TestServiceAccount"
    assert service_account.spec.credentials_provider == "AWSCredentials"


def test_from_yaml_path_sets_yaml_path(registry: Registry) -> None:
    yaml_path = TEST_DATA_PATH / "valid_service_account.yaml"
    service_account = ServiceAccount.from_yaml_path(str(yaml_path), registry)
    assert service_account.yaml_path == str(yaml_path)


def test_from_yaml_path_strict_mode(registry: Registry) -> None:
    yaml_path = TEST_DATA_PATH / "valid_service_account.yaml"
    service_account = ServiceAccount.from_yaml_path(
        str(yaml_path), registry, strict=True
    )
    assert service_account.strict is True


def test_from_yaml_path_nonexistent_file(registry: Registry) -> None:
    with pytest.raises(FileNotFoundError):
        ServiceAccount.from_yaml_path("/nonexistent/path.yaml", registry)


def test_from_yaml_path_empty_file(registry: Registry) -> None:
    yaml_path = TEST_DATA_PATH / "empty.yaml"
    with pytest.raises(InvalidSpecError):
        ServiceAccount.from_yaml_path(str(yaml_path), registry)


def test_from_yaml_path_malformed_yaml(registry: Registry) -> None:
    yaml_path = TEST_DATA_PATH / "malformed.yaml"
    with pytest.raises(YAMLError):
        ServiceAccount.from_yaml_path(str(yaml_path), registry)


def test_from_yaml_path_invalid_service_account_spec(registry: Registry) -> None:
    yaml_path = TEST_DATA_PATH / "invalid_service_account.yaml"
    with pytest.raises(InvalidSpecError):
        ServiceAccount.from_yaml_path(str(yaml_path), registry)
