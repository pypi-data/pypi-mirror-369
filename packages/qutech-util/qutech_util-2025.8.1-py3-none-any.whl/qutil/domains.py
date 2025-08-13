from __future__ import annotations

import abc
import numbers
from abc import ABC
from collections.abc import Container, Iterable
from dataclasses import InitVar, dataclass, field
from math import ceil, floor, inf, log, nan
from typing import Callable, Generic, Protocol, Set, TypeVar, Union, runtime_checkable

from numpy import iterable as is_iterable

from .functools import cached_property
from .itertools import next_closest, next_largest, next_smallest

_T = TypeVar("_T")
_RealT = TypeVar("_RealT", bound=numbers.Real)
_IntegralT = TypeVar("_IntegralT", bound=numbers.Integral)
_BoundT = Union[Callable[[], _RealT], _RealT]
_BoundT = Union[Iterable[_BoundT], _BoundT]


class Bound(Generic[_RealT]):
    """A lazily evaluated bound."""

    def __init__(self, default: _RealT, integral: bool):
        self.default = default
        self.integral = integral

    def __set_name__(self, owner, name):
        self._name = f'_{name}'

    def __get__(self, instance, owner=None) -> _RealT:
        if instance is None:
            return self.default

        value = getattr(instance, self._name, {self.default})
        evaluated = set()
        for item in value:
            if callable(item):
                evaluated.add(item())
            else:
                evaluated.add(item)

        if self._name.startswith('_lower'):
            lower = self.constrain_lower(evaluated)
            if self.integral:
                try:
                    return self.cast_lower(lower)
                except (OverflowError, ValueError):
                    # inf or nan
                    return lower
            return lower

        if self._name.startswith('_upper'):
            upper = self.constrain_upper(evaluated)
            if self.integral:
                try:
                    return self.cast_upper(upper)
                except (OverflowError, ValueError):
                    # inf or nan
                    return upper
            return upper

        raise NameError('Bound descriptor instance name should start with lower or upper')

    def __set__(self, instance, value: _BoundT):
        if value is self:
            value = self.default
        if not is_iterable(value):
            value = {value}
        else:
            value = set(value)
        setattr(instance, self._name, value)

    @staticmethod
    def constrain_upper(upper):
        return min(upper)

    @staticmethod
    def constrain_lower(lower):
        return max(lower)

    @staticmethod
    def cast_lower(lower):
        return ceil(lower)

    @staticmethod
    def cast_upper(upper):
        return floor(upper)


class ReciprocalBound(Bound[_RealT]):

    @staticmethod
    def constrain_upper(upper):
        return max(upper)

    @staticmethod
    def constrain_lower(lower):
        return max(lower)

    @staticmethod
    def cast_lower(lower):
        # 1/floor is less inclusive than 1/ceil
        return floor(lower)

    @staticmethod
    def cast_upper(upper):
        # 1/ceil is less inclusive than 1/floor
        return ceil(upper)


class Bounded(Protocol[_RealT]):
    """An object with bounds."""
    lower: Bound[_RealT]
    upper: Bound[_RealT]


@runtime_checkable
class Reciprocal(Protocol[_RealT]):
    """A reciprocal quantity that's specified by a numerator."""
    numerator: _RealT

    def _to_denominator(self, value: _RealT) -> _RealT:
        """Converts rationals in it to denominators given numerator."""
        return self.numerator / value


