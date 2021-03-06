import numpy as np
import pytest

import pygeos

from .common import assert_geometries_equal, line_string, linear_ring, point, polygon

pnts = pygeos.points
lstrs = pygeos.linestrings
geom_coll = pygeos.geometrycollections


@pytest.mark.parametrize(
    "func", [pygeos.points, pygeos.linestrings, pygeos.linearrings]
)
@pytest.mark.parametrize(
    "coordinates",
    [
        np.empty((2,)),  # not enough dimensions
        np.empty((2, 4, 1)),  # too many dimensions
        np.empty((2, 4)),  # wrong inner dimension size
        None,
        np.full((2, 2), "foo", dtype=object),  # wrong type
    ],
)
def test_invalid_coordinates(func, coordinates):
    with pytest.raises((TypeError, ValueError)):
        func(coordinates, indices=[0, 1])


@pytest.mark.parametrize(
    "func",
    [
        pygeos.multipoints,
        pygeos.multilinestrings,
        pygeos.multipolygons,
        pygeos.geometrycollections,
    ],
)
@pytest.mark.parametrize(
    "geometries", [np.array([1, 2], dtype=np.int32), None, np.array([[point]]), "hello"]
)
def test_invalid_geometries(func, geometries):
    with pytest.raises((TypeError, ValueError)):
        func(geometries, indices=[0, 1])


@pytest.mark.parametrize(
    "func", [pygeos.points, pygeos.linestrings, pygeos.linearrings]
)
@pytest.mark.parametrize("indices", [[point], " hello", [0, 1], [-1]])
def test_invalid_indices_simple(func, indices):
    with pytest.raises((TypeError, ValueError)):
        func([[0.2, 0.3]], indices=indices)


def test_points_invalid():
    # attempt to construct a point with 2 coordinates
    with pytest.raises(pygeos.GEOSException):
        pygeos.points([[1, 1], [2, 2]], indices=[0, 0])


def test_points():
    actual = pygeos.points([[2, 3], [2, 3]], indices=[0, 2])
    assert_geometries_equal(actual, [point, None, point])


@pytest.mark.parametrize(
    "coordinates,indices,expected",
    [
        ([[1, 1], [2, 2]], [0, 0], [lstrs([[1, 1], [2, 2]])]),
        ([[1, 1, 1], [2, 2, 2]], [0, 0], [lstrs([[1, 1, 1], [2, 2, 2]])]),
        ([[1, 1], [2, 2]], [1, 1], [None, lstrs([[1, 1], [2, 2]])]),
        (
            [[1, 1], [2, 2], [2, 2], [3, 3]],
            [0, 0, 1, 1],
            [lstrs([[1, 1], [2, 2]]), lstrs([[2, 2], [3, 3]])],
        ),
    ],
)
def test_linestrings(coordinates, indices, expected):
    actual = pygeos.linestrings(coordinates, indices=indices)
    assert_geometries_equal(actual, expected)


def test_linestrings_invalid():
    # attempt to construct linestrings with 1 coordinate
    with pytest.raises(pygeos.GEOSException):
        pygeos.linestrings([[1, 1], [2, 2]], indices=[0, 1])


@pytest.mark.parametrize(
    "coordinates", [([[1, 1], [2, 1], [2, 2], [1, 1]]), ([[1, 1], [2, 1], [2, 2]])]
)
def test_linearrings(coordinates):
    actual = pygeos.linearrings(coordinates, indices=len(coordinates) * [0])
    assert_geometries_equal(actual, pygeos.linearrings(coordinates))


@pytest.mark.parametrize(
    "coordinates",
    [
        ([[1, 1], [2, 1], [1, 1]]),  # too few coordinates
        ([[1, np.nan], [2, 1], [2, 2], [1, 1]]),  # starting with nan
    ],
)
def test_linearrings_invalid(coordinates):
    # attempt to construct linestrings with 1 coordinate
    with pytest.raises(pygeos.GEOSException):
        pygeos.linearrings(coordinates, indices=np.zeros(len(coordinates)))


@pytest.mark.parametrize("shells", [[point], [line_string], "hello", [2]])
def test_polygons_invalid_shells(shells):
    with pytest.raises((TypeError, ValueError, pygeos.GEOSException)):
        pygeos.polygons(shells, [linear_ring], indices=[0])


@pytest.mark.parametrize("holes", [[1, 2], None, [linear_ring, point], "hello"])
def test_polygons_invalid_holes(holes):
    with pytest.raises((TypeError, ValueError, pygeos.GEOSException)):
        pygeos.polygons([linear_ring, linear_ring], holes, indices=[0, 1])


