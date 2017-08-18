Intro to Relational Databases
=============================

TopChef relies on a relational database for long-term storage. Relational
databases implement a
`relational algebra <https://en.wikipedia.org/wiki/Relational_algebra>`_ for
storing and querying data from the database. The most common abstraction for
considering relational storage systems is that of cross-indexed tables. Each
table has a set of columns associated with it. Each column in a table holds
a variable of a given type. For instance, the table

+----------------------+
| Students             |
+============+=========+
| first_name | String  |
+------------+---------+
| last_name  | String  |
+------------+---------+
| student_id | Integer |
+------------+---------+

Is a table with the name ``Student``, and three columns, that represent
``First Name``, ``Last Name``, and ``Student ID``.
The databases that TopChef uses allow users to manipulate them through a
domain-specific programming language called Structured Query Language, or
SQL. There is an ANSI standard for SQL, but different database products will
have different features, resulting in many different SQL "dialects". This is
one of the reasons why this project uses SQLAlchemy.

In order to create the table above, we would send the query

.. sourcecode:: sql

    CREATE TABLE Students (
        STRING first_name,
        STRING last_name,
        INTEGER student_id
    );

and in order to fill the table up, we may use an ``INSERT`` query like

.. sourcecode:: sql

    INSERT INTO Students ("First Name", "Last Name", "Student ID") VALUES
        ("Woll", "Smoth", "123456");

The table will now look something like

+------------+-----------+------------+
| first_name | last_name | student_id |
+============+===========+============+
| Woll       | Smoth     | 123456     |
+------------+-----------+------------+

Each row of data in this table is called a record.

Unfortunately, we've made a mistake entering our data. The student written
as ``Woll Smoth`` is really named ``Will Smith``. Fortunately, SQL allows us
to change database records using ``UPDATE`` queries. The ``UPDATE`` query
that will fix this problem is

.. sourcecode:: sql

    UPDATE students SET first_name = "Will", last_name = "Smith"
    WHERE student_id = 123456;

The table will now look like

+------------+-----------+------------+
| first_name | last_name | student_id |
+============+===========+============+
| Will       | Smith     | 123456     |
+------------+-----------+------------+

We can then retrieve this data at any time using a ``SELECT`` query, like

.. sourcecode:: sql

    SELECT * FROM Students WHERE student_id = 123456;

The use of the ``*`` is a wildcard character standing in for all columns.

Great! We've built out our first table, but it doesn't really tell us much.
Let's say we need to record what residence Will Smith lives in. We can do
this by introducing another column with the name of the residence. The query
to do this is an ``ALTER TABLE`` query, and it would look something like

.. sourcecode:: sql

    ALTER TABLE Students ADD "Residence Name" STRING;

This approach will eventually get cumbersome, as the same information will
get repeated over and over again. This will be a drag on storage space, but
it will also be bad for the consistency of the database. If something about
the database were to change, we would have to change it for EVERY student in
that table. We would also have to know all the information for the residence
when creating new students, which would be quite wasteful.

Lastly, this represents a design problem, as the data between students and
residences is obviously related, but we haven't communicated that relation
in any way. To solve this, we create a second table in our database as follows

+------------------------+
| Residences             |
+==============+=========+
| residence_id | Integer |
+--------------+---------+
| name         | String  |
+--------------+---------+
| address      | String  |
+--------------+---------+

And we alter our "Students" table to be the following

+------------------------+
| Students               |
+==============+=========+
| first_name   | String  |
+--------------+---------+
| last_name    | String  |
+--------------+---------+
| student_id   | Integer |
+--------------+---------+
| residence_id | Integer |
+--------------+---------+

Since the student and residence records share a record, we say that these
tables are related. This is a way of writing down a one-to-many relation
between residences and students, where one residence can have many students.

Now, let's say we want to select all the students that live in a particular
residence. This is where the relational algebra defines an operation called
a ``JOIN``. There are several types of joins, but in our case, we will want
to take an ``INNER JOIN``. ``JOIN``s must be defined on some logical
condition.

In order to select all the students that live in a residence "REV", we could
send a query like

.. sourcecode:: sql

    SELECT * FROM Students INNER JOIN Residences ON
        Students.residence_id = Residences.residence_id
        WHERE Residences.name = "REV";

Note the use of the member access operator ``.`` in order to differentiate
between columns that have the same name in different tables.

It would be useful at this point to introduce the concept of primary keys. A
primary key for a database record is the minimum amount of data to uniquely
identify a record in our database. In this case, it would be useful to
define the ``student_id`` as the primary key in our ``Students`` table, and
the ``residence_id`` as the primary key of the ``Residences`` table. We
could also define a "composite key" as a primary key that spans multiple
columns. The entry in each column of the composite key doesn't have to be
unique, but the combination would have to be unique. It may be tempting to
define ``first_name`` and ``last_name`` as the composite key of the
``Students`` table, but we would run into some problems if a second Will
Smith decided to enroll in our school.

The uniqueness of primary keys allows us to define foreign keys as well. In
the case of the ``residence_id`` column in the ``Students`` table, we can
define this column as a foreign key using the query

.. sourcecode:: sql

    ALTER TABLE Students
        ADD FOREIGN KEY (residence_id) REFERENCES Residences.residence_id

In a ``CREATE TABLE`` query, this would be

.. sourcecode:: sql

    CREATE TABLE Students (
        STRING first_name,
        STRING last_name,
        INTEGER student_id,
        INTEGER residence_id,
        FOREIGN KEY (residence_id) REFERENCES Residences.residence_id
    );

Composite keys come in handy when expressing many-to-many relations. In the
case of many-to-many relations, we use a design pattern called an
association table. Let's say we had some classes in our school as well. In
that case, the classes may look something like the table below. Primary keys
are identified using **bolded text**.

+------------------------+
| Classes                |
+==============+=========+
| **class_id** | Integer |
+--------------+---------+
| name         | String  |
+--------------+---------+

The association table will look like

+--------------------------+
| Classes To Students      |
+================+=========+
| **class_id**   | Integer |
+----------------+---------+
| **student_id** | Integer |
+----------------+---------+

We can use the same ``JOIN`` syntax discussed above, but we will now need to
make two ``JOIN`` opreations, one to ``JOIN`` our ``Students`` table to the
``Classes To Students`` association table, and one to join the result of the
previous join to the ``Classes`` table. This process of removing repeated
data is called normalization, and it's a major part of database design.

Extra References
----------------

`W3Schools <https://www.w3schools.com/sql/>`_ has an excellent SQL tutorial.
The `Flask Mega-Tutorial <https://goo.gl/vrTtDt>`_ also database design in
some detail, applying it to the design of a small blogging application.
