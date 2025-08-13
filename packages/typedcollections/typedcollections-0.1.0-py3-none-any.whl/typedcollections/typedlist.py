from __future__ import annotations
from collections.abc import MutableSequence
from .exceptions import TypedListTypeError
from typing import (
    TypeVar, Generic, Type, Tuple, Iterable, Iterator,
    Callable, Optional, Any
)
import json
from .exceptions import CoercionError, ValidationError

T = TypeVar("T")

Validator = Callable[[T], bool]
Coercer = Callable[[Any], T]


class TypedList(MutableSequence, Generic[T]):
    """
    TypedList — A list-like container enforcing element type(s).

    Features:
    - Accept one or multiple allowed types (e.g. int or (int, float))
    - strict (raise on wrong type) or coerce (convert where possible)
    - optional validator callable for extra validation
    - fully list-compatible (slicing, +, *, in-place ops)
    - helpers: map, filter, unique, sort, reverse, to_json/from_json, copy, to_list
    """

    def __init__(
        self,
        dtype: Type[T] | tuple[Type[Any], ...],
        iterable: Optional[Iterable[Any]] = None,
        *,
        strict: bool = True,
        validator: Optional[Validator] = None,
        coercer: Optional[Coercer] = None,
    ) -> None:
        if not isinstance(dtype, (type, tuple)):
            raise TypedListTypeError("dtype must be a type or a tuple of types")
        self.dtype = dtype
        self.strict = strict
        self.validator = validator
        self._coercer = coercer
        self._data: list[T] = []
        if iterable:
            self.extend(iterable)

    # ---------- helpers ----------
    def _dtype_names(self) -> str:
        if isinstance(self.dtype, type):
            return self.dtype.__name__
        return "(" + ", ".join(t.__name__ for t in self.dtype) + ")"

    def _try_coerce(self, value: Any) -> T:
        """Attempt to coerce using provided coercer or built-in tries."""
        if self._coercer is not None:
            try:
                return self._coercer(value)
            except Exception as exc:
                raise CoercionError(f"Coercion via custom coercer failed for {value!r}") from exc

        # built-in coercion
        if isinstance(self.dtype, type):
            try:
                return self.dtype(value)
            except Exception as exc:
                raise CoercionError(f"Could not coerce {value!r} to {self._dtype_names()}") from exc

        last_exc = None
        for typ in self.dtype:
            try:
                return typ(value)  
            except Exception as exc:
                last_exc = exc
        raise CoercionError(f"Could not coerce {value!r} to any of {self._dtype_names()}") from last_exc

    def _validate_value(self, value: Any) -> T:
        """Validate (and coerce if allowed) and run validator if present."""
        if isinstance(value, self.dtype):
            val: T = value  
        elif not self.strict:
            val = self._try_coerce(value)
        else:
            raise TypedListTypeError(f"Expected {self._dtype_names()}, got {type(value).__name__}")

        if self.validator is not None:
            ok = False
            try:
                ok = self.validator(val)
            except Exception as exc:
                raise ValidationError("Validator raised an exception") from exc
            if not ok:
                raise ValidationError(f"Validator rejected value: {val!r}")
        return val

    # ---------- MutableSequence contract ----------
    def __getitem__(self, index):
        if isinstance(index, slice):
            return TypedList(self.dtype, self._data[index], strict=self.strict,
                             validator=self.validator, coercer=self._coercer)
        return self._data[index]

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            values = list(value)
            validated = [self._validate_value(v) for v in values]
            self._data[index] = validated
        else:
            self._data[index] = self._validate_value(value)

    def __delitem__(self, index):
        del self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def insert(self, index: int, value: Any) -> None:
        self._data.insert(index, self._validate_value(value))

    # ---------- list-like methods ----------
    def append(self, value: Any) -> None:
        self._data.append(self._validate_value(value))

    def extend(self, iterable: Iterable[Any]) -> None:
        for item in iterable:
            self.append(item)

    def pop(self, index: int = -1):
        return self._data.pop(index)

    def remove(self, value: Any) -> None:
        self._data.remove(value)

    def clear(self) -> None:
        self._data.clear()

    def index(self, value: Any, start: int = 0, stop: Optional[int] = None) -> int:
        if stop is None:
            stop = len(self._data)
        return self._data.index(value, start, stop)

    def count(self, value: Any) -> int:
        return self._data.count(value)

    # ---------- extras ----------
    def to_list(self) -> list[T]:
        """Return a shallow Python list copy."""
        return list(self._data)

    def copy(self) -> "TypedList[T]":
        """Return a shallow copy (same dtype, strict, validator, coercer)."""
        return TypedList(self.dtype, self._data.copy(), strict=self.strict,
                         validator=self.validator, coercer=self._coercer)

    def to_json(self) -> str:
        """Serialize internal list to JSON (values must be JSON serializable)."""
        return json.dumps(self._data)

    @classmethod
    def from_json(cls, dtype, json_str: str, *, strict: bool = True,
                  validator: Optional[Validator] = None,
                  coercer: Optional[Coercer] = None) -> "TypedList":
        data = json.loads(json_str)
        if not isinstance(data, list):
            raise TypedListTypeError("JSON must represent a list")
        return cls(dtype, data, strict=strict, validator=validator, coercer=coercer)

    def unique(self) -> "TypedList[T]":
        seen = set()
        out = []
        for x in self._data:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return TypedList(self.dtype, out, strict=self.strict,
                         validator=self.validator, coercer=self._coercer)

    def map(self, func: Callable[[T], Any]) -> "TypedList[T]":
        return TypedList(self.dtype, (func(x) for x in self._data),
                         strict=self.strict, validator=self.validator, coercer=self._coercer)

    def filter(self, predicate: Callable[[T], bool]) -> "TypedList[T]":
        return TypedList(self.dtype, (x for x in self._data if predicate(x)),
                         strict=self.strict, validator=self.validator, coercer=self._coercer)

    def sort(self, *, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> None:
        self._data.sort(key=key, reverse=reverse)

    def reversed(self) -> "TypedList[T]":
        return TypedList(self.dtype, list(reversed(self._data)),
                         strict=self.strict, validator=self.validator, coercer=self._coercer)

    def reverse(self) -> None:
        self._data.reverse()

    # ---------- dunder/ops ----------
    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __contains__(self, item: Any) -> bool:
        return item in self._data

    def __repr__(self) -> str:
        return f"TypedList({self._dtype_names()}, {self._data}, strict={self.strict})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TypedList):
            return self.dtype == other.dtype and self._data == other._data
        if isinstance(other, list):
            return self._data == other
        return False

    def __add__(self, other: Iterable[Any]) -> "TypedList[T]":
        if isinstance(other, TypedList):
            new = TypedList(self.dtype, self._data, strict=self.strict,
                            validator=self.validator, coercer=self._coercer)
            new.extend(other._data)
            return new
        new = TypedList(self.dtype, self._data, strict=self.strict,
                        validator=self.validator, coercer=self._coercer)
        new.extend(other)
        return new

    def __iadd__(self, other: Iterable[Any]) -> "TypedList[T]":
        self.extend(other)
        return self

    def __mul__(self, n: int) -> "TypedList[T]":
        return TypedList(self.dtype, self._data * n, strict=self.strict,
                         validator=self.validator, coercer=self._coercer)

    def __rmul__(self, n: int) -> "TypedList[T]":
        return self.__mul__(n)