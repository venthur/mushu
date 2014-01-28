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

Next, install mushu
```sh
sudo python ./setup.py install
```
Supported Amplifiers
--------------------

  * g.USBamp by g.tec
  * EPOC by emotiv

Online Documentation
--------------------

Online documentation is available [here][mushudoc].

  [mushudoc]: http://venthur.github.io/mushu

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

Related Software
----------------

For a complete BCI system written in Python use Mushu together with
[Wyrm][wyrm] and [Pyff][pyff]. Wyrm is a Brain Computer Interface (BCI) toolbox
written in Python and is suitable for running on-line BCI experiments as well as
off-line analysis of EEG data. Pyff a BCI feedback and -stimulus framework.

  [pyff]: http://github.com/venthur/pyff
  [wyrm]: http://github.com/venthur/wyrm



Author
------

  * [Bastian Venthur][venthur]


  [venthur]: http://venthur.de

