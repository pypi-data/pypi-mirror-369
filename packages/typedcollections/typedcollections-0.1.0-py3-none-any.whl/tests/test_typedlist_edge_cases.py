# tests/test_typedlist_edge_cases.py
import pytest
from hypothesis import given, strategies as st
from typedcollections.typedlist import TypedList
from typedcollections.exceptions import TypedListTypeError,CoercionError

# --- BASIC BEHAVIOR ---
def test_empty_strict():
    tl = TypedList(int, [], strict=True)
    assert len(tl) == 0

def test_append_valid():
    tl = TypedList(int, strict=True)
    tl.append(5)
    assert tl[0] == 5

def test_append_invalid_strict():
    tl = TypedList(int, strict=True)
    with pytest.raises(TypedListTypeError):
        tl.append("not an int")

def test_extend_valid():
    tl = TypedList(str, strict=True)
    tl.extend(["a", "b"])
    assert tl == ["a", "b"]

# --- TYPE ENFORCEMENT ---
def test_non_strict_coercion():
    tl = TypedList(int, strict=False)
    tl.append("42")  # should coerce to int
    assert tl[0] == 42

def test_non_strict_coercion_failure():
    tl = TypedList(int, strict=False)
    with pytest.raises(CoercionError):
        tl.append("abc")  # can't be coerced to int

# --- SPECIAL VALUES ---
def test_none_in_strict_mode():
    with pytest.raises(TypedListTypeError):
        TypedList(int, [1, None], strict=True)

def test_none_with_type_none():
    tl = TypedList(type(None), [None], strict=True)
    assert tl == [None]

def test_nested_typedlist():
    inner = TypedList(int, [1, 2, 3], strict=True)
    outer = TypedList(TypedList, [inner], strict=True)
    assert isinstance(outer[0], TypedList)

# --- LARGE INPUT ---
def test_large_append():
    tl = TypedList(int, strict=True)
    for i in range(100_000):
        tl.append(i)
    assert len(tl) == 100_000

# --- HYPOTHESIS PROPERTY TESTS ---
@given(st.lists(st.integers()))
def test_strict_integers_only(data):
    tl = TypedList(int, data, strict=True)
    assert all(isinstance(x, int) for x in tl)

@given(st.lists(st.integers() | st.text()))
def test_strict_mode_rejects_non_int(data):
    try:
        tl = TypedList(int, data, strict=True)
        assert all(isinstance(x, int) for x in tl)
    except TypedListTypeError:
        assert True
