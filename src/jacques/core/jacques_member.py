class JacquesMember:  # pylint: disable=too-few-public-methods # it's a meta class
    """Meta class for all classes that need to access Jacques instance.

    :param jacques: Jacques instance to access."""

    def __init__(self, jacques) -> None:
        self.jacques = jacques
