"""

"""
from topchef.database.models.service import Service
from hypothesis.strategies import composite
from hypothesis.strategies import text, dictionaries


@composite
def services(
        draw,
        names=text(),
        descriptions=text(),
        registration=dictionaries(text(), text()),
        results=dictionaries(text(), text())
) -> Service:
    return Service.new(
        name=draw(names),
        description=draw(descriptions),
        registration_schema=draw(registration),
        result_schema=draw(results)
    )
