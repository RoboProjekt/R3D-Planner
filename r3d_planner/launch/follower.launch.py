# =============================================================================
# R3D-Planner
#
# Author:        Bastian Aumer
# Last modified: 2026-09-16
# Repository:    https://github.com/RoboProjekt/R3D-Planner
#
# Copyright (c) Bastian Aumer
# =============================================================================

"""Explicit motion-producing launch; deliberately not included in planner launch."""
from r3d_planner.launching import description


def generate_launch_description():
    return description('follower')
