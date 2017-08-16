"""
Contains generators for a job that is not committed to a DB session
"""
from hypothesis.strategies import composite
from hypothesis.strategies import dictionaries, text
from topchef.database.models import Job
from tests.unit.database_model_generators import services as service_generator


@composite
def jobs(
        draw,
        services=service_generator(),
        parameters=dictionaries(text(), text()),
) -> Job:
    return Job.new(
        draw(services),
        draw(parameters)
    )
