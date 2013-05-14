Mushu
=====

[Mushu][mushu] is a free and open-source Brain Computer Interface (BCI) signal
acquisition software written in Python.

  [mushu]: http://bbci.de/mushu

Installation
------------

The required packages to run Mushu can be found in the file
[requirements.txt](requirements.txt). To install all required packages at once
one can use `pip`:

```sh
pip install -r requirements.txt
```

or simply install all packages line by line using the package manager of your
operating system.

Supported Amplifiers
--------------------

  * g.USBamp by g.tec
  * EPOC by emotiv

Motivation
----------

  * Platform Independent
  * Amplifier Independent
    * Single interface regardless of the underlying Amplifier type used
  * Free Software
  * Next step towards a whole BCI system based on Python (as opposed to C++ or
    Matlab)

Use Cases
---------

  * Directly as Python library
  * As Network server


Output Format
-------------

  * Numpy arrays
  * TOBI Interface A


Author
------

  * [Bastian Venthur][venthur]


  [venthur]: http://venthur.de

