"""Geometry utilities for polygonal motif generation (numpy-free)."""

from __future__ import annotations

import math
from functools import lru_cache
from typing import List, Tuple

from .tensor_mapper import HLSFState


def canonical_start_angle(sides: int) -> float:
    """Return the canonical starting angle for a regular polygon.

    Odd-sided polygons are oriented point-up (pi/2) while even-sided polygons
    start flat on the x-axis (0)."""

    return math.pi / 2 if (sides % 2) else 0.0


def total_replications(sides: int, levels: int) -> int:
    """Total triangle replications across levels (geometric series)."""

    if levels <= 0:
        return 0
    if sides == 1:
        return levels
    return (sides * (sides**levels - 1)) // (sides - 1)


def build_base_triangles(
    vertices: List[Tuple[float, float]], sides: int
) -> List[List[Tuple[float, float]]]:
    """Build the base-level triangle motifs.

    ``vertices`` should contain the polygon vertices ordered around the center.
    The function mirrors the 'base rays' logic used by the original prototype.
    """

    tris: List[List[Tuple[float, float]]] = []
    limit = (sides // 2 + 2) if (sides % 2) else (sides // 2 + 1)
    i = 0
    for j in range(1, limit):
        a = vertices[i]
        b = vertices[(i + j) % sides]
        c = vertices[(i + j - 1) % sides]
        tris.append([a, b, c])
    return tris


def rotate_batched(
    verts: List[List[Tuple[float, float]]],
    center: Tuple[float, float],
    theta_deg: float,
) -> List[List[Tuple[float, float]]]:
    """Rotate a batch of triangles about ``center`` by ``theta_deg`` degrees."""

    theta = math.radians(theta_deg)
    ct, st = math.cos(theta), math.sin(theta)
    cx, cy = center
    rotated: List[List[Tuple[float, float]]] = []
    for tri in verts:
        new_tri = []
        for x, y in tri:
            x0, y0 = x - cx, y - cy
            xr = x0 * ct - y0 * st + cx
            yr = x0 * st + y0 * ct + cy
            new_tri.append((xr, yr))
        rotated.append(new_tri)
    return rotated


def _bbox(tri: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in tri]
    ys = [p[1] for p in tri]
    return min(xs), max(xs), min(ys), max(ys)


def _overlap(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> bool:
    return not (a[1] < b[0] or a[0] > b[1] or a[3] < b[2] or a[2] > b[3])


def rotate_state(state: HLSFState, angle_deg: float) -> HLSFState:
    """Rotate all triangles in ``state`` and collapse overlapping ones."""

    if not state.triangles:
        return state

    xs = [p[0] for tri in state.triangles for p in tri]
    ys = [p[1] for tri in state.triangles for p in tri]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    rotated = rotate_batched(state.triangles, (cx, cy), angle_deg)

    tris: List[List[Tuple[float, float]]] = [list(map(list, tri)) for tri in rotated]
    cols = [list(col) for col in state.colors]

    i = 0
    while i < len(tris):
        j = i + 1
        bbox_i = _bbox(tris[i])
        while j < len(tris):
            bbox_j = _bbox(tris[j])
            if _overlap(bbox_i, bbox_j):
                tri = [
                    [
                        (p1[0] + p2[0]) / 2.0,
                        (p1[1] + p2[1]) / 2.0,
                    ]
                    for p1, p2 in zip(tris[i], tris[j])
                ]
                col = [
                    (c1 + c2) / 2.0
                    for c1, c2 in zip(cols[i], cols[j])
                ]
                tris[i] = tri
                cols[i] = col
                tris.pop(j)
                cols.pop(j)
                bbox_i = _bbox(tris[i])
            else:
                j += 1
        i += 1

    return HLSFState(
        triangles=[ [ [float(x), float(y)] for x,y in tri ] for tri in tris ],
        colors=[list(col) for col in cols],
        active_motif=state.active_motif,
        metrics=state.metrics,
        resonance_metrics=state.resonance_metrics,
        prototypes=state.prototypes,
        proof_log=state.proof_log,
    )


class HLSFGenerator:
    """Static helpers for hierarchical polygon geometry."""

    @staticmethod
    @lru_cache(maxsize=None)
    def multiplier(level: int, sides: int) -> float:
        return 2 ** (level - 2) if sides % 2 == 0 else 1.5 ** (level - 2)

    @staticmethod
    @lru_cache(maxsize=None)
    def _generate_vertices_impl(
        center: Tuple[float, float], radius: float, sides: int
    ) -> List[Tuple[float, float, float]]:
        angles = [2 * math.pi * i / sides for i in range(sides)]
        verts = []
        for angle in angles:
            x = center[0] + radius * math.sin(angle)
            y = center[1] + radius * math.cos(angle)
            verts.append((x, y, 0.0))
        return verts

    @staticmethod
    def generate_vertices(
        center: Tuple[float, float], radius: float, sides: int
    ) -> List[Tuple[float, float, float]]:
        if not isinstance(center, tuple):
            center = tuple(center)
        return HLSFGenerator._generate_vertices_impl(center, radius, sides)

    @staticmethod
    def midpoint(
        p1: Tuple[float, float, float], p2: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        return (
            (p1[0] + p2[0]) / 2,
            (p1[1] + p2[1]) / 2,
            (p1[2] + p2[2]) / 2,
        )

    @staticmethod
    def calculate_symmetry_point_adjusted(
        center: Tuple[float, float], radius: float, sides: int, level: int
    ) -> Tuple[float, float, float]:
        center3d = (center[0], center[1], 0.0)
        if level <= 1:
            return center3d

        cx, cy, cz = center3d
        off_x = off_y = off_z = 0.0
        for current_level in range(2, level + 1):
            scaling_factor = HLSFGenerator.multiplier(current_level, sides)
            current_adjustment = radius * scaling_factor
            verts = HLSFGenerator.generate_vertices(center, current_adjustment, sides)
            if sides % 2 == 1:
                mx, my, mz = HLSFGenerator.midpoint(verts[0], verts[1])
                current_offset = (mx - cx, my - cy, mz - cz)
            else:
                vx, vy, vz = verts[0]
                current_offset = (vx - cx, vy - cy, vz - cz)
            off_x += current_offset[0]
            off_y += current_offset[1]
            off_z += current_offset[2]
        return (cx + off_x, cy + off_y, cz + off_z)
