natsort
=======

.. image:: https://img.shields.io/pypi/v/natsort.svg
    :target: https://pypi.org/project/natsort/

.. image:: https://img.shields.io/pypi/pyversions/natsort.svg
    :target: https://pypi.org/project/natsort/

.. image:: https://img.shields.io/pypi/l/natsort.svg
    :target: https://github.com/SethMMorton/natsort/blob/main/LICENSE

.. image:: https://github.com/SethMMorton/natsort/workflows/Tests/badge.svg
    :target: https://github.com/SethMMorton/natsort/actions

.. image:: https://codecov.io/gh/SethMMorton/natsort/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/SethMMorton/natsort

.. image:: https://img.shields.io/pypi/dw/natsort.svg
    :target: https://pypi.org/project/natsort/

Simple yet flexible natural sorting in Python.

    - Source Code: https://github.com/SethMMorton/natsort
    - Downloads: https://pypi.org/project/natsort/
    - Documentation: https://natsort.readthedocs.io/

      - `Examples and Recipes`_
      - `How Does Natsort Work?`_
      - `API`_

    - `Quick Description`_
    - `Quick Examples`_
    - `FAQ`_
    - `Requirements`_
    - `Optional Dependencies`_
    - `Installation`_
    - `How to Run Tests`_
    - `How to Build Documentation`_
    - `Dropped Deprecated APIs`_
    - `History`_

**NOTE**: Please see the `Dropped Deprecated APIs`_ section for changes.

Quick Description
-----------------

When you try to sort a list of strings that contain numbers, the normal python
sort algorithm sorts lexicographically, so you might not get the results that
you expect:

.. code-block:: pycon

    >>> a = ['2 ft 7 in', '1 ft 5 in', '10 ft 2 in', '2 ft 11 in', '7 ft 6 in']
    >>> sorted(a)
    ['1 ft 5 in', '10 ft 2 in', '2 ft 11 in', '2 ft 7 in', '7 ft 6 in']

Notice that it has the order ('1', '10', '2') - this is because the list is
being sorted in lexicographical order, which sorts numbers like you would
letters (i.e. 'b', 'ba', 'c').

`natsort`_ provides a function `natsorted()`_ that helps sort lists
"naturally" ("naturally" is rather ill-defined, but in general it means
sorting based on meaning and not computer code point).
Using `natsorted()`_ is simple:

.. code-block:: pycon

    >>> from natsort import natsorted
    >>> a = ['2 ft 7 in', '1 ft 5 in', '10 ft 2 in', '2 ft 11 in', '7 ft 6 in']
    >>> natsorted(a)
    ['1 ft 5 in', '2 ft 7 in', '2 ft 11 in', '7 ft 6 in', '10 ft 2 in']

`natsorted()`_ identifies numbers anywhere in a string and sorts them
naturally. Below are some other things you can do with `natsort`_
(also see the `Examples and Recipes`_ for a quick start guide, or the
`API`_ for complete details).

**Note**: `natsorted()`_ is designed to be a drop-in replacement for the
built-in `sorted()`_ function. Like `sorted()`_, `natsorted()`_
`does not sort in-place`. To sort a list and assign the output to the same
variable, you must explicitly assign the output to a variable:

.. code-block:: pycon

    >>> a = ['2 ft 7 in', '1 ft 5 in', '10 ft 2 in', '2 ft 11 in', '7 ft 6 in']
    >>> natsorted(a)
    ['1 ft 5 in', '2 ft 7 in', '2 ft 11 in', '7 ft 6 in', '10 ft 2 in']
    >>> print(a)  # 'a' was not sorted; "natsorted" simply returned a sorted list
    ['2 ft 7 in', '1 ft 5 in', '10 ft 2 in', '2 ft 11 in', '7 ft 6 in']
    >>> a = natsorted(a)  # Now 'a' will be sorted because the sorted list was assigned to 'a'
    >>> print(a)
    ['1 ft 5 in', '2 ft 7 in', '2 ft 11 in', '7 ft 6 in', '10 ft 2 in']

Please see `Generating a Reusable Sorting Key and Sorting In-Place`_ for
an alternate way to sort in-place naturally.

Quick Examples
--------------