class Domain(Container[_RealT], Bounded[_RealT]):
    """A domain that constrains the allowed values a parameter can take.

    Supports the ``in``, ``<``, ``>``, ``&`` keyword and binary
    operators that reveal if a value is

    1. ``in`` : part of the domain
    2. ``<`` : outside of the domain and smaller than the lower bound
    3. ``>`` : outside of the domain and greater than the upper bound

    or return the

    4. ``&`` : intersection of the two domains.

    Examples
    --------
    >>> domain = ContinuousInterval(-2.3, 4.5)
    >>> domain
    ContinuousInterval(lower=-2.3, upper=4.5)
    >>> 1 in domain
    True
    >>> 7 in domain
    False
    >>> 7 > domain
    True
    >>> 7 < domain
    False
    >>> intersection = domain & ContinuousInterval(3, 7)
    >>> intersection
    ContinuousInterval(lower=3, upper=4.5)
    >>> 1 in intersection
    False

    There exist discrete versions as well as a bounded set:

    >>> discrete_domain = DiscreteInterval(1, 10)
    >>> discrete_domain
    DiscreteInterval(lower=1, upper=10)
    >>> 3.2 in discrete_domain
    False
    >>> 3 in discrete_domain
    True
    >>> bounded_set = discrete_domain.to_bounded_set()
    >>> bounded_set
    BoundedSet({1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, lower=1, upper=10)
    >>> intersection = bounded_set & BoundedSet([2, 4, 3.2, 12])
    >>> intersection
    BoundedSet({2, 4}, lower=1, upper=10)
    >>> intersection &= DiscreteInterval(-2, 3)
    >>> intersection
    BoundedSet({2, 4}, lower=1, upper=3)
    >>> 4 in intersection
    False

    The methods :meth:`next_smallest`, :meth:`next_largest`, and
    :meth:`next_closest` do what their name implies:

    >>> domain = BoundedSet({2, 7, 21})
    >>> domain.next_largest(8)
    21
    >>> domain.next_closest(8)
    7
    >>> domain.next_smallest(8)
    7

    """
    lower: Bound[_RealT]
    upper: Bound[_RealT]
    precision: int

    def __lt__(self, value: _RealT) -> bool:
        return self.round(self.max() - value) < 0

    def __gt__(self, value: _RealT) -> bool:
        return self.round(self.min() - value) > 0

    @abc.abstractmethod
    def __and__(self, other: object) -> _DomainT:
        ...

    def __contains__(self, value: object) -> bool:
        return isinstance(value, numbers.Real) and not (value > self or value < self)

    @abc.abstractmethod
    def min(self) -> _RealT:
        ...

    @abc.abstractmethod
    def max(self) -> _RealT:
        ...

    @abc.abstractmethod
    def next_closest(self, value: _RealT) -> _RealT:
        ...

    @abc.abstractmethod
    def next_smallest(self, value: _RealT) -> _RealT:
        ...

    @abc.abstractmethod
    def next_largest(self, value: _RealT) -> _RealT:
        ...

    def round(self, value: _RealT):
        if self.precision is None:
            return value
        try:
            # NumPy object, cast to builtin type to avoid differences
            # in the implementation of __round__
            return round(value.item(), self.precision)
        except AttributeError:
            return round(value, self.precision)

    @staticmethod
    def _transform_bound(func: Callable[[_RealT], _RealT], value: _T) -> _T:
        if isinstance(value, numbers.Real):
            return func(value)

        if is_iterable(value):
            cls = type(value)
            result = []
            for val in value:
                if callable(val):
                    result.append(lambda: func(val()))
                else:
                    result.append(val)
            return cls(result)

        raise TypeError(f'Cannot transform value of type {type(value)}')


_DomainT = TypeVar('_DomainT', bound=Domain)


@dataclass
class Interval(Domain[_RealT], Bounded[_RealT], ABC):
    """An interval with lower and upper bounds."""
    lower: _BoundT[_RealT] = Bound[_RealT](default=-inf, integral=False)
    upper: _BoundT[_RealT] = Bound[_RealT](default=+inf, integral=False)
    precision: int = field(default=16, repr=False)

    def __and__(self, other: object) -> _DomainT:
        if isinstance(other, Domain) and isinstance(other, Reciprocal):
            # let reciprocal class handle it
            return other & self

        if isinstance(other, Interval):
            cls = type(self)
            return cls(lower=self._lower | other._lower,
                       upper=self._upper | other._upper,
                       precision=min(self.precision, other.precision))

        if isinstance(other, Iterable):
            if not isinstance(other, BoundedSet):
                other = BoundedSet(other)
            return other & self

        return NotImplemented

    def min(self) -> _RealT:
        return self.lower

    def max(self) -> _RealT:
        return self.upper


