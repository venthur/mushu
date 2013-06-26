"""
This package contains the low-level drivers for various amplifiers.

As a user, you'll probably not deal with them directly but with their decorated
counterparts via :func:`libmushu.__init__.get_amp`.

If you want to use the low level drivers directly you can use it like this::

    from libmushu.driver.randomamp import RandomAmp
    amp = RandomAmp()

TODO: Add a 'writing your own drivers' section or tutorial.

"""
