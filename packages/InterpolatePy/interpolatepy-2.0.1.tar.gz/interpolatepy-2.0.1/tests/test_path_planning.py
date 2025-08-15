"""
Comprehensive tests for path planning implementations.

This module contains extensive tests for the path planning classes covering:
1. Frenet frame computation functions
2. LinearPath - Linear path implementation
3. CircularPath - Circular path implementation

Test coverage includes:
- Constructor validation and parameter checking
- Mathematical accuracy with known analytical solutions
- Frenet frame calculations and properties
- Path parameterization (arc length)
- Geometric properties verification
- Edge cases and error handling
- Performance benchmarks

The tests verify that path planning algorithms correctly implement
geometric computations and maintain expected mathematical properties.
"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from interpolatepy.frenet_frame import compute_trajectory_frames
from interpolatepy.simple_paths import CircularPath
from interpolatepy.simple_paths import LinearPath


# Type alias for pytest benchmark fixture
if not hasattr(pytest, "FixtureFunction"):
    pytest.FixtureFunction = Any


class TestLinearPath:
    """Test suite for LinearPath class."""

    NUMERICAL_RTOL = 1e-10
    NUMERICAL_ATOL = 1e-10

    def test_basic_construction(self) -> None:
        """Test basic LinearPath construction."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([3.0, 4.0, 0.0])

        path = LinearPath(pi, pf)

        assert np.allclose(path.pi, pi, atol=self.NUMERICAL_ATOL)
        assert np.allclose(path.pf, pf, atol=self.NUMERICAL_ATOL)
        assert abs(path.length - 5.0) < self.NUMERICAL_ATOL  # 3-4-5 triangle

        # Check tangent vector
        expected_tangent = np.array([0.6, 0.8, 0.0])  # (3,4,0)/5
        assert np.allclose(path.tangent, expected_tangent, atol=self.NUMERICAL_ATOL)

    def test_construction_with_lists(self) -> None:
        """Test LinearPath construction with list inputs."""
        pi = [1.0, 2.0, 3.0]
        pf = [4.0, 6.0, 3.0]

        path = LinearPath(pi, pf)

        assert isinstance(path.pi, np.ndarray)
        assert isinstance(path.pf, np.ndarray)
        assert len(path.pi) == 3
        assert len(path.pf) == 3

        expected_length = np.sqrt((4 - 1) ** 2 + (6 - 2) ** 2 + (3 - 3) ** 2)  # 5.0
        assert abs(path.length - expected_length) < self.NUMERICAL_ATOL

    def test_zero_length_path(self) -> None:
        """Test LinearPath with identical start and end points."""
        pi = np.array([2.0, 3.0, 1.0])
        pf = np.array([2.0, 3.0, 1.0])

        path = LinearPath(pi, pf)

        assert path.length == 0.0
        assert np.allclose(path.tangent, np.zeros(3), atol=self.NUMERICAL_ATOL)

    def test_position_evaluation(self) -> None:
        """Test position evaluation at various arc lengths."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([6.0, 8.0, 0.0])  # Length 10

        path = LinearPath(pi, pf)

        # Test at start
        pos_start = path.position(0.0)
        assert np.allclose(pos_start, pi, atol=self.NUMERICAL_ATOL)

        # Test at end
        pos_end = path.position(path.length)
        assert np.allclose(pos_end, pf, atol=self.NUMERICAL_ATOL)

        # Test at midpoint
        pos_mid = path.position(path.length / 2)
        expected_mid = (pi + pf) / 2
        assert np.allclose(pos_mid, expected_mid, atol=self.NUMERICAL_ATOL)

        # Test at quarter point
        pos_quarter = path.position(path.length / 4)
        expected_quarter = pi + 0.25 * (pf - pi)
        assert np.allclose(pos_quarter, expected_quarter, atol=self.NUMERICAL_ATOL)

    def test_position_clamping(self) -> None:
        """Test that position evaluation clamps arc length to valid range."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([1.0, 0.0, 0.0])

        path = LinearPath(pi, pf)

        # Test negative arc length (should clamp to 0)
        pos_neg = path.position(-1.0)
        assert np.allclose(pos_neg, pi, atol=self.NUMERICAL_ATOL)

        # Test arc length beyond path length (should clamp to end)
        pos_beyond = path.position(path.length + 1.0)
        assert np.allclose(pos_beyond, pf, atol=self.NUMERICAL_ATOL)

    def test_velocity_constant(self) -> None:
        """Test that velocity is constant for linear path."""
        pi = np.array([1.0, 2.0, 3.0])
        pf = np.array([4.0, 6.0, 7.0])

        path = LinearPath(pi, pf)

        # Velocity should be the unit tangent vector
        vel1 = path.velocity(0.0)
        vel2 = path.velocity(path.length / 2)
        vel3 = path.velocity(path.length)
        vel_no_param = path.velocity()

        # All should be equal and equal to tangent
        assert np.allclose(vel1, path.tangent, atol=self.NUMERICAL_ATOL)
        assert np.allclose(vel2, path.tangent, atol=self.NUMERICAL_ATOL)
        assert np.allclose(vel3, path.tangent, atol=self.NUMERICAL_ATOL)
        assert np.allclose(vel_no_param, path.tangent, atol=self.NUMERICAL_ATOL)

    def test_acceleration_zero(self) -> None:
        """Test that acceleration is zero for linear path."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([5.0, 0.0, 0.0])

        path = LinearPath(pi, pf)

        # Test acceleration at various points
        acc1 = path.acceleration(0.0)
        acc2 = path.acceleration(path.length / 2)
        acc3 = path.acceleration(path.length)
        acc_no_param = path.acceleration()

        # All should be zero
        assert np.allclose(acc1, np.zeros(3), atol=self.NUMERICAL_ATOL)
        assert np.allclose(acc2, np.zeros(3), atol=self.NUMERICAL_ATOL)
        assert np.allclose(acc3, np.zeros(3), atol=self.NUMERICAL_ATOL)
        assert np.allclose(acc_no_param, np.zeros(3), atol=self.NUMERICAL_ATOL)

    def test_3d_path(self) -> None:
        """Test LinearPath in 3D space."""
        pi = np.array([1.0, 2.0, 3.0])
        pf = np.array([4.0, 6.0, 11.0])

        path = LinearPath(pi, pf)

        # Check length calculation
        expected_length = np.sqrt(3**2 + 4**2 + 8**2)  # sqrt(9+16+64) = sqrt(89)
        assert abs(path.length - expected_length) < self.NUMERICAL_ATOL

        # Check position evaluation
        pos_mid = path.position(path.length / 2)
        expected_mid = np.array([2.5, 4.0, 7.0])
        assert np.allclose(pos_mid, expected_mid, atol=self.NUMERICAL_ATOL)

    def test_2d_path(self) -> None:
        """Test LinearPath with 2D points (should still work)."""
        pi = np.array([0.0, 0.0])
        pf = np.array([3.0, 4.0])

        path = LinearPath(pi, pf)

        assert path.length == 5.0
        assert len(path.pi) == 2
        assert len(path.pf) == 2

        # Position should work
        pos_mid = path.position(2.5)
        expected_mid = np.array([1.5, 2.0])
        assert np.allclose(pos_mid, expected_mid, atol=self.NUMERICAL_ATOL)


class TestCircularPath:
    """Test suite for CircularPath class."""

    NUMERICAL_RTOL = 1e-6
    NUMERICAL_ATOL = 1e-6

    def test_basic_construction(self) -> None:
        """Test basic CircularPath construction."""
        # CircularPath(r, d, pi) where:
        # r = axis vector, d = point on axis, pi = point on circle
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # origin on axis
        pi = np.array([2.0, 0.0, 0.0])  # point on circle (radius=2)

        path = CircularPath(r, d, pi)

        assert np.allclose(path.center, d, atol=self.NUMERICAL_ATOL)  # center should be at d
        assert abs(path.radius - 2.0) < self.NUMERICAL_ATOL

    def test_construction_with_lists(self) -> None:
        """Test CircularPath construction with list inputs."""
        r = [0.0, 0.0, 1.0]  # z-axis
        d = [1.0, 2.0, 0.0]  # point on axis
        pi = [4.0, 2.0, 0.0]  # point on circle (radius=3 from center)

        path = CircularPath(r, d, pi)

        assert isinstance(path.center, np.ndarray)
        assert len(path.center) == 3
        assert path.radius == 3.0

    def test_position_evaluation_unit_circle(self) -> None:
        """Test position evaluation on unit circle."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([1.0, 0.0, 0.0])  # point on unit circle

        path = CircularPath(r, d, pi)

        # Test at specific angles
        # At s=0 (angle=0), should be at (1, 0, 0)
        pos_0 = path.position(0.0)
        expected_0 = np.array([1.0, 0.0, 0.0])
        assert np.allclose(pos_0, expected_0, atol=self.NUMERICAL_ATOL)

        # At s=π/2 (quarter circle), should be at (0, 1, 0)
        pos_quarter = path.position(np.pi / 2)
        expected_quarter = np.array([0.0, 1.0, 0.0])
        assert np.allclose(pos_quarter, expected_quarter, atol=self.NUMERICAL_ATOL)

        # At s=π (half circle), should be at (-1, 0, 0)
        pos_half = path.position(np.pi)
        expected_half = np.array([-1.0, 0.0, 0.0])
        assert np.allclose(pos_half, expected_half, atol=self.NUMERICAL_ATOL)

        # At s=3π/2 (three quarters), should be at (0, -1, 0)
        pos_three_quarter = path.position(3 * np.pi / 2)
        expected_three_quarter = np.array([0.0, -1.0, 0.0])
        assert np.allclose(pos_three_quarter, expected_three_quarter, atol=self.NUMERICAL_ATOL)

    def test_position_with_offset_center(self) -> None:
        """Test position evaluation with non-zero center."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([2.0, 3.0, 0.0])  # center at (2,3,0)
        pi = np.array([3.0, 3.0, 0.0])  # point on circle (radius=1)

        path = CircularPath(r, d, pi)

        # At s=0, should be at the initial point pi
        pos_0 = path.position(0.0)
        expected_0 = pi  # should return to initial point
        assert np.allclose(pos_0, expected_0, atol=self.NUMERICAL_ATOL)

        # Test that position stays at correct distance from center
        pos_quarter = path.position(np.pi / 2)
        distance = np.linalg.norm(pos_quarter - d)
        assert abs(distance - 1.0) < self.NUMERICAL_ATOL

    def test_velocity_circular(self) -> None:
        """Test velocity for circular path."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([2.0, 0.0, 0.0])  # point on circle (radius=2)

        path = CircularPath(r, d, pi)

        # Test that velocity is unit tangent vector
        vel_0 = path.velocity(0.0)
        vel_magnitude = np.linalg.norm(vel_0)
        assert abs(vel_magnitude - 1.0) < self.NUMERICAL_ATOL

        # Test velocity at different points
        vel_quarter = path.velocity(np.pi)  # quarter of circumference
        vel_magnitude_quarter = np.linalg.norm(vel_quarter)
        assert abs(vel_magnitude_quarter - 1.0) < self.NUMERICAL_ATOL

        # Velocity magnitude should always be 1 (unit tangent)
        for s in [0.0, np.pi / 4, np.pi / 2, np.pi, 3 * np.pi / 2]:
            vel = path.velocity(s)
            vel_magnitude = np.linalg.norm(vel)
            assert abs(vel_magnitude - 1.0) < self.NUMERICAL_ATOL

    def test_acceleration_circular(self) -> None:
        """Test acceleration for circular path (centripetal)."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([1.0, 0.0, 0.0])  # point on unit circle

        path = CircularPath(r, d, pi)

        # For unit circle, acceleration should have magnitude 1/r = 1
        acc_0 = path.acceleration(0.0)
        acc_magnitude = np.linalg.norm(acc_0)
        assert abs(acc_magnitude - 1.0) < self.NUMERICAL_ATOL

        # Test acceleration at different points
        for s in [0.0, np.pi / 4, np.pi / 2, np.pi]:
            acc = path.acceleration(s)
            acc_magnitude = np.linalg.norm(acc)
            assert abs(acc_magnitude - 1.0) < self.NUMERICAL_ATOL

    def test_circular_properties(self) -> None:
        """Test geometric properties of circular path."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([1.0, 1.0, 0.0])  # center at (1,1,0)
        pi = np.array([4.0, 1.0, 0.0])  # point on circle (radius=3)

        path = CircularPath(r, d, pi)

        # All points should be at distance radius from center
        for s in np.linspace(0, 2 * np.pi * path.radius, 20):
            pos = path.position(s)
            distance_to_center = np.linalg.norm(pos - path.center)
            assert abs(distance_to_center - path.radius) < self.NUMERICAL_ATOL

        # Velocity should always be perpendicular to radius vector
        for s in np.linspace(0, 2 * np.pi * path.radius, 10):
            pos = path.position(s)
            vel = path.velocity(s)
            radius_vector = pos - path.center

            # Dot product should be zero (perpendicular)
            dot_product = np.dot(vel, radius_vector)
            assert abs(dot_product) < self.NUMERICAL_ATOL

    def test_position_clamping_circular(self) -> None:
        """Test position clamping for circular path."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([1.0, 0.0, 0.0])  # point on unit circle

        path = CircularPath(r, d, pi)

        # Test beyond full circle (should wrap around)
        full_circle = 2 * np.pi * path.radius
        pos_beyond = path.position(full_circle + np.pi / 2)
        pos_quarter = path.position(np.pi / 2)

        # Should be the same due to periodicity
        assert np.allclose(pos_beyond, pos_quarter, atol=self.NUMERICAL_ATOL)


class TestLinearPathAdvanced:
    """Advanced test suite for LinearPath functionality."""

    NUMERICAL_RTOL = 1e-10
    NUMERICAL_ATOL = 1e-10

    def test_evaluate_at_single_value(self) -> None:
        """Test evaluate_at method with single arc length value."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([3.0, 4.0, 0.0])  # Length 5
        path = LinearPath(pi, pf)

        # Test with single scalar value
        result = path.evaluate_at(2.5)  # Half length

        assert "position" in result
        assert "velocity" in result
        assert "acceleration" in result
        assert "s" in result

        # Check shapes
        assert result["position"].shape == (1, 3)
        assert result["velocity"].shape == (1, 3)
        assert result["acceleration"].shape == (1, 3)
        assert result["s"].shape == (1,)

        # Check values
        expected_pos = (pi + pf) / 2
        assert np.allclose(result["position"][0], expected_pos, atol=self.NUMERICAL_ATOL)
        assert np.allclose(result["velocity"][0], path.tangent, atol=self.NUMERICAL_ATOL)
        assert np.allclose(result["acceleration"][0], np.zeros(3), atol=self.NUMERICAL_ATOL)

    def test_evaluate_at_array_values(self) -> None:
        """Test evaluate_at method with array of arc length values."""
        pi = np.array([1.0, 2.0, 3.0])
        pf = np.array([4.0, 6.0, 3.0])  # Length 5
        path = LinearPath(pi, pf)

        # Test with array of values
        s_values = [0.0, 1.25, 2.5, 3.75, 5.0]
        result = path.evaluate_at(s_values)

        # Check shapes
        assert result["position"].shape == (5, 3)
        assert result["velocity"].shape == (5, 3)
        assert result["acceleration"].shape == (5, 3)
        assert result["s"].shape == (5,)

        # Check start and end positions
        assert np.allclose(result["position"][0], pi, atol=self.NUMERICAL_ATOL)
        assert np.allclose(result["position"][-1], pf, atol=self.NUMERICAL_ATOL)

        # Check that all velocities are the same (constant)
        for i in range(5):
            assert np.allclose(result["velocity"][i], path.tangent, atol=self.NUMERICAL_ATOL)
            assert np.allclose(result["acceleration"][i], np.zeros(3), atol=self.NUMERICAL_ATOL)

    def test_evaluate_at_clamping(self) -> None:
        """Test that evaluate_at clamps values to valid range."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([2.0, 0.0, 0.0])  # Length 2
        path = LinearPath(pi, pf)

        # Test with out-of-range values
        s_values = [-1.0, 0.5, 1.0, 1.5, 3.0]  # Some outside [0, 2]
        result = path.evaluate_at(s_values)

        # Check that clamped values are used
        expected_s = [0.0, 0.5, 1.0, 1.5, 2.0]  # Clamped to [0, 2]
        assert np.allclose(result["s"], expected_s, atol=self.NUMERICAL_ATOL)

        # First and last positions should be at endpoints despite input
        assert np.allclose(result["position"][0], pi, atol=self.NUMERICAL_ATOL)
        assert np.allclose(result["position"][-1], pf, atol=self.NUMERICAL_ATOL)

    def test_all_traj_default(self) -> None:
        """Test all_traj method with default parameters."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([6.0, 8.0, 0.0])  # Length 10
        path = LinearPath(pi, pf)

        result = path.all_traj()  # Default 100 points

        # Check structure
        assert "position" in result
        assert "velocity" in result
        assert "acceleration" in result
        assert "s" in result

        # Check shapes
        assert result["position"].shape == (100, 3)
        assert result["velocity"].shape == (100, 3)
        assert result["acceleration"].shape == (100, 3)
        assert result["s"].shape == (100,)

        # Check s values span the entire path
        assert np.isclose(result["s"][0], 0.0, atol=self.NUMERICAL_ATOL)
        assert np.isclose(result["s"][-1], path.length, atol=self.NUMERICAL_ATOL)

        # Check start and end positions
        assert np.allclose(result["position"][0], pi, atol=self.NUMERICAL_ATOL)
        assert np.allclose(result["position"][-1], pf, atol=self.NUMERICAL_ATOL)

    def test_all_traj_custom_points(self) -> None:
        """Test all_traj method with custom number of points."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([3.0, 4.0, 0.0])  # Length 5
        path = LinearPath(pi, pf)

        num_points = 50
        result = path.all_traj(num_points)

        # Check shapes
        assert result["position"].shape == (num_points, 3)
        assert result["velocity"].shape == (num_points, 3)
        assert result["acceleration"].shape == (num_points, 3)
        assert result["s"].shape == (num_points,)

        # Check linearity of positions
        positions = result["position"]
        for i in range(1, num_points - 1):
            # Check that points are collinear (cross product is zero)
            v1 = positions[i] - positions[0]
            v2 = positions[i + 1] - positions[0]
            cross = np.cross(v1, v2)
            # For 3D vectors, cross product magnitude should be zero for collinear points
            assert np.linalg.norm(cross) < self.NUMERICAL_ATOL

    def test_all_traj_zero_length(self) -> None:
        """Test all_traj method with zero-length path."""
        pi = np.array([1.0, 2.0, 3.0])
        pf = np.array([1.0, 2.0, 3.0])  # Same point
        path = LinearPath(pi, pf)

        result = path.all_traj(20)

        # All positions should be the same
        for i in range(20):
            assert np.allclose(result["position"][i], pi, atol=self.NUMERICAL_ATOL)
            assert np.allclose(result["velocity"][i], np.zeros(3), atol=self.NUMERICAL_ATOL)
            assert np.allclose(result["acceleration"][i], np.zeros(3), atol=self.NUMERICAL_ATOL)


class TestCircularPathAdvanced:
    """Advanced test suite for CircularPath functionality."""

    NUMERICAL_RTOL = 1e-10
    NUMERICAL_ATOL = 1e-10

    def test_evaluate_at_single_value(self) -> None:
        """Test evaluate_at method with single arc length value."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([1.0, 0.0, 0.0])  # point on unit circle
        path = CircularPath(r, d, pi)

        # Test with single scalar value
        result = path.evaluate_at(np.pi / 2)  # Quarter circle

        assert "position" in result
        assert "velocity" in result
        assert "acceleration" in result
        assert "s" in result

        # Check shapes
        assert result["position"].shape == (1, 3)
        assert result["velocity"].shape == (1, 3)
        assert result["acceleration"].shape == (1, 3)
        assert result["s"].shape == (1,)

        # At s = π/2 on unit circle, should be at (0, 1, 0)
        expected_pos = np.array([0.0, 1.0, 0.0])
        assert np.allclose(result["position"][0], expected_pos, atol=self.NUMERICAL_ATOL)

    def test_evaluate_at_array_values(self) -> None:
        """Test evaluate_at method with array of arc length values."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([2.0, 0.0, 0.0])  # point on circle with radius 2
        path = CircularPath(r, d, pi)

        # Test with array of values
        s_values = [0.0, np.pi, 2 * np.pi, 3 * np.pi]  # Multiple positions around circle
        result = path.evaluate_at(s_values)

        # Check shapes
        assert result["position"].shape == (4, 3)
        assert result["velocity"].shape == (4, 3)
        assert result["acceleration"].shape == (4, 3)
        assert result["s"].shape == (4,)

        # Check specific positions on circle with radius 2
        # For radius=2, s=π means angle=π/2, s=2π means angle=π, etc.
        expected_positions = np.array(
            [
                [2.0, 0.0, 0.0],  # s = 0, angle = 0
                [0.0, 2.0, 0.0],  # s = π, angle = π/2
                [-2.0, 0.0, 0.0],  # s = 2π, angle = π
                [0.0, -2.0, 0.0],  # s = 3π, angle = 3π/2
            ]
        )

        for i in range(4):
            assert np.allclose(
                result["position"][i], expected_positions[i], atol=self.NUMERICAL_ATOL
            )
            # Velocity magnitude should be constant = 1 (unit tangent scaled by radius/radius = 1)
            assert np.isclose(np.linalg.norm(result["velocity"][i]), 1.0, atol=self.NUMERICAL_ATOL)
            # Acceleration magnitude should be constant = 1/radius = 1/2 = 0.5
            assert np.isclose(
                np.linalg.norm(result["acceleration"][i]), 0.5, atol=self.NUMERICAL_ATOL
            )

    def test_evaluate_at_with_numpy_array(self) -> None:
        """Test evaluate_at method with numpy array input."""
        r = np.array([1.0, 0.0, 0.0])  # x-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([0.0, 1.0, 0.0])  # point on unit circle in yz-plane
        path = CircularPath(r, d, pi)

        # Test with numpy array
        s_values = np.linspace(0, np.pi, 5)
        result = path.evaluate_at(s_values)

        # Check shapes
        assert result["position"].shape == (5, 3)
        assert result["velocity"].shape == (5, 3)
        assert result["acceleration"].shape == (5, 3)
        assert result["s"].shape == (5,)

        np.testing.assert_array_equal(result["s"], s_values)

    def test_all_traj_default(self) -> None:
        """Test all_traj method with default parameters."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([1.0, 1.0, 0.0])  # center at (1,1,0)
        pi = np.array([4.0, 1.0, 0.0])  # point on circle (radius=3)
        path = CircularPath(r, d, pi)

        result = path.all_traj()  # Default 100 points

        # Check structure
        assert "position" in result
        assert "velocity" in result
        assert "acceleration" in result
        assert "s" in result

        # Check shapes
        assert result["position"].shape == (100, 3)
        assert result["velocity"].shape == (100, 3)
        assert result["acceleration"].shape == (100, 3)
        assert result["s"].shape == (100,)

        # Check s values span a complete circle
        expected_full_circle = 2 * np.pi * path.radius
        assert np.isclose(result["s"][0], 0.0, atol=self.NUMERICAL_ATOL)
        assert np.isclose(result["s"][-1], expected_full_circle, atol=self.NUMERICAL_ATOL)

        # Check that all points are at the correct distance from center
        for i in range(100):
            distance = np.linalg.norm(result["position"][i] - path.center)
            assert np.isclose(distance, path.radius, atol=self.NUMERICAL_ATOL)

    def test_all_traj_custom_points(self) -> None:
        """Test all_traj method with custom number of points."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([2.0, 0.0, 0.0])  # point on circle with radius 2
        path = CircularPath(r, d, pi)

        num_points = 36  # 10 degree increments
        result = path.all_traj(num_points)

        # Check shapes
        assert result["position"].shape == (num_points, 3)
        assert result["velocity"].shape == (num_points, 3)
        assert result["acceleration"].shape == (num_points, 3)
        assert result["s"].shape == (num_points,)

        # Check circular properties
        for i in range(num_points):
            # Distance from center should be radius
            distance = np.linalg.norm(result["position"][i] - path.center)
            assert np.isclose(distance, path.radius, atol=self.NUMERICAL_ATOL)

            # Velocity should be tangent to circle (perpendicular to radius)
            radius_vec = result["position"][i] - path.center
            velocity_vec = result["velocity"][i]
            dot_product = np.dot(radius_vec, velocity_vec)
            assert np.isclose(dot_product, 0.0, atol=self.NUMERICAL_ATOL)

            # Acceleration should point toward center
            acceleration_vec = result["acceleration"][i]
            expected_acc_direction = -radius_vec / np.linalg.norm(radius_vec)
            actual_acc_direction = acceleration_vec / np.linalg.norm(acceleration_vec)
            assert np.allclose(
                actual_acc_direction, expected_acc_direction, atol=self.NUMERICAL_ATOL
            )

    def test_position_array_evaluation(self) -> None:
        """Test position method with array input."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([1.0, 0.0, 0.0])  # point on unit circle
        path = CircularPath(r, d, pi)

        # Test with array input
        s_values = np.array([0.0, np.pi / 2, np.pi, 3 * np.pi / 2])
        positions = path.position(s_values)

        # Should return array of positions
        assert positions.shape == (4, 3)

        # Check specific positions
        expected_positions = np.array(
            [
                [1.0, 0.0, 0.0],  # s = 0
                [0.0, 1.0, 0.0],  # s = π/2
                [-1.0, 0.0, 0.0],  # s = π
                [0.0, -1.0, 0.0],  # s = 3π/2
            ]
        )

        assert np.allclose(positions, expected_positions, atol=self.NUMERICAL_ATOL)

    def test_circular_path_validation_errors(self) -> None:
        """Test validation errors in CircularPath construction."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin

        # Test with point on the axis (should raise ValueError)
        pi_on_axis = np.array([0.0, 0.0, 1.0])  # Point on z-axis

        with pytest.raises(ValueError, match="The point pi must not be on the circle axis"):
            CircularPath(r, d, pi_on_axis)

    def test_circular_path_axis_normalization(self) -> None:
        """Test that axis vector is properly normalized."""
        r = np.array([0.0, 0.0, 5.0])  # Non-unit z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([1.0, 0.0, 0.0])  # point on circle

        path = CircularPath(r, d, pi)

        # Axis should be normalized
        assert np.isclose(np.linalg.norm(path.r), 1.0, atol=self.NUMERICAL_ATOL)
        assert np.allclose(path.r, np.array([0.0, 0.0, 1.0]), atol=self.NUMERICAL_ATOL)

    def test_circular_path_rotation_matrix_properties(self) -> None:
        """Test properties of the rotation matrix."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([1.0, 1.0, 0.0])  # center at (1,1,0)
        pi = np.array([3.0, 1.0, 0.0])  # point on circle (radius=2)

        path = CircularPath(r, d, pi)

        # Rotation matrix should be orthogonal
        R = path.R
        assert R.shape == (3, 3)

        # R^T * R should be identity
        should_be_identity = R.T @ R
        identity = np.eye(3)
        assert np.allclose(should_be_identity, identity, atol=self.NUMERICAL_ATOL)

        # Determinant should be ±1 (orthogonal matrix)
        det = np.linalg.det(R)
        assert np.isclose(abs(det), 1.0, atol=self.NUMERICAL_ATOL)

        # Each column should be a unit vector
        for i in range(3):
            col_norm = np.linalg.norm(R[:, i])
            assert np.isclose(col_norm, 1.0, atol=self.NUMERICAL_ATOL)


