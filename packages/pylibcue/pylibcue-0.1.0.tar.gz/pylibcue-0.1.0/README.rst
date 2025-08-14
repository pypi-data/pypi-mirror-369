pylibcue
========

.. image:: https://img.shields.io/badge/libcue-v2.3.0-blue
   :target: https://github.com/lipnitsk/libcue/tree/v2.3.0
   :alt: libcue version


Python wrapper for `libcue <https://github.com/lipnitsk/libcue>`_ CUE sheet parser library.

Usage
-----

Create a CD instance from CUE sheet file or string:

.. code-block:: python

    from pylibcue import Cd

    cd = Cd.from_path("./example.cue")
    # cd = Cd.from_file(open("./example.cue", 'r'))
    # cd = Cd.from_str("...")

Extract CD metadata and tracks:

.. code-block:: python

    cdtext = cd.cdtext
    rem = cd.rem
    print("Title:", cdtext.title)
    print("Artist:", cdtext.performer)
    print("Date:", rem.date)
    print("Tracks:")

    for track in cd:
        print(f"\t{track.start} - {track.cdtext.title}")

License
-------

pylibcue is licensed under the GNU General Public License v2.0.
