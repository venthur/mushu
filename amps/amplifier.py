
class Amplifier(object):

    def configure(self, config):
        """Configure the amplifier.

        Use this method to set the mode (i.e. impedance, data, ...), sampling
        frequency, filter, etc.

        This depends strongly on the amplifier.
        """
        pass

    def start(self):
        """Initialize the amplifier and make it ready."""
        pass

    def stop(self):
        """Shut down the amplifier."""
        pass

    def get_data(self):
        """Get data."""
        pass