- `Sorting Versions`_
- `Sort Paths Like My File Browser (e.g. Windows Explorer on Windows)`_
- `Sorting by Real Numbers (i.e. Signed Floats)`_
- `Locale-Aware Sorting (or "Human Sorting")`_
- `Further Customizing Natsort`_
- `Sorting Mixed Types`_
- `Handling Bytes`_
- `Generating a Reusable Sorting Key and Sorting In-Place`_
- `Other Useful Things`_

Sorting Versions
++++++++++++++++

`natsort`_ does not actually *comprehend* version numbers.
It just so happens that the most common versioning schemes are designed to
work with standard natural sorting techniques; these schemes include
``MAJOR.MINOR``, ``MAJOR.MINOR.PATCH``, ``YEAR.MONTH.DAY``. If your data
conforms to a scheme like this, then it will work out-of-the-box with
`natsorted()`_ (as of `natsort`_ version >= 4.0.0):

.. code-block:: pycon

    >>> a = ['version-1.9', 'version-2.0', 'version-1.11', 'version-1.10']
    >>> natsorted(a)
    ['version-1.9', 'version-1.10', 'version-1.11', 'version-2.0']

If you need to versions that use a more complicated scheme, please see
`these version sorting examples`_.

Sort Paths Like My File Browser (e.g. Windows Explorer on Windows)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Prior to `natsort`_ version 7.1.0, it was a common request to be able to
sort paths like Windows Explorer. As of `natsort`_ 7.1.0, the function
`os_sorted()`_ has been added to provide users the ability to sort
in the order that their file browser might sort (e.g Windows Explorer on
Windows, Finder on MacOS, Dolphin/Nautilus/Thunar/etc. on Linux).

.. code-block:: python

    import os
    from natsort import os_sorted
    print(os_sorted(os.listdir()))
    # The directory sorted like your file browser might show

Output will be different depending on the operating system you are on.

For users **not** on Windows (e.g. MacOS/Linux) it is **strongly** recommended
to also install `PyICU`_, which will help
`natsort`_ give results that match most file browsers. If this is not installed,
it will fall back on Python's built-in `locale`_ module and will give good
results for most input, but will give poor results for special characters.

Sorting by Real Numbers (i.e. Signed Floats)
++++++++++++++++++++++++++++++++++++++++++++

This is useful in scientific data analysis (and was the default behavior
of `natsorted()`_ for `natsort`_ version < 4.0.0). Use the `realsorted()`_
function:

.. code-block:: pycon

    >>> from natsort import realsorted, ns
    >>> # Note that when interpreting as signed floats, the below numbers are
    >>> #            +5.10,                -3.00,            +5.30,              +2.00
    >>> a = ['position5.10.data', 'position-3.data', 'position5.3.data', 'position2.data']
    >>> natsorted(a)
    ['position2.data', 'position5.3.data', 'position5.10.data', 'position-3.data']
    >>> natsorted(a, alg=ns.REAL)
    ['position-3.data', 'position2.data', 'position5.10.data', 'position5.3.data']
    >>> realsorted(a)  # shortcut for natsorted with alg=ns.REAL
    ['position-3.data', 'position2.data', 'position5.10.data', 'position5.3.data']

Locale-Aware Sorting (or "Human Sorting")
+++++++++++++++++++++++++++++++++++++++++

This is where the non-numeric characters are also ordered based on their
meaning, not on their ordinal value, and a locale-dependent thousands
separator and decimal separator is accounted for in the number.
This can be achieved with the `humansorted()`_ function:

.. code-block:: pycon

    >>> a = ['Apple', 'apple15', 'Banana', 'apple14,689', 'banana']
    >>> natsorted(a)
    ['Apple', 'Banana', 'apple14,689', 'apple15', 'banana']
    >>> import locale
    >>> locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    'en_US.UTF-8'
    >>> natsorted(a, alg=ns.LOCALE)
    ['apple15', 'apple14,689', 'Apple', 'banana', 'Banana']
    >>> from natsort import humansorted
    >>> humansorted(a)  # shortcut for natsorted with alg=ns.LOCALE
    ['apple15', 'apple14,689', 'Apple', 'banana', 'Banana']

You may find you need to explicitly set the locale to get this to work
(as shown in the example). Please see `locale issues`_ and the
`Optional Dependencies`_ section below before using the `humansorted()`_ function.

Further Customizing Natsort
+++++++++++++++++++++++++++

If you need to combine multiple algorithm modifiers (such as ``ns.REAL``,
``ns.LOCALE``, and ``ns.IGNORECASE``), you can combine the options using the
bitwise OR operator (``|``). For example,

