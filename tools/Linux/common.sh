#!/bin/bash
#
# Lara Maia <dev@lara.monster> 2015 ~ 2022
#
# The stlib is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The stlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

check_linux() {
    if ! grep -q "Linux" <<<"$(uname -s)"; then
        echo "Unsupported platform"
        exit 1
    fi
}

cd "$(dirname "$0")/../.." || exit 1

export PYTHON_VERSION RELEASE_NAME APP_VERSION
PYTHON_VERSION="$(python -c 'import sys;print(sys.implementation.cache_tag)')"
RELEASE_NAME="$(basename "$PWD")-LIN64-Python-$PYTHON_VERSION"
APP_VERSION="$(grep version= setup.py | cut -d\' -f2)"
