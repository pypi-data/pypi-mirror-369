"""Some bespoke exceptions that can be used in control sequences.

Over builtins, these provide more information to the user. I (Conrad) prefer to use warnings for
the latter purpose, but there are reasons to throw these errors in a variety of circumstances.
"""


class AnalysisError(Exception):
    """Base class to indicate that something scientific went wrong.

    Example:
        A bad fit from scipy.optimize in an internal function or analysis
        routine that could not be handled by the user.
    """