.. code-block:: pycon

    >>> a = ['Apple', 'apple15', 'Banana', 'apple14,689', 'banana']
    >>> natsorted(a, alg=ns.REAL | ns.LOCALE | ns.IGNORECASE)
    ['Apple', 'apple15', 'apple14,689', 'Banana', 'banana']
    >>> # The ns enum provides long and short forms for each option.
    >>> ns.LOCALE == ns.L
    True
    >>> # You can also customize the convenience functions, too.
    >>> natsorted(a, alg=ns.REAL | ns.LOCALE | ns.IGNORECASE) == realsorted(a, alg=ns.L | ns.IC)
    True
    >>> natsorted(a, alg=ns.REAL | ns.LOCALE | ns.IGNORECASE) == humansorted(a, alg=ns.R | ns.IC)
    True

All of the available customizations can be found in the documentation for
`the ns enum`_.

You can also add your own custom transformation functions with the ``key``
argument. These can be used with ``alg`` if you wish.

.. code-block:: pycon

    >>> a = ['apple2.50', '2.3apple']
    >>> natsorted(a, key=lambda x: x.replace('apple', ''), alg=ns.REAL)
    ['2.3apple', 'apple2.50']

Sorting Mixed Types
+++++++++++++++++++

You can mix and match `int`_, `float`_, and `str`_ types when you sort:

.. code-block:: pycon

    >>> a = ['4.5', 6, 2.0, '5', 'a']
    >>> natsorted(a)
    [2.0, '4.5', '5', 6, 'a']
    >>> # sorted(a) would raise an "unorderable types" TypeError

Handling Bytes
++++++++++++++

`natsort`_ does not officially support the `bytes`_ type, but
convenience functions are provided that help you decode to `str`_ first:

.. code-block:: pycon

    >>> from natsort import as_utf8
    >>> a = [b'a', 14.0, 'b']
    >>> # natsorted(a) would raise a TypeError (bytes() < str())
    >>> natsorted(a, key=as_utf8) == [14.0, b'a', 'b']
    True
    >>> a = [b'a56', b'a5', b'a6', b'a40']
    >>> # natsorted(a) would return the same results as sorted(a)
    >>> natsorted(a, key=as_utf8) == [b'a5', b'a6', b'a40', b'a56']
    True

Generating a Reusable Sorting Key and Sorting In-Place
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Under the hood, `natsorted()`_ works by generating a custom sorting
key using `natsort_keygen()`_ and then passes that to the built-in
`sorted()`_. You can use the `natsort_keygen()`_ function yourself to
generate a custom sorting key to sort in-place using the `list.sort()`_
method.

.. code-block:: pycon

    >>> from natsort import natsort_keygen
    >>> natsort_key = natsort_keygen()
    >>> a = ['2 ft 7 in', '1 ft 5 in', '10 ft 2 in', '2 ft 11 in', '7 ft 6 in']
    >>> natsorted(a) == sorted(a, key=natsort_key)
    True
    >>> a.sort(key=natsort_key)
    >>> a
    ['1 ft 5 in', '2 ft 7 in', '2 ft 11 in', '7 ft 6 in', '10 ft 2 in']

All of the algorithm customizations mentioned in the
`Further Customizing Natsort`_ section can also be applied to
`natsort_keygen()`_ through the *alg* keyword option.

Other Useful Things
+++++++++++++++++++

 - recursively descend into lists of lists
 - automatic unicode normalization of input data
 - `controlling the case-sensitivity`_
 - `sorting file paths correctly`_
 - `allow custom sorting keys`_
 - `accounting for units`_

FAQ
---

How do I debug `natsorted()`_?
    The best way to debug `natsorted()`_ is to generate a key using `natsort_keygen()`_
    with the same options being passed to `natsorted()`_. One can take a look at
    exactly what is being done with their input using this key - it is highly
    recommended to `look at this issue describing how to debug`_ for *how* to debug,
    and also to review the `How Does Natsort Work?`_ page for *why* `natsort`_ is
    doing that to your data.

    If you are trying to sort custom classes and running into trouble, please
    take a look at https://github.com/SethMMorton/natsort/issues/60. In short,
    custom classes are not likely to be sorted correctly if one relies
    on the behavior of ``__lt__`` and the other rich comparison operators in
    their custom class - it is better to use a ``key`` function with
    `natsort`_, or use the `natsort`_ key as part of your rich comparison
    operator definition.

