
class Amplifier(object):
    """Amplifier base class.

    How an amplifier should be used:

        amp = Amp()
        # measure impedance
        amp.configure(config)
        amp.start()
        while 1:
            data = amp.get_data()
            if enough:
                break
        amp.stop()
        # measure data
        amp.configure(config)
        amp.start()
        while 1:
            data = amp.get_data()
            if enough:
                break
        amp.stop()

    or using the context manager:

        amp = Amp()
        # measure impedance
        amp.configure(config)
        with amp as a:
            while 1:
                data = a.get_data()
                if enough:
                    break
        # measure impedance
        amp.configure(config)
        with amp as a:
            while 1:
                data = a.get_data()
                if enough:
                    break

    """

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def configure(self, config):
        """Configure the amplifier.

        Use this method to set the mode (i.e. impedance, data, ...), sampling
        frequency, filter, etc.

        This depends strongly on the amplifier.
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

