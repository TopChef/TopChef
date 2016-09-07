# Contributing to TopChef 

## Bugs

If you found a bug in TopChef, please 
[open an issue](https://github.com/TopChef/TopChef/issues/new) on the
[GitHub repository](https://github.com/TopChef/TopChef). The issue template
form has a series of checkboxes and a place to put the description.


## Project Management

The entire project is managed through GitHub issues. If you have a feature
request, or want to ask about the system, please [open an issue](
https://github.com/TopChef/TopChef/issues/new) and we can discuss it

The [Waffle IO board](https://waffle.io/TopChef/TopChef) is used to manage
deadlines, as well as establish a cadence for our project team. In order to
make the most of its integrations with GitHub, we ask that contributors
adhere to a few rules

### Creating Branches
If you are creating a branch with the intent of fixing an issue, make sure
the name of the branch has the number of the issue to be fixed, preceded
by a ``#``. An example of a good branch name is ``ReadmeFix-#84``. The 
``#84`` does not need to be in any special place in the branch, as long
as it is in the branch name.

Upon pushing this branch to GitHub, you will be assigned to the branch,
and an ``in progress`` label will be added to the issue. Check the Waffle
IO board to view issue status.

We ask that you remain in touch with us during this period as you work
on your branch.

### Pull Requests

When you are done with your branch, please send us a PR. If you didn't
include the issue number in your branch name, please include it manually
in the PR title. An example of a good title for a PR is ``Fixes #85``. 
Waffle will then add an ``In Review`` label to the issue. 

The title of the PR must be ``Fixes #<number>`` where ``<number>`` is the 
number of the issue that the PR is fixing.

There is a Pull Request Form that will be displayed. If you are not referencing
any particular issue, please give us a description of what your code
changes are.

We use [Travis CI](https://travis-ci.org/TopChef/TopChef) to build and unit
test our code. In order for us to accept your pull requests, the tests in here must
pass.