`natsort`_ gave me results I didn't expect, and it's a terrible library!
    Did you try to debug using the above advice? If so, and you still cannot figure out
    the error, then please `file an issue`_.

How *does* `natsort`_ work?
    If you don't want to read `How Does Natsort Work?`_,
    here is a quick primer.

    `natsort`_ provides a `key function`_ that can be passed to `list.sort()`_
    or `sorted()`_ in order to modify the default sorting behavior. This key
    is generated on-demand with the key generator `natsort_keygen()`_.
    `natsorted()`_ is essentially a wrapper for the following code:

    .. code-block:: pycon

        >>> from natsort import natsort_keygen
        >>> natsort_key = natsort_keygen()
        >>> sorted(['1', '10', '2'], key=natsort_key)
        ['1', '2', '10']

    Users can further customize `natsort`_ sorting behavior with the ``key``
    and/or ``alg`` options (see details in the `Further Customizing Natsort`_
    section).

    The key generated by `natsort_keygen()`_ *always* returns a `tuple`_. It
    does so in the following way (*some details omitted for clarity*):

      1. Assume the input is a string, and attempt to split it into numbers and
         non-numbers using regular expressions. Numbers are then converted into
         either `int`_ or `float`_.
      2. If the above fails because the input is not a string, assume the input
         is some other sequence (e.g. `list`_ or `tuple`_), and recursively
         apply the key to each element of the sequence.
      3. If the above fails because the input is not iterable, assume the input
         is an `int`_ or `float`_, and just return the input in a `tuple`_.

    Because a `tuple`_ is always returned, a `TypeError`_ should not be common
    unless one tries to do something odd like sort an `int`_ against a `list`_.

Shell script
------------

`natsort`_ comes with a shell script called `natsort`_, or can also be called
from the command line with ``python -m natsort``.  Check out the
`shell script wiki documentation`_ for more details.

Requirements
------------

`natsort`_ requires Python 3.9 or greater.

Optional Dependencies
---------------------

fastnumbers
+++++++++++

The most efficient sorting can occur if you install the
`fastnumbers`_ package
(version >=2.0.0); it helps with the string to number conversions.
`natsort`_ will still run (efficiently) without the package, but if you need
to squeeze out that extra juice it is recommended you include this as a
dependency. `natsort`_ will not require (or check) that
`fastnumbers`_ is installed at installation.

PyICU
+++++

It is recommended that you install `PyICU`_ if you wish to sort in a
locale-dependent manner, see this page on `locale issues`_ for an explanation why.

Installation
------------

Use ``pip``!

.. code-block:: console

    $ pip install natsort

If you want to install the `Optional Dependencies`_, you can use the
`"extras" notation`_ at installation time to install those dependencies as
well - use ``fast`` for `fastnumbers`_ and ``icu`` for `PyICU`_.

.. code-block:: console

    # Install both optional dependencies.
    $ pip install natsort[fast,icu]
    # Install just fastnumbers
    $ pip install natsort[fast]

How to Run Tests
----------------

Please note that `natsort`_ is NOT set-up to support ``python setup.py test``.

The recommended way to run tests is with `tox`_. After installing ``tox``,
running tests is as simple as executing the following in the `natsort`_ directory:

.. code-block:: console

    $ tox

``tox`` will create virtual a virtual environment for your tests and install
all the needed testing requirements for you.  You can specify a particular
python version with the ``-e`` flag, e.g. ``tox -e py36``. Static analysis
is done with ``tox -e flake8``. You can see all available testing environments
with ``tox --listenvs``.

How to Build Documentation
--------------------------

If you want to build the documentation for `natsort`_, it is recommended to
use ``tox``:

.. code-block:: console

    $ tox -e docs

This will place the documentation in ``build/sphinx/html``.

Dropped Deprecated APIs
-----------------------

In `natsort`_ version 6.0.0, the following APIs and functions were removed

 - ``number_type`` keyword argument (deprecated since 3.4.0)
 - ``signed`` keyword argument (deprecated since 3.4.0)
 - ``exp`` keyword argument (deprecated since 3.4.0)
 - ``as_path`` keyword argument (deprecated since 3.4.0)
 - ``py3_safe`` keyword argument (deprecated since 3.4.0)
 - ``ns.TYPESAFE`` (deprecated since version 5.0.0)
 - ``ns.DIGIT`` (deprecated since version 5.0.0)
 - ``ns.VERSION`` (deprecated since version 5.0.0)
 - ``versorted()`` (discouraged since version 4.0.0,
   officially deprecated since version 5.5.0)
 - ``index_versorted()`` (discouraged since version 4.0.0,
   officially deprecated since version 5.5.0)

