"""

"""
import os
import shutil
from topchef.config import config
from topchef.models import Service, Job
import topchef.schema_directory_organizer as organizer
import pytest

PATH = os.path.join(config.BASE_DIRECTORY, 'schema_testing')
SERVICE_NAME = 'TestService'

@pytest.yield_fixture()
def schema_directory(monkeypatch):
    if not os.path.isdir(PATH):
        os.mkdir(PATH)

    monkeypatch.setattr('topchef.config.Config.SCHEMA_DIRECTORY', PATH)

    yield

    shutil.rmtree(PATH)


@pytest.yield_fixture()
def empty_manager(schema_directory):
    manager = organizer.SchemaDirectoryOrganizer(PATH)

    yield manager


def test_organizer_constructor(schema_directory):
    manager = organizer.SchemaDirectoryOrganizer(PATH)

    assert isinstance(manager, organizer.SchemaDirectoryOrganizer)
    assert manager.root_path == PATH


def test_services_empty(empty_manager):
    assert empty_manager.services == []


@pytest.yield_fixture()
def manager_with_service(empty_manager):

    service = Service(SERVICE_NAME, organizer=empty_manager)

    yield (empty_manager, service)


def test_getitem_for_service(manager_with_service):
    manager = manager_with_service[0]
    service = manager_with_service[1]

    assert manager[service] == os.path.join(manager.root_path, str(service.id))


@pytest.yield_fixture
def manager_with_job(manager_with_service):
    manager = manager_with_service[0]

    job = Job(manager_with_service[1], {'value': True}, file_manager=manager)

    yield manager, manager_with_service[1], job
   

def test_getitem_for_job(manager_with_job):
    manager, service, job = manager_with_job
    assert manager[job] == os.path.join(
        manager.root_path, str(service.id), '%s.json' % str(job.id)
    )


def test_getitem_error(empty_manager):
    with pytest.raises(ValueError):
        empty_manager['foo']