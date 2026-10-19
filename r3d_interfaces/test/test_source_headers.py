# Copyright 2026 Bastian Aumer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-FileCopyrightText: 2026 Bastian Aumer
# SPDX-License-Identifier: Apache-2.0

"""Check own non-Python interface sources omitted by generic copyright discovery."""
from pathlib import Path

import pytest


@pytest.mark.parametrize('filename', ['CMakeLists.txt', 'msg/PathWithMetadata.msg'])
def test_own_source_license_header(filename):
    source = Path(__file__).resolve().parents[1] / filename
    text = source.read_text()
    assert '# Copyright 2026 Bastian Aumer' in text
    assert '# SPDX-FileCopyrightText: 2026 Bastian Aumer' in text
    assert '# SPDX-License-Identifier: Apache-2.0' in text
    assert '# Licensed under the Apache License, Version 2.0' in text