@dataclass
class DiscreteInterval(Interval[_IntegralT], Bounded[_IntegralT]):
    """A discrete interval that only allows integral values.

    Examples
    --------
    >>> x = 7
    >>> domain = DiscreteInterval(lower=-4.3, upper={5, lambda: x})
    >>> domain
    DiscreteInterval(lower=-4, upper=5)
    >>> 4 in domain
    True
    >>> 4.0 in domain  # only ints
    False
    >>> domain.next_closest(1.7)
    2
    >>> domain.next_smallest(1.7)
    1

    Bounds can be dynamic and are lazily evaluated:

    >>> x = 2
    >>> 4 in domain
    False
    >>> domain
    DiscreteInterval(lower=-4, upper=2)
    """
    lower: _BoundT[_IntegralT] = Bound[_IntegralT](default=-inf, integral=True)
    upper: _BoundT[_IntegralT] = Bound[_IntegralT](default=+inf, integral=True)

    def __contains__(self, value: object) -> bool:
        return isinstance(value, numbers.Integral) and super().__contains__(value)

    def to_bounded_set(self) -> BoundedSet:
        return BoundedSet(range(self.min(), self.max() + 1),
                          lower=self.min(),
                          upper=self.max(),
                          precision=self.precision)

    def next_closest(self, value: _RealT) -> int:
        if value < self:
            return ceil(self.min())
        if value > self:
            return floor(self.max())
        return round(self.round(value))

    def next_smallest(self, value: _RealT) -> int:
        if value < self:
            return ceil(self.min())
        if value > self:
            return floor(self.max())
        return floor(self.round(value))

    def next_largest(self, value: _RealT) -> int:
        if value < self:
            return ceil(self.min())
        if value > self:
            return floor(self.max())
        return ceil(self.round(value))


class ContinuousInterval(Interval[_RealT]):
    """A continuous interval that allows any value within its bounds.

    Examples
    --------
    >>> domain = ContinuousInterval(-3.1, 1.7)
    >>> 0 in domain
    True
    >>> 1.7 in domain
    True
    >>> 10 in domain
    False
    >>> -10 < domain
    True
    >>> domain.next_smallest(0.91)
    0.91
    >>> domain.next_largest(6)
    1.7

    """

    def next_closest(self, value: _RealT) -> _RealT:
        if value < self:
            return self.min()
        if value > self:
            return self.max()
        return value

    def next_smallest(self, value: _RealT) -> _RealT:
        return self.next_closest(value)

    def next_largest(self, value: _RealT) -> _RealT:
        return self.next_closest(value)


