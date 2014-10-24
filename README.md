Mushu
=====

[Mushu][mushu] is a free and open-source Brain Computer Interface (BCI) signal
acquisition software written in Python.

  [mushu]: http://bbci.de/mushu

Installation
------------


### Using PyPI

Mushu is available on the [Python Package Index (PyPI)][pypi] and can be easily
installed via:

```bash
$ pip install mushu
```

  [pypi]: https://pypi.python.org/pypi/Mushu


### Requirements

The required packages to run Mushu can be found in the file
[requirements.txt](requirements.txt). To install all required packages at once
one can use `pip`:

```sh
$ pip install -r requirements.txt
```

or simply install all packages line by line using the package manager of your
operating system.


### Manually Installing Mushu

To install Mushu manually on your system, download the latest version of Mushu
and run:

```sh
$ python ./setup.py install --user
```

Supported Amplifiers
--------------------

  * g.USBamp by g.tec (native)
  * EPOC by emotiv (native)
  * any [lab streaming layer][lsl] device publishing EEG data
  * Virtual Amplifier: ReplayAmp, an amplifier that replays EEG data in realtime
    or timelapse

  [lsl]: https://code.google.com/p/labstreaminglayer/

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


Citing Us
---------

If you use Mushu for anything that results in a publication, We humbly ask you
to cite us:

```bibtex
@INPROCEEDINGS{venthur2012,
    author={Venthur, Bastian and Blankertz, Benjamin},
    booktitle={Engineering in Medicine and Biology Society (EMBC), 2012 Annual International Conference of the IEEE},
    title={Mushu, a free- and open source BCI signal acquisition, written in Python},
    year={2012},
    month={Aug},
    pages={1786-1788},
    organization={IEEE},
    doi={10.1109/EMBC.2012.6346296},
    ISSN={1557-170X},
}
```

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

