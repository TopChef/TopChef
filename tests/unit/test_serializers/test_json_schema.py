"""
Contains unit tests for :mod:`topchef.serializers.json_schema`
"""
import unittest
import unittest.mock as mock
from hypothesis import given
from hypothesis.strategies import text
from marshmallow import Schema, fields
from marshmallow_jsonschema import JSONSchema as MarshmallowJSONSchema
from topchef.serializers.json_schema import JSONSchema


class TestJSONSchema(unittest.TestCase):
    """
    Set up some fixed data for the serializer, along with a mock serializer
    """
    def setUp(self) -> None:
        self.schema_url = 'http://json-schema.org/draft-04/schema#'
        self.title = 'Unit testing schema'
        self.description = 'Unit testing schema description'
        self.marshmallow_jsonschema = mock.MagicMock(
            spec=MarshmallowJSONSchema
        )  # type: MarshmallowJSONSchema

    class UnitTestingSchema(Schema):
        """
        A simple schema to serialize
        """
        data = fields.Str()


class TestConstructor(TestJSONSchema):
    """
    Contains unit tests for
    :meth:`topchef.serializers.json_schema.JSONSchema.__init__`
    """

    @given(text(), text(), text())
    def test_all_constructor_args(
            self,
            schema_url: str,
            title: str,
            description: str
    ) -> None:
        """
        Test that when metadata is provided ,the system is initialized
        correctly

        :param schema_url: A randomly-generated string representing a URL to
            the base JSON schema
        :param title: A randomly-generated title
        :param description: A randomly-generated description
        """
        schema = JSONSchema(
            schema=schema_url,
            title=title,
            description=description,
            json_schema_serializer=self.marshmallow_jsonschema
        )

        self.assertEqual(
            schema.schema,
            schema_url
        )
        self.assertEqual(
            schema.description,
            description
        )
        self.assertEqual(
            schema.title,
            title
        )

    def test_minimum_args(self) -> None:
        """
        Tests that initialization can happen with the minimum number of
        arguments
        """
        schema = JSONSchema()
        self.assertIsInstance(schema.schema, str)
        self.assertIsNone(schema.title)
        self.assertIsNone(schema.description)


class TestDump(TestJSONSchema):
    """
    Contains unit tests for
    :meth:`topchef.serializers.json_schema.JSONSchema.dump`
    """
    def setUp(self) -> None:
        """
        Prepare an instance of the marshmallow schema, along with a serializer
        """
        TestJSONSchema.setUp(self)
        self.schema_to_serialize = self.UnitTestingSchema()
        self.serializer = JSONSchema()

    def test_dump_single(self):
        """
        Test that the schema serializes to a ``dict``
        """
        result = self.serializer.dump(self.schema_to_serialize)
        self.assertIsInstance(result, dict)

    @given(text(), text(), text())
    def test_schema_dump_metadata(
            self,
            schema_url: str,
            title: str,
            description: str
    ):
        """
        Given some metadata, test that the metadata appears in the output
        schema

        :param schema_url: A randomly-generated string representing a URL to
            the base JSON schema
        :param title: A randomly-generated title
        :param description: A randomly-generated description
        """
        json_schema = JSONSchema(schema_url, title, description)
        result = json_schema.dump(self.schema_to_serialize)

        self.assertEqual(
            description, result['description']
        )
        self.assertEqual(
            title, result['title']
        )
        self.assertEqual(
            schema_url, result['$schema']
        )


class TestDumps(TestJSONSchema):
    """
    Contains unit tests for
    :meth:`topchef.serializers.json_schema.JSONSchema.dumps
    """
    def test_dumps(self):
        """
        Test that the system dumps to a string correctly
        """
        schema = self.UnitTestingSchema()
        serializer = JSONSchema()
        self.assertIsInstance(serializer.dumps(schema), str)
