.. Mushu documentation master file, created by
   sphinx-quickstart on Tue Jun 25 10:06:49 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Quickstart
==========

::

    import libmushu

    # look for amplifiers connected to the system, and return a list of the
    # respective classes
    available_amps = libmushu.get_available_amps()

    # select the first available amp and decorate it with tcp-marker- and
    # save-to-file-functionality
    ampname = available_amps[0]
    amp = libmushu.get_amp(ampname)

    # configure the amplifier
    amp.configure(cfg)

    # start it and collect data until finished
    amp.start()
    while 1:
        data, trigger = amp.get_data()

    # stop the amplifier
    amp.stop()


API Documentation
=================

.. autosummary::
   :toctree: api

   libmushu
   libmushu.ampdecorator
   libmushu.amplifier
   libmushu.driver


Welcome to Mushu's documentation!
=================================


Contents:

.. toctree::
   :maxdepth: 2

   user_stories

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

