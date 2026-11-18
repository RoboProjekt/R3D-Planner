// Copyright 2026 Bastian Aumer
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// SPDX-FileCopyrightText: 2026 Bastian Aumer
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <array>
#include <cmath>

namespace r3d
{
struct GaitState
{
  int mode = 0;
  int gait = 0;
  unsigned error = 0;
  std::array<float, 3> velocity{};
  float yaw_speed = 0;
};

inline bool stationary(const GaitState & state)
{
  double squared_speed = 0;
  for (const auto value : state.velocity) {
    if (!std::isfinite(value)) {
      return false;
    }
    squared_speed += value * value;
  }
  return std::isfinite(state.yaw_speed) && squared_speed <= 0.02 * 0.02 &&
         std::abs(state.yaw_speed) <= 0.03;
}

inline bool ready(const GaitState & state, int gait = -1)
{
  return state.error == 0 && stationary(state) && state.mode == 1 &&
         (gait < 0 || state.gait == gait);
}
}  // namespace r3d