@dataclass
class ExponentialDiscreteInterval(DiscreteInterval[_IntegralT]):
    r"""Exponentially spaced interval.

    The domain is given by::

        prefactor * base ** [lower, upper]

    with integral bounds for the exponent.

    Examples
    --------
    The interval ``[3/8, 3/4, 3/2, 3/1, 3*2]``:

    >>> domain = ExponentialDiscreteInterval(-3, 1, prefactor=3)
    >>> domain
    ExponentialDiscreteInterval(lower=-3, upper=1, prefactor=3, base=2.0)
    >>> domain.to_bounded_set()
    BoundedSet({0.375, 0.75, 1.5, 3.0, 6.0}, lower=0.375, upper=6.0)

    The ``in`` keyword works as usual:

    >>> 1.5 in domain
    True
    >>> 1 in domain
    False

    Get the next largest point in the domain:

    >>> domain.next_largest(3.7)
    6.0

    The :meth:`next_closest` method works in log-space, i.e., chooses
    the exponent that's closest to
    :math:`\log_\texttt{base}(x/\texttt{prefactor})`:

    >>> domain.next_closest(4.3)  # Not 3.0!
    6.0

    Note that for large exponents, the precision might need to be
    adjusted:

    >>> 1 << 31 in ExponentialDiscreteInterval(0, precision=16)
    False
    >>> 1 << 31 in ExponentialDiscreteInterval(0, precision=14)
    True

    """
    lower: _BoundT[_IntegralT] = Bound[_IntegralT](default=-inf, integral=True)
    upper: _BoundT[_IntegralT] = Bound[_IntegralT](default=inf, integral=True)
    prefactor: _RealT = 1.0
    base: _RealT = 2.0

    def __post_init__(self):
        if self.base <= 0:
            raise ValueError(f'Base must be positive, got {self.base}')
        self._exponent_interval = DiscreteInterval(self.lower, self.upper, self.precision)

    def __contains__(self, value: object) -> bool:
        # Works only without floating point imprecision
        try:
            exponent = self._to_exponent(value)
        except TypeError:
            return False
        return not self.round(exponent % 1) and int(exponent) in self._exponent_interval

    def __and__(self, other: object) -> _DomainT:
        cls = type(self)
        if isinstance(other, DiscreteInterval):
            if (
                    isinstance(other, cls)
                    and other.prefactor == self.prefactor
                    and other.base == self.base
            ):
                return cls(prefactor=self.prefactor,
                           base=self.base,
                           lower=self._lower | other._lower,
                           upper=self._upper | other._upper,
                           precision=min(self.precision, other.precision))

            try:
                return self.to_bounded_set() & other.to_bounded_set()
            except TypeError:
                raise NotImplementedError(f'Intersection not implemented for {self} & {other}')

        if isinstance(other, Interval):
            return cls(prefactor=self.prefactor,
                       base=self.base,
                       lower=self._lower | self._transform_bound(self._to_exponent, other._lower),
                       upper=self._upper | self._transform_bound(self._to_exponent, other._upper),
                       precision=min(self.precision, other.precision))

        if isinstance(other, Iterable):
            return self.to_bounded_set() & other

        return NotImplemented

    def _to_exponent(self, value: _RealT) -> _RealT:
        return log(value / self.prefactor, self.base)

    def _to_value(self, exponent: _RealT) -> _RealT:
        return self.prefactor * self.base ** exponent

    def to_bounded_set(self) -> BoundedSet:
        return BoundedSet((self._to_value(i) for i in range(self.lower, self.upper + 1)),
                          lower=self.min(),
                          upper=self.max(),
                          precision=self.precision)

    def next_closest(self, value: _RealT) -> _RealT:
        return self._to_value(self._exponent_interval.next_closest(self._to_exponent(value)))

    def next_smallest(self, value: _RealT) -> _RealT:
        return self._to_value(self._exponent_interval.next_smallest(self._to_exponent(value)))

    def next_largest(self, value: _RealT) -> _RealT:
        return self._to_value(self._exponent_interval.next_largest(self._to_exponent(value)))

    def min(self) -> _RealT:
        return self._to_value(self.lower)

    def max(self) -> _RealT:
        return self._to_value(self.upper)


@dataclass
class ReciprocalDiscreteInterval(DiscreteInterval[_IntegralT], Reciprocal[_RealT]):
    """A rational interval that only allows integral denominators.

    Examples
    --------
    The interval [2.3/10, 2.3/9, ..., 2.3/1]:

    >>> domain = ReciprocalDiscreteInterval(lower=1, upper=10, numerator=2.3)
    >>> 2.3/8 in domain
    True
    >>> 2.4/8 in domain
    False
    >>> 2.3/11 < domain
    True
    >>> domain.next_smallest(0.3)  # 2.3/8
    0.2875
    >>> domain.next_largest(0.3)  # 2.3/7
    0.32857142857142857
    >>> domain.next_closest(0.3)  # 2.3/8
    0.2875

    """
    lower: _BoundT[_IntegralT] = ReciprocalBound[_IntegralT](default=1, integral=True)
    upper: _BoundT[_IntegralT] = ReciprocalBound[_IntegralT](default=inf, integral=True)
    numerator: _RealT = 1.0

    def __post_init__(self):
        self._denominator_interval = DiscreteInterval(self.lower, self.upper, self.precision)

    def __contains__(self, value: object) -> bool:
        # Works only without floating point imprecision
        try:
            denominator = self._to_denominator(value)
        except TypeError:
            return False
        return not self.round(denominator % 1) and int(denominator) in self._denominator_interval

    def __and__(self, other: object) -> _DomainT:
        cls = type(self)
        if isinstance(other, DiscreteInterval):
            if isinstance(other, cls) and other.numerator == self.numerator:
                return cls(numerator=self.numerator,
                           lower=self._lower | other._lower,
                           upper=self._upper | other._upper,
                           precision=min(self.precision, other.precision))

            try:
                return self.to_bounded_set() & other.to_bounded_set()
            except TypeError:
                raise NotImplementedError(f'Intersection not implemented for {self} & {other}')

        if isinstance(other, Interval):
            return cls(
                numerator=self.numerator,
                lower=self._lower | self._transform_bound(self._to_denominator, other._upper),
                upper=self._upper | self._transform_bound(self._to_denominator, other._lower),
                precision=min(self.precision, other.precision)
            )

        if isinstance(other, Iterable):
            return self.to_bounded_set() & other

        return NotImplemented

    def to_bounded_set(self) -> BoundedSet:
        return BoundedSet((self.numerator / i for i in range(self.lower, self.upper + 1)),
                          lower=self.min(),
                          upper=self.max(),
                          precision=self.precision)

    def next_closest(self, value: _RealT) -> _RealT:
        return self.numerator / self._denominator_interval.next_closest(self.numerator / value)

    def next_smallest(self, value: _RealT) -> _RealT:
        return self.numerator / self._denominator_interval.next_largest(self.numerator / value)

    def next_largest(self, value: _RealT) -> _RealT:
        return self.numerator / self._denominator_interval.next_smallest(self.numerator / value)

    def min(self) -> _RealT:
        return self.numerator / self.upper

    def max(self) -> _RealT:
        return self.numerator / self.lower


