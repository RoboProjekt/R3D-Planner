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

#include "gait_guard.hpp"

#include <unitree/robot/channel/channel_subscriber.hpp>
#include <unitree/robot/go2/sport/sport_client.hpp>
#include <unitree/idl/go2/SportModeState_.hpp>

#include <chrono>
#include <functional>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>

using SteadyClock = std::chrono::steady_clock;

class Telemetry
{
public:
  void receive(const void * message)
  {
    const auto & data = *static_cast<const unitree_go::msg::dds_::SportModeState_ *>(message);
    std::lock_guard<std::mutex> lock(mutex_);
    state_ = {data.mode(), data.gait_type(), data.error_code(), data.velocity(), data.yaw_speed()};
    received_ = SteadyClock::now();
    ++sequence_;
  }

  bool wait(const std::function<bool(const r3d::GaitState &)> & condition,
            r3d::GaitState & result, double stable_seconds)
  {
    const auto start = SteadyClock::now();
    auto stable_since = start;
    bool stable = false;
    while (SteadyClock::now() - start < std::chrono::seconds(4)) {
      const auto now = SteadyClock::now();
      bool good = false;
      {
        std::lock_guard<std::mutex> lock(mutex_);
        result = state_;
        good = sequence_ >= 2 && now - received_ <= std::chrono::milliseconds(200) &&
               condition(state_);
      }
      if (!good) {
        stable = false;
      } else if (!stable) {
        stable_since = now;
        stable = true;
      } else if (std::chrono::duration<double>(now - stable_since).count() >= stable_seconds) {
        return true;
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    std::cerr << "Telemetry condition failed: mode=" << result.mode << " gait=" << result.gait
              << " error=" << result.error << '\n';
    return false;
  }

private:
  std::mutex mutex_;
  r3d::GaitState state_;
  SteadyClock::time_point received_{};
  unsigned sequence_ = 0;
};

int main(int argc, char ** argv)
{
  if (argc != 3) {
    std::cerr << "Usage: r3d_go2w_gait_guard INTERFACE prepare|verify_normal|verify_stairs\n";
    return 2;
  }
  const std::string operation(argv[2]);
  if (operation != "prepare" && operation != "verify_normal" && operation != "verify_stairs") {
    return 2;
  }
  try {
    unitree::robot::ChannelFactory::Instance()->Init(0, argv[1]);
    Telemetry telemetry;
    unitree::robot::ChannelSubscriber<unitree_go::msg::dds_::SportModeState_> subscriber(
      "rt/lf/sportmodestate");
    subscriber.InitChannel([&telemetry](const void * data) {telemetry.receive(data);}, 1);
    r3d::GaitState state;
    if (operation == "prepare") {
      const auto stopped = [](const r3d::GaitState & value) {
          return value.error == 0 && r3d::stationary(value);
        };
      if (!telemetry.wait(stopped, state, 0.5)) {
        return 1;
      }
      if (state.mode != 1) {
        unitree::robot::go2::SportClient client;
        client.SetTimeout(3.0f);
        client.Init();
        const auto code = client.BalanceStand();
        if (code != 0) {
          std::cerr << "BalanceStand failed: " << code << '\n';
          return 1;
        }
      }
      return telemetry.wait([](const r3d::GaitState & value) {return r3d::ready(value);},
                            state, 0.3) ? 0 : 1;
    }
    const int target = operation == "verify_stairs" ? 1 : 0;
    return telemetry.wait([target](const r3d::GaitState & value) {return r3d::ready(value, target);},
                          state, 0.3) ? 0 : 1;
  } catch (const std::exception & error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}

