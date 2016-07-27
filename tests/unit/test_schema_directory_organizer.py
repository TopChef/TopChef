"""

"""
import os
import shutil
from topchef.config import config
import topchef.schema_directory_organizer as organizer
import pytest
from .test_models import service

PATH = os.path.join(config.BASE_DIRECTORY, 'schema_testing')


@pytest.yield_fixture()
def schema_directory():
    if not os.path.isdir(PATH):
        os.mkdir(PATH)

    yield

    shutil.rmtree(PATH)


def test_organizer_constructor(schema_directory):
    manager = organizer.SchemaDirectoryOrganizer(PATH)

    assert isinstance(manager, organizer.SchemaDirectoryOrganizer)
    assert manager.root_path == PATH


@pytest.yield_fixture()
def empty_manager(schema_directory):
    manager = organizer.SchemaDirectoryOrganizer(PATH)

    yield manager


def test_register_service(empty_manager, service):
    empty_manager.register_service(service)

    assert os.path.isdir(
        os.path.join(PATH, str(service.id))
    )
