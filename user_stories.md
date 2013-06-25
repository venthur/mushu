User Stories
============

Alice the researcher.
---------------------

Alice wants to use the signal acquisition mainly in a non-interactive way in
Python scripts. She will decide per project what kind of amplifier she needs
and stick with that throughout the experiment.

    >>> amp = SomeAmp()
    >>> amp.configure(configure_string)
    >>> amp.start()
    >>> while 1:
    >>>     data = amp.get_data()
    >>>     # so something with the data
    >>> amp.stop()

It is very important that the data is recorded to a file to allow for later
off-line analysis.

Some amplifiers will support their own trigger input others don't. Triggers
are always required for Alice.