@pytest.mark.parametrize("indices", [[1, 2], [point], "hello", [1], [-1]])
def test_polygons_invalid_indices(indices):
    with pytest.raises((TypeError, ValueError)):
        pygeos.polygons([linear_ring], [linear_ring], indices=indices)


hole_1 = pygeos.linearrings([(0.2, 0.2), (0.2, 0.4), (0.4, 0.4)])
hole_2 = pygeos.linearrings([(0.6, 0.6), (0.6, 0.8), (0.8, 0.8)])
poly = pygeos.polygons(linear_ring)
poly_hole_1 = pygeos.polygons(linear_ring, holes=[hole_1])
poly_hole_2 = pygeos.polygons(linear_ring, holes=[hole_2])
poly_hole_1_2 = pygeos.polygons(linear_ring, holes=[hole_1, hole_2])


@pytest.mark.parametrize(
    "holes,indices,expected",
    [
        ([None], [1], [poly, poly]),
        ([hole_1], [0], [poly_hole_1, poly]),
        ([hole_1], [1], [poly, poly_hole_1]),
        ([hole_1, hole_2], [0, 0], [poly_hole_1_2, poly]),
        ([hole_1, hole_2], [0, 1], [poly_hole_1, poly_hole_2]),
        ([hole_1, None, hole_2], [0, 0, 0], [poly_hole_1_2, poly]),
        ([hole_1, None, hole_2], [0, 0, 1], [poly_hole_1, poly_hole_2]),
        ([hole_1, None, hole_2], [0, 1, 1], [poly_hole_1, poly_hole_2]),
    ],
)
def test_polygons(holes, indices, expected):
    actual = pygeos.polygons([linear_ring, linear_ring], holes, indices=indices)
    assert_geometries_equal(actual, expected)


def test_polygons_missing_shell():
    actual = pygeos.polygons([None, linear_ring], [hole_1, hole_2], indices=[0, 1])
    assert_geometries_equal(actual, [None, poly_hole_2])


@pytest.mark.parametrize(
    "func",
    [
        pygeos.multipoints,
        pygeos.multilinestrings,
        pygeos.multipolygons,
        pygeos.geometrycollections,
    ],
)
@pytest.mark.parametrize("indices", [np.array([point]), " hello", [0, 1], [-1]])
def test_invalid_indices_collections(func, indices):
    with pytest.raises((TypeError, ValueError)):
        func([point], indices=indices)


@pytest.mark.parametrize(
    "geometries,indices,expected",
    [
        ([point, line_string], [0, 0], [geom_coll([point, line_string])]),
        ([point, line_string], [0, 1], [geom_coll([point]), geom_coll([line_string])]),
        (
            [point, line_string],
            [1, 1],
            [geom_coll([]), geom_coll([point, line_string])],
        ),
        ([point, None], [0, 0], [geom_coll([point])]),
        ([point, None], [0, 1], [geom_coll([point]), geom_coll([])]),
        ([point, None, line_string], [0, 0, 0], [geom_coll([point, line_string])]),
    ],
)
def test_geometrycollections(geometries, indices, expected):
    actual = pygeos.geometrycollections(geometries, indices=indices)
    assert_geometries_equal(actual, expected)


def test_multipoints():
    actual = pygeos.multipoints([point], indices=[0])
    assert_geometries_equal(actual, pygeos.multipoints([point]))


def test_multilinestrings():
    actual = pygeos.multilinestrings([line_string], indices=[0])
    assert_geometries_equal(actual, pygeos.multilinestrings([line_string]))


def test_multilinearrings():
    actual = pygeos.multilinestrings([linear_ring], indices=[0])
    assert_geometries_equal(actual, pygeos.multilinestrings([linear_ring]))


def test_multipolygons():
    actual = pygeos.multipolygons([polygon], indices=[0])
    assert_geometries_equal(actual, pygeos.multipolygons([polygon]))


@pytest.mark.parametrize(
    "geometries,func",
    [
        ([line_string], pygeos.multipoints),
        ([polygon], pygeos.multipoints),
        ([point], pygeos.multilinestrings),
        ([polygon], pygeos.multilinestrings),
        ([point], pygeos.multipolygons),
        ([line_string], pygeos.multipolygons),
    ],
)
def test_incompatible_types(geometries, func):
    with pytest.raises(TypeError):
        func(geometries, indices=[0])
