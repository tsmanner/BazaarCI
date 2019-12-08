from bazaarci.runner import Step
from bazaarci.runner.step import skip_if_redundant, wait_for_producers


class Remote:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, step: Step):
        """ Remote subclasses are constructed with the necessary
            information to do setup and teardown for the remote host.
            Calling a Remote instance on a step adds the setup
            and teardown routines to it's run behavior.
        """
        raise NotImplementedError(
            "Class `{}` has not implemented a `__call__` method!".format(self.__class__.__name__)
        )
