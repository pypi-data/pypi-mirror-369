pylibcue
========

pylibcue is a CUE sheet parser library for python. It provides fast and
reliable CUE sheets parsing interfaces for python by wrapping `libcue
<https://github.com/lipnitsk/libcue>`_ C library with Cython.

Install
-------

.. code-block:: bash

    pip install pylibcue

Compile from source
^^^^^^^^^^^^^^^^^^^

Requirements: bison, flex, make.

.. code-block:: bash

    pip install --upgrade build
    make wheel

Usage
-----

Create a CD instance by parsing a CUE sheet file or string:

.. code-block:: python

    import pylibcue

    cd = pylibcue.parse_file("./example.cue")
    # cd = pylibcue.parse_str("...")

Extract CD metadata and iterate through tracks in CD:

.. code-block:: python

    print("Title:", cd.cdtext.title)
    print("Artist:", cd.cdtext.performer)
    print("Date:", cd.rem.date)
    print("Tracks:")

    for tr in cd:
        print(f"{tr.start} - {tr.cdtext.title} - {tr.cdtext.performer}")

License
-------

pylibcue is licensed under the GNU General Public License v2.0.
