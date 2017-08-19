Unit Testing With ``unittest`` and ``hypothesis``
=================================================

TopChef is committed to testing code as much as possible. The
:mod:`unittest` library provides tools for declaring test cases. The
:mod:`nose` library is used to collect the tests defined in
:mod:`unittest`, and run them from the command line.

The purpose of a unit test is to isolate one specific component from the
rest of the code, and to test that the component runs according to some
specification. The smallest unit of testing is a test case. With unit tests,
a useful level of where to start testing is at the level of a conditional in
a function. Ideally, every conditional branch of code will be unit tested.
If there is an ``if`` statement in the code, then each branch of that ``if``
statement should be tested.

Unit tests are also useful for debugging purposes. If a user reports a bug,
an attempt should be made to reproduce the bug by writing a unit test.
Confirmation of the bug will be seen by the unit test failing. Confirmation
of the bug fix will be seen by the unit test passing. Confirmation of the
fix not breaking other code will be seen by the rest of the unit tests passing.

The pattern of behaviour for a unit test is "action-assert." This means that
each test case should do something, and then assert that the outcome took
place.

Example: Unit testing the factorial function
--------------------------------------------

Let's start with a simple factorial function

.. sourcecode:: python

    def factorial(n: int) -> int:
        """
        Calculate the factorial for a number using the recursive definition
        of a factorial as

        .. math::

            n! = \begin{cases}
                0 & n = 0 \\
                (n - 1)! & n > 0
            \end{cases}

        :param n: The number for which the factorial is to be calculated
        :return: The factorial of ``n``
        """
        if n < 0:
            raise ValueError(
            'Attempted to calculate a factorial for a'
            'number less than 0'
            )
        if n == 0:
            return 1
        else:
            return factorial(n - 1)

To fully cover this code, we will need three test cases. One test case will
be needed to check that :class:`ValueError` is raised when ``n < 0``.
One test case will be needed to check that ``factorial(0) == 1``, and then
one test case will be needed to check whether the recursive definition works
correctly.

In this project, it is recommended that each function has a class associated
with it that inherits from :class:`unittest.TestCase`. In order for
:mod:`nose` to recognize the class as a test, the class will have to begin
with ``Test`` or end with ``Test``. In order for nose to recognize a method
as a test, the method name will need to start with ``test_`` or end with
``_test``. Let's go ahead and write a simple unit test for the factorial
function.

First Generation Unit Test
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. sourcecode:: python

    import unittest

    class TestFactorial(unittest.TestCase):
        """
        Contains unit tests for the factorial function
        """

        def test_n_less_than_0(self):
            """
            Tests that the factorial raises a ``ValueError`` if an attempt
            is made to calculate a factorial for ``n < 0``.
            """
            was_error_thrown = False

            try:
                _ = factorial(-1)
            except ValueError:
                was_error_thrown = True

            assert was_error_thrown

        def test_n_is_0(self):
            """
            Tests that the result of the factorial is ``1`` if ``n == 0``
            """
            assert factorial(0) == 1

        def test_n_greater_than_0(self):
            """
            Tests that the factorial is calculated correctly if ``n > 0``
            """
            assert factorial(3) == 6

Let's look at what this code does. In the first test, we are checking
whether calculating an invalid factorial raises :class:`ValueError`. In the
second test, we check whether the factorial of ``0`` is ``1``. In the next
test, we check whether the factorial of a number is equal to its factorial.
This style of testing is referred to as a first-generation test.

Note the use of the python convention of assigning a value to ``_`` to
indicate that the function returns a value, but that we're not interested in
what it returns.

There are several issues with us writing tests in this way. Firstly, testing
for exceptions is something that we will be doing all the time, and the
try-catch block doesn't really communicate what we are doing that well.
Secondly, Python's ``assert`` throws an :class:`AssertionError` without any
message in case the condition is false. That's great for telling us whether
a test failed, but it won't do us much good for telling us how the test
failed. It would be nice to prepare a report telling us why a test failed.
Fortunately, :mod:`unittest` can help us out with that.

Second Generation Unit Test
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to providing naming, :class:`unittest.TestCase` also provides
some interesting methods for assertions. These methods, like
:meth:`unittest.TestCase.assertTrue` and :meth:`unittest.TestCase.assertEqual`
do double duty of checking that the condition is true, and preparing a
report indicating why the test failed. The ``assert`` statements in our code
will be replaced with :meth:`unittest.TestCase.assertEqual` and
:meth:`unittest.TestCase.assertRaises`. Note the use of the context manager
`"with" syntax <https://goo.gl/H6DSWj>`_ to check whether an exception was
thrown in a code block.

