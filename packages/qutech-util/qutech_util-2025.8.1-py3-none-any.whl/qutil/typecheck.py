"""Functions and decorators to  help with runtime typechecking. Notably the `@check_literals` decorator to ensure that
arguments match an annotated literal. Wildcard imports the `typeguard` which provides the powerful `@typechecked`
decorator.
"""

import functools
import inspect
import typing

import typeguard
from typeguard import *

__all__ = [x for x in typeguard.__dict__ if not x.startswith('_')] + ["check_literals"]


def _get_annotated_literals(signature: inspect.Signature) -> typing.Mapping[str, tuple]:
    literals = {}
    for name, parameter in signature.parameters.items():
        annotation = parameter.annotation
        additional_values = ()

        # check for Optional[Literal[...]]
        if typing.get_origin(annotation) == typing.Union:
            union_types = typing.get_args(annotation)
            if len(union_types) == 2 and type(None) in union_types:
                annotation, = set(union_types) - {type(None)}
                additional_values = (None,)

        if typing.get_origin(annotation) == typing.Literal:
            literals[name] = typing.get_args(annotation) + additional_values
    return literals


def check_literals(function: callable) -> callable:
    """A decorator that checks if arguments are valid for all typing.Literal annotated function arguments.

    This decorator handles Literal[...] and Optional[Literal[...]].

    Examples
    --------
    >>> from typing import Literal, Sequence
    >>> @check_literals
    ... def my_function(a: Sequence[int], b: Literal['forward', 'backward']):
    ...     if b == 'backward':
    ...         return list(reversed(a))
    ...     else:
    ...         # b is guaranteed to be 'forward' here
    ...         return list(a)

    works

    >>> my_function([1, 2, 3], 'backward')
    [3, 2, 1]

    works because the first arguement is not checked at runtime

    >>> my_function({'no': 'sequence', 'yes': 'mapping'}, 'backward')
    ['yes', 'no']

    Here we get a runtime error because of typo in 'backward'

    >>> my_function('wrong', 'backwardd')
    Traceback (most recent call last):
    ...
    ValueError: The argument b of ...typecheck.my_function has to be in ('forward', 'backward') but was 'backwardd'.

    This decorator has an overhead per function call of several microseconds (~10µs) and roughly one order of
    magnitude less than ``typeguard.typechecked``.

    If you need runtime-typechecking for all arguments use the typeguard functions that are exposed in this module for
    your convenience.
    """

    signature = inspect.signature(function)
    parameters = signature.parameters
    literals = _get_annotated_literals(signature)
    var_positional_name = next((name
                                for name, param in parameters.items()
                                if param.kind == inspect.Parameter.VAR_POSITIONAL),
                               None)
    var_keyword_name = next((name
                             for name, param in parameters.items()
                             if param.kind == inspect.Parameter.VAR_KEYWORD),
                            None)

    function_name = f'{inspect.getmodule(function).__name__}.{function.__name__}'

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        for arg_name, arg in bound.arguments.items():
            values = literals.get(arg_name, None)
            if values is not None:
                if arg_name == var_positional_name:
                    for idx, value in enumerate(arg):
                        if value not in values:
                            raise ValueError(f"The positional argument {arg_name}[{idx}] of {function_name} has "
                                             f"to be in {values!r} but was {value!r}.")
                elif arg_name == var_keyword_name:
                    for key, value in arg.items():
                        if value not in values:
                            raise ValueError(f"The keyword argument {arg_name}[{key!r}] of {function_name} has "
                                             f"to be in {values!r} but was {value!r}.")
                elif arg not in values:
                    raise ValueError(f"The argument {arg_name} of {function_name} has "
                                     f"to be in {values!r} but was {arg!r}.")

        return function(*args, **kwargs)
    return wrapper
