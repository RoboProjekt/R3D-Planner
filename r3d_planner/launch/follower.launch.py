"""Explicit motion-producing launch; deliberately not included in planner launch."""
from r3d_planner.launching import description


def generate_launch_description():
    return description('follower')