In general, if you want to determine if you are using deprecated APIs you
can run your code with the following flag

.. code-block:: console

    $ python -Wdefault::DeprecationWarning my-code.py

By default `DeprecationWarnings`_ are not shown, but this will cause them
to be shown. Alternatively, you can just set the environment variable
``PYTHONWARNINGS`` to "default::DeprecationWarning" and then run your code.

Author
------

Seth M. Morton

History
-------

Please visit the changelog `on GitHub`_.

.. _natsort: https://natsort.readthedocs.io/en/stable/index.html
.. _natsorted(): https://natsort.readthedocs.io/en/stable/api.html#natsort.natsorted
.. _natsort_keygen(): https://natsort.readthedocs.io/en/stable/api.html#natsort.natsort_keygen
.. _realsorted(): https://natsort.readthedocs.io/en/stable/api.html#natsort.realsorted
.. _humansorted(): https://natsort.readthedocs.io/en/stable/api.html#natsort.humansorted
.. _os_sorted(): https://natsort.readthedocs.io/en/stable/api.html#natsort.os_sorted
.. _the ns enum: https://natsort.readthedocs.io/en/stable/api.html#natsort.ns
.. _fastnumbers: https://github.com/SethMMorton/fastnumbers
.. _sorted(): https://docs.python.org/3/library/functions.html#sorted
.. _list.sort(): https://docs.python.org/3/library/stdtypes.html#list.sort
.. _key function: https://docs.python.org/3/howto/sorting.html#key-functions
.. _locale: https://docs.python.org/3/library/locale.html
.. _int: https://docs.python.org/3/library/functions.html#int
.. _float: https://docs.python.org/3/library/functions.html#float
.. _str: https://docs.python.org/3/library/stdtypes.html#str
.. _bytes: https://docs.python.org/3/library/stdtypes.html#bytes
.. _list: https://docs.python.org/3/library/stdtypes.html#list
.. _tuple: https://docs.python.org/3/library/stdtypes.html#tuple
.. _TypeError: https://docs.python.org/3/library/exceptions.html#TypeError
.. _DeprecationWarnings: https://docs.python.org/3/library/exceptions.html#DeprecationWarning
.. _"extras" notation: https://packaging.python.org/tutorials/installing-packages/#installing-setuptools-extras
.. _PyICU: https://pypi.org/project/PyICU
.. _tox: https://tox.readthedocs.io/en/latest/
.. _Examples and Recipes: https://github.com/SethMMorton/natsort/wiki/Examples-and-Recipes
.. _How Does Natsort Work?: https://github.com/SethMMorton/natsort/wiki/How-Does-Natsort-Work%3F
.. _API: https://natsort.readthedocs.io/en/stable/api.html
.. _on GitHub: https://github.com/SethMMorton/natsort/blob/main/CHANGELOG.md
.. _file an issue: https://github.com/SethMMorton/natsort/issues/new
.. _look at this issue describing how to debug: https://github.com/SethMMorton/natsort/issues/13#issuecomment-50422375
.. _controlling the case-sensitivity: https://github.com/SethMMorton/natsort/wiki/Examples-and-Recipes#controlling-case-when-sorting
.. _sorting file paths correctly: https://github.com/SethMMorton/natsort/wiki/Examples-and-Recipes#sort-os-generated-paths
.. _allow custom sorting keys: https://github.com/SethMMorton/natsort/wiki/Examples-and-Recipes#using-a-custom-sorting-key
.. _accounting for units: https://github.com/SethMMorton/natsort/wiki/Examples-and-Recipes#accounting-for-units-when-sorting
.. _these version sorting examples: https://github.com/SethMMorton/natsort/wiki/Examples-and-Recipes#sorting-more-expressive-versioning-schemes
.. _locale issues: https://github.com/SethMMorton/natsort/wiki/Possible-Issues-with-natsort.humansorted-or-ns.LOCALE
.. _shell script wiki documentation: https://github.com/SethMMorton/natsort/wiki/Shell-Script
