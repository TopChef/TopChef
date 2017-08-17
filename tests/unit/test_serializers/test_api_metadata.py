"""
Contains unit tests for :mod:`topchef.serializers.api_metadata`
"""
import unittest
import unittest.mock as mock
from topchef.serializers import APIMetadata
from topchef.models import APIMetadata as APIMetadataModel
from hypothesis import given
from hypothesis.strategies import text


class TestAPIMetadata(unittest.TestCase):
    """
    Base class for testing API metadata
    """
    def setUp(self) -> None:
        """
        Create a fake metadata model to serialize
        """
        self.model = mock.MagicMock(spec=APIMetadataModel)
        self.serializer = APIMetadata()


class TestFieldSerialization(TestAPIMetadata):
    """
    Tests that the fields are correctly serialized
    """
    def setUp(self) -> None:
        """
        Write down the values for the keys of the field names in the
        serializer to look up
        """
        TestAPIMetadata.setUp(self)
        self.maintainer_name_key = 'maintainer_name'
        self.maintainer_email_key = 'maintainer_email'

        self.model.maintainer_email = 'email@maintainer.com'

    @given(text())
    def test_maintainer_name(self, maintainer_name: str) -> None:
        """
        Tests that the ``maintainer_name`` field is correctly serialized
        """
        self.model.maintainer_name = maintainer_name
        data, _ = self.serializer.dump(self.model)
        self.assertEqual(data[self.maintainer_name_key], maintainer_name)

    def test_maintainer_email(self) -> None:
        """
        Tests that the ``maintainer_email`` field is correctly serialized
        """
        data, _ = self.serializer.dump(self.model)
        self.assertEqual(
            data[self.maintainer_email_key], self.model.maintainer_email
        )
