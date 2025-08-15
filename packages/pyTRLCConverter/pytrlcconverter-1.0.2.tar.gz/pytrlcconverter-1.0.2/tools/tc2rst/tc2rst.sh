#!/bin/bash

# pyTRLCConverter - A tool to convert TRLC files to specific formats.
# Copyright (c) 2024 - 2025 NewTec GmbH
#
# This file is part of pyTRLCConverter program.
#
# The pyTRLCConverter program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# The pyTRLCConverter program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with pyTRLCConverter.
# If not, see <https://www.gnu.org/licenses/>.

cd ../plantuml
chmod +x get_plantuml.sh
. ./get_plantuml.sh
cd ../tc2rst

if [ ! -d "out" ]; then
    mkdir out
else
    rm -rf "out"/*
fi

# ****************************************************************************************************
# Software Tests
# ****************************************************************************************************
SW_TEST_OUT_FORMAT="rst"
SW_TEST_OUT_DIR="./out/sw-tests/$SW_TEST_OUT_FORMAT"
SW_TEST_CONVERTER="../ProjectConverter/tc2rst"
TRANSLATION=../ProjectConverter/translation.json

if [ ! -d "$SW_TEST_OUT_DIR" ]; then
    mkdir -p "$SW_TEST_OUT_DIR"
fi

echo "Generate software test cases ..."
pyTRLCConverter --source=../../trlc/swe-req --source=../../trlc/swe-test --exclude=../../trlc/swe-req --source=../../trlc/model -o="$SW_TEST_OUT_DIR" --verbose --project="$SW_TEST_CONVERTER" --translation="$TRANSLATION" "$SW_TEST_OUT_FORMAT"
