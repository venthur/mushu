
class Amplifier(object):

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