.. sourcecode:: python

    import unittest

    class TestFactorial(unittest.TestCase):
        """
        Contains unit tests for the factorial function
        """

        def test_n_less_than_0(self):
            """
            Tests that the factorial raises a ``ValueError`` if an attempt
            is made to calculate a factorial for ``n < 0``.
            """
            with self.assertRaises(ValueError):
                _ = factorial(-1)

        def test_n_is_0(self):
            """
            Tests that the result of the factorial is ``1`` if ``n == 0``
            """
            self.assertEqual(factorial(0), 1)

        def test_n_greater_than_0(self):
            """
            Tests that the factorial is calculated correctly if ``n > 0``
            """
            self.assertEqual(factorial(3), 6)

This looks much better! However, we can still do better when it comes to
testing our function. We're testing the ``factorial`` function for the
values ``-1``, ``0``, and ``3``. This is good, but it's hardly
representative of the entire domain of natural numbers including 0. When we
wrote our ``factorial`` function, we did so with the intent that it would
work for all numbers, not just the three that we test with. We've done our
due diligence when it comes to code coverage; every line of code that we
defined in our source code is "hit" while testing. However, even with 100%
code coverage, there can still be bugs in the code caused by unforeseen
interactions between software components.

Let's solve this problem by writing more unit tests for the ``n > 0`` case

Parametrized Unit Tests
~~~~~~~~~~~~~~~~~~~~~~~

.. sourcecode:: python

    import unittest

    class TestFactorial(unittest.TestCase):
        """
        Contains unit tests for the factorial function
        """

        def test_n_less_than_0(self):
            """
            Tests that the factorial raises a ``ValueError`` if an attempt
            is made to calculate a factorial for ``n < 0``.
            """
            with self.assertRaises(ValueError):
                _ = factorial(-1)

        def test_n_is_0(self):
            """
            Tests that the result of the factorial is ``1`` if ``n == 0``
            """
            self.assertEqual(factorial(0), 1)

        def test_n_is_1(self):
            """
            Tests that the factorial is calculated correctly if ``n = 1``
            """
            self.assertEqual(factorial(1), 1)

        def test_n_is_2(self):
            """
            Tests that the factorial is calculated correctly if ``n = 2``
            """
            self.assertEqual(factorial(2), 2)

        def test_n_is_3(self):
            """
            Tests that the factorial is calculated correctly if ``n = 3``
            """
            self.assertEqual(factorial(3), 6)

Whew, my hands got tired just typing out all those cases! There's also a
whole bunch of repeated code in our tests. Let's write down a function to
run our tests, and run it with multiple parameters. We'll put all our tests
for ``n > 1`` into a parametrized unit test. This way, if we need to add
more cases for more ``n`` into the future, we can do it with a single entry
into a list.

.. sourcecode:: python

    import unittest

    class TestFactorial(unittest.TestCase):
        """
        Contains unit tests for the factorial function
        """
        test_data = [
            (0, 1),
            (1, 1),
            (2, 2),
            (3, 6),
            (4, 24),
            (5, 120)
        ]

        def test_n_less_than_0(self):
            """
            Tests that the factorial raises a ``ValueError`` if an attempt
            is made to calculate a factorial for ``n < 0``.
            """
            with self.assertRaises(ValueError):
                _ = factorial(-1)

        def test_n_is_0(self):
            """
            Tests that the result of the factorial is ``1`` if ``n == 0``
            """
            self.assertEqual(factorial(0), 1)

        def test_n_greater_than_0(self):
            """
            Tests that the factorial is calculated correctly if ``n > 1``
            """
            for parameter in self.test_data:
                self._assert_factorial_is_correct(parameter)

        def _assert_factorial_is_correct(self, parameter):
            """
            Asserts that the second element in a two-tuple is equal to the
            factorial of the first element
            """
            self.assertEqual(factorial(parameter[0]), parameter[1])

This is a very good test! But it still has some issues. The set
``{1, 2, 3, 4, 5}`` doesn't come any closer to representing the set
of all natural numbers any more than the set ``{1, 3}`` (darn countable
infinities). We haven't made any progress in testing our function. Secondly,
humans are actually pretty bad at generating test data. If we were asked to
generate strings instead of integers, the possibilities for random strings
increase exponentially as the length of the random strings increase. In
addition, think about how many characters there are in Unicode besides the
Western alphabet. It would be pretty embarrassing if a stray character
ruined our application.

.. note::

    This is exactly what happened to `Apple <https://goo.gl/6rq9ub>`_ in May
    2015. The `"effective power" <https://goo.gl/kb8B2s>`_ bug occurred due
    to the fact that when the iPhone tried to render a notification for a
    message containing certain Arabic characters at a certain place in the
    text, the message would end up being longer than the allowed area for
    rendering the shortened message. This is because Arabic can't be
    truncated like English, as the letters in Arabic script
    change `depending on their position <https://goo.gl/UWBUV3>`_.

Property-Driven Testing
~~~~~~~~~~~~~~~~~~~~~~~