@dataclass
class BoundedSet(frozenset, Domain[_RealT], Bounded[_RealT]):
    """A finite set of numbers with lower and upper bounds.

    Examples
    --------
    >>> domain = BoundedSet([1, 1.0, 3, -2.3, 7], lower=-4, upper=5)
    >>> domain  # behaves like frozenset
    BoundedSet({1, 3, -2.3, 7}, lower=-4, upper=5)
    >>> 3 in domain
    True
    >>> -1.7 in domain
    False
    >>> 7 in domain  # out of bounds
    False
    >>> domain.next_largest(2.7)
    3

    """
    iterable: InitVar[Iterable[_RealT]] = ...
    lower: _BoundT[_RealT] = Bound[_RealT](default=-inf, integral=False)
    upper: _BoundT[_RealT] = Bound[_RealT](default=+inf, integral=False)
    precision: int = field(default=16, repr=False)

    def __repr__(self) -> str:
        r = super().__repr__()
        r = r.replace(')', f', lower={self.lower}, upper={self.upper})', 1)
        return r

    def __and__(self, other: object) -> _DomainT:
        cls = type(self)
        if isinstance(other, Domain) and not self:
            return other

        if isinstance(other, Interval):
            return cls(self,
                       lower=self._lower | other._lower,
                       upper=self._upper | other._upper,
                       precision=min(self.precision, other.precision))

        if isinstance(other, BoundedSet):
            return cls(frozenset.intersection(self, other),
                       lower=self._lower | other._lower,
                       upper=self._upper | other._upper,
                       precision=min(self.precision, other.precision))

        if isinstance(other, Iterable):
            return cls(frozenset.intersection(self, other),
                       lower=self._lower,
                       upper=self._upper,
                       precision=self.precision)

        return NotImplemented

    def __contains__(self, value: object) -> bool:
        return (isinstance(value, numbers.Real)
                and self.round(self.lower - value) <= 0 <= self.round(self.upper - value)
                and self.round(value) in self._rounded)

    @cached_property
    def _rounded(self) -> set[_RealT]:
        return {self.round(item) for item in self}

    def min(self) -> _RealT:
        return min((item for item in self if item in self), default=nan)

    def max(self) -> _RealT:
        return max((item for item in self if item in self), default=nan)

    def next_closest(self, value: _RealT) -> _RealT:
        return next_closest(self, value, self.precision)

    def next_smallest(self, value: _RealT) -> _RealT:
        return next_smallest(self, value, self.precision)

    def next_largest(self, value: _RealT) -> _RealT:
        return next_largest(self, value, self.precision)