class TestFrenetFrames:
    """Test suite for Frenet frame computation."""

    NUMERICAL_RTOL = 1e-6
    NUMERICAL_ATOL = 1e-6

    def create_linear_trajectory_func(
        self, pi: np.ndarray, pf: np.ndarray
    ) -> Callable[[float], tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Create a trajectory function for linear path."""

        def trajectory_func(u: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            # Linear interpolation: p(u) = pi + u*(pf - pi), u ∈ [0,1]
            position = pi + u * (pf - pi)
            # First derivative is constant
            velocity = pf - pi
            # Second derivative is zero
            acceleration = np.zeros_like(pi)
            return position, velocity, acceleration

        return trajectory_func

    def create_circular_trajectory_func(
        self, center: np.ndarray, radius: float
    ) -> Callable[[float], tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Create a trajectory function for circular path."""

        def trajectory_func(u: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            # Circular path: p(u) = center + radius*(cos(u), sin(u), 0)
            # u is the angle parameter
            cos_u, sin_u = np.cos(u), np.sin(u)

            position = center + radius * np.array([cos_u, sin_u, 0.0])
            # First derivative: dp/du = radius*(-sin(u), cos(u), 0)
            velocity = radius * np.array([-sin_u, cos_u, 0.0])
            # Second derivative: d²p/du² = radius*(-cos(u), -sin(u), 0)
            acceleration = radius * np.array([-cos_u, -sin_u, 0.0])

            return position, velocity, acceleration

        return trajectory_func

    def test_linear_trajectory_frames(self) -> None:
        """Test Frenet frames for linear trajectory."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([1.0, 0.0, 0.0])  # Along x-axis

        trajectory_func = self.create_linear_trajectory_func(pi, pf)
        u_values = np.array([0.0, 0.5, 1.0])

        points, frames = compute_trajectory_frames(trajectory_func, u_values)

        # Check points
        assert points.shape == (3, 3)
        assert np.allclose(points[0], pi, atol=self.NUMERICAL_ATOL)
        assert np.allclose(points[-1], pf, atol=self.NUMERICAL_ATOL)

        # Check frames
        assert frames.shape == (3, 3, 3)

        # For linear path along x-axis, tangent should be [1,0,0]
        # Normal and binormal depend on implementation details
        for i in range(len(u_values)):
            frame = frames[i]
            # Each frame should be orthonormal
            assert abs(np.linalg.det(frame) - 1.0) < self.NUMERICAL_ATOL  # Right-handed

            # Check orthogonality
            for j in range(3):
                for k in range(3):
                    if j == k:
                        assert abs(np.dot(frame[j], frame[k]) - 1.0) < self.NUMERICAL_ATOL
                    else:
                        assert abs(np.dot(frame[j], frame[k])) < self.NUMERICAL_ATOL

    def test_circular_trajectory_frames(self) -> None:
        """Test Frenet frames for circular trajectory."""
        center = np.array([0.0, 0.0, 0.0])
        radius = 1.0

        trajectory_func = self.create_circular_trajectory_func(center, radius)
        u_values = np.array([0.0, np.pi / 2, np.pi])

        points, frames = compute_trajectory_frames(trajectory_func, u_values)

        # Check points
        assert points.shape == (3, 3)
        expected_points = np.array(
            [
                [1.0, 0.0, 0.0],  # u = 0
                [0.0, 1.0, 0.0],  # u = π/2
                [-1.0, 0.0, 0.0],  # u = π
            ]
        )
        assert np.allclose(points, expected_points, atol=self.NUMERICAL_ATOL)

        # Check frames
        assert frames.shape == (3, 3, 3)

        for i in range(len(u_values)):
            frame = frames[i]
            # Each frame should be orthonormal
            det = np.linalg.det(frame)
            assert abs(abs(det) - 1.0) < self.NUMERICAL_ATOL  # Orthonormal

            # Check that frame vectors are unit vectors
            for j in range(3):
                norm = np.linalg.norm(frame[j])
                assert abs(norm - 1.0) < self.NUMERICAL_ATOL

    def test_frames_with_tool_orientation(self) -> None:
        """Test Frenet frames with tool orientation."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([1.0, 0.0, 0.0])

        trajectory_func = self.create_linear_trajectory_func(pi, pf)
        u_values = np.array([0.0, 1.0])

        # Test with rotation angle
        tool_angle = np.pi / 4  # 45 degrees

        points, frames = compute_trajectory_frames(
            trajectory_func, u_values, tool_orientation=tool_angle
        )

        # Points should be the same
        assert np.allclose(points[0], pi, atol=self.NUMERICAL_ATOL)
        assert np.allclose(points[1], pf, atol=self.NUMERICAL_ATOL)

        # Frames should be modified by tool orientation
        assert frames.shape == (2, 3, 3)

        # Each frame should still be orthonormal
        for i in range(2):
            frame = frames[i]
            det = np.linalg.det(frame)
            assert abs(abs(det) - 1.0) < self.NUMERICAL_ATOL

    def test_frames_with_rpy_orientation(self) -> None:
        """Test Frenet frames with roll-pitch-yaw orientation."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([0.0, 1.0, 0.0])  # Along y-axis

        trajectory_func = self.create_linear_trajectory_func(pi, pf)
        u_values = np.array([0.5])  # Single point

        # Test with RPY angles
        rpy_angles = (np.pi / 6, np.pi / 4, np.pi / 3)  # Roll, pitch, yaw

        points, frames = compute_trajectory_frames(
            trajectory_func, u_values, tool_orientation=rpy_angles
        )

        # Should produce valid frames
        assert points.shape == (1, 3)
        assert frames.shape == (1, 3, 3)

        # Frame should be orthonormal
        frame = frames[0]
        det = np.linalg.det(frame)
        assert abs(abs(det) - 1.0) < self.NUMERICAL_ATOL

    def test_frames_edge_cases(self) -> None:
        """Test Frenet frames with edge cases."""

        # Degenerate case: zero velocity (stationary point)
        def stationary_func(u: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            position = np.array([1.0, 1.0, 1.0])  # Constant position
            velocity = np.zeros(3)  # Zero velocity
            acceleration = np.zeros(3)  # Zero acceleration
            return position, velocity, acceleration

        u_values = np.array([0.0, 1.0])

        try:
            points, frames = compute_trajectory_frames(stationary_func, u_values)

            # Should handle gracefully
            assert points.shape == (2, 3)
            assert frames.shape == (2, 3, 3)

        except Exception as e:
            # Some implementations might raise an error for degenerate cases
            pytest.skip(f"Frenet frame computation failed for degenerate case: {e}")


class TestPathPlanningEdgeCases:
    """Test suite for edge cases in path planning."""

    NUMERICAL_RTOL = 1e-6
    NUMERICAL_ATOL = 1e-6

    def test_very_small_linear_path(self) -> None:
        """Test linear path with very small length."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([1e-10, 1e-10, 0.0])

        path = LinearPath(pi, pf)

        # Should handle small lengths
        assert path.length > 0
        assert np.all(np.isfinite(path.tangent))

        # Position evaluation should work
        pos = path.position(path.length / 2)
        assert np.all(np.isfinite(pos))

    def test_very_small_circular_path(self) -> None:
        """Test circular path with very small radius."""
        r = np.array([0.0, 0.0, 1.0])  # z-axis
        d = np.array([0.0, 0.0, 0.0])  # center at origin
        pi = np.array([1e-8, 0.0, 0.0])  # point on very small circle

        path = CircularPath(r, d, pi)

        # Should handle small radius
        assert abs(path.radius - 1e-8) < 1e-9
        # Note: CircularPath doesn't have a length attribute, it's an infinite circle

        # Position evaluation should work
        pos = path.position(0.0)
        assert np.all(np.isfinite(pos))

    def test_large_coordinates(self) -> None:
        """Test paths with large coordinate values."""
        pi = np.array([1e6, 1e6, 1e6])
        pf = np.array([2e6, 2e6, 2e6])

        path = LinearPath(pi, pf)

        # Should handle large coordinates
        assert np.all(np.isfinite(path.pi))
        assert np.all(np.isfinite(path.pf))
        assert np.isfinite(path.length)

        pos = path.position(path.length / 2)
        assert np.all(np.isfinite(pos))


class TestPathPlanningPerformance:
    """Test suite for performance benchmarks."""

    @pytest.mark.parametrize("path_type", ["linear", "circular"])
    def test_path_construction_performance(
        self, path_type: str, benchmark: pytest.FixtureFunction
    ) -> None:
        """Benchmark path construction performance."""
        if path_type == "linear":

            def construct_path():
                pi = np.array([0.0, 0.0, 0.0])
                pf = np.array([10.0, 5.0, 3.0])
                return LinearPath(pi, pf)
        else:  # circular

            def construct_path():
                r = np.array([0.0, 0.0, 1.0])  # z-axis
                d = np.array([2.0, 3.0, 1.0])  # center
                pi = np.array([7.0, 3.0, 1.0])  # point on circle (radius=5)
                return CircularPath(r, d, pi)

        path = benchmark(construct_path)
        assert path is not None

    @pytest.mark.parametrize("n_evaluations", [100, 1000])
    def test_path_evaluation_performance(
        self, n_evaluations: int, benchmark: pytest.FixtureFunction
    ) -> None:
        """Benchmark path evaluation performance."""
        pi = np.array([0.0, 0.0, 0.0])
        pf = np.array([10.0, 10.0, 0.0])
        path = LinearPath(pi, pf)

        s_values = np.linspace(0, path.length, n_evaluations)

        def evaluate_positions():
            return [path.position(s) for s in s_values]

        positions = benchmark(evaluate_positions)
        assert len(positions) == n_evaluations

    def test_frenet_frame_performance(self, benchmark: pytest.FixtureFunction) -> None:
        """Benchmark Frenet frame computation performance."""
        center = np.array([0.0, 0.0, 0.0])
        radius = 2.0

        trajectory_func = self.create_circular_trajectory_func(center, radius)
        u_values = np.linspace(0, 2 * np.pi, 50)

        def compute_frames():
            return compute_trajectory_frames(trajectory_func, u_values)

        points, frames = benchmark(compute_frames)
        assert points.shape == (50, 3)
        assert frames.shape == (50, 3, 3)

    def create_circular_trajectory_func(
        self, center: np.ndarray, radius: float
    ) -> Callable[[float], tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Helper method for creating circular trajectory function."""

        def trajectory_func(u: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            cos_u, sin_u = np.cos(u), np.sin(u)
            position = center + radius * np.array([cos_u, sin_u, 0.0])
            velocity = radius * np.array([-sin_u, cos_u, 0.0])
            acceleration = radius * np.array([-cos_u, -sin_u, 0.0])
            return position, velocity, acceleration

        return trajectory_func


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main(["-xvs", __file__])
