
class Amplifier(object):
    """Amplifier base class.

    The base class is very generic on purpose. Amplifiers from different
    vendors vary in so many ways that it is difficult to find a common set of
    methods that all support.

    In the spirit of "encapsulating what varies", I decided to encapsulate the
    configuration. So the main configuration of the amplifier, like setting the
    mode (e.g. data, impedance, etc.), sampling frequency, etc. happens in
    `configure` and is very specific for the amplifier at hand.

    `start`, `stop`, and `get_data` is very generic and must be supported by
    all derived amplifier classes.

    How an amplifier should be used:

        amp = Amp()
        # measure impedance
        amp.configure(config)
        channels = amp.get_channels()
        amp.start()
        while 1:
            data = amp.get_data()
            if enough:
                break
        amp.stop()
        # measure data
        amp.configure(config)
        channels = amp.get_channels()
        amp.start()
        while 1:
            data = amp.get_data()
            if enough:
                break
        amp.stop()

    """

    def configure(self, config):
        """Configure the amplifier.

        Use this method to set the mode (i.e. impedance, data, ...), sampling
        frequency, filter, etc.

        This depends strongly on the amplifier.
        """
        pass

    def configure_with_gui(self):
        """Configure the amplifier interactively.

        Use this method to spawn a GUI which allows for configuring the
        amplifier.
        """
        pass

    def start(self):
        """Make the amplifier ready for delivering data."""
        pass

    def stop(self):
        """Stop the amplifier."""
        pass

    def get_data(self):
        """Get data.

        This method is called as fast as possible.
        """
        pass

    def get_channels(self):
        """Return the list of channelnames.

        The list has the same order as the data, i.e. the second name in the
        list represents the second colum of the data returned by `get_data`.
        """
        pass

    @staticmethod
    def is_available():
        """Is the amplifier connected to the computer?

        This method should be overwritten by derived classes and return True if
        the amplifier is connected to the computer or False if not.
        """
        raise NotImplementedError


