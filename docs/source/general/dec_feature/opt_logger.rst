opt_logger
==========

``opt_logger`` option requires a logger. When a logger is passed in then the decorator will
log to the logger when validation fails.

.. note::

    When :doc:`opt_return` option is set and/or :doc:`raise_error` is ``False`` then logging
    will **not** take place as no validation error are raised.

Example logger and function with a decorator that uses logger.

.. code-block:: python

    import logging
    from pathlib import Path
    from kwhelp.decorator import RuleCheckAll
    from kwhelp.rules import RuleIntPositive

    def _create_logger(level:int, log_path: Path) -> logging.Logger:
        """
        Creates a logging object and returns it
        """
        logger = logging.getLogger("default_logger")
        logger.setLevel(level)
        # create the logging file handler
        fh = logging.FileHandler(str(log_path))

        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)

        # add handler to logger object
        logger.addHandler(fh)
        return logger

    default_logger = _create_logger(level=logging.DEBUG ,log_path=(Path.home() / 'mylog.log'))

    @RuleCheckAll(RuleIntPositive, opt_logger=default_logger)
    def add_positives(*args) -> int:
        return sum(args)


Call sample function.

.. code-block:: python

    >>> try:
    >>>     result = add_positives(1, 33, -3)
    >>>     print(result)
    >>> except Exception as e:
    >>>     print(e)
    RuleError: 'add_positives' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    RuleCheckAll decorator error.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value



.. code-block::
    :caption: Log file contents

    2021-11-18 07:58:17,995 - default_logger - ERROR - RuleError: 'add_positives' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    RuleCheckAll decorator error.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value
    Traceback (most recent call last):
    File "/home/paul/Documents/Projects/Python/Publish/kwargs/kwhelp/checks/__init__.py", line 237, in _validate_rules_all
        result = result & rule_instance.validate()
    File "/home/paul/Documents/Projects/Python/Publish/kwargs/kwhelp/rules/__init__.py", line 347, in validate
        raise ValueError(
    ValueError: Arg error: 'arg' must be a positive int value

    The above exception was the direct cause of the following exception:

    Traceback (most recent call last):
    File "/home/paul/Documents/Projects/Python/Publish/kwargs/kwhelp/decorator/__init__.py", line 1648, in wrapper
        is_valid = self._rulechecker.validate_all(**arg_name_values)
    File "/home/paul/Documents/Projects/Python/Publish/kwargs/kwhelp/checks/__init__.py", line 311, in validate_all
        result = result & self._validate_rules_all(key=k, field=k, value=v)
    File "/home/paul/Documents/Projects/Python/Publish/kwargs/kwhelp/checks/__init__.py", line 240, in _validate_rules_all
        raise RuleError(
    kwhelp.exceptions.RuleError: RuleError:
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value