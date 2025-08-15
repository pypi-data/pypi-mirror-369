# Bash script to create a virtual environment with PyHangouts2

# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>
# SPDX-License-Identifier: GPL-3.0-or-later

if [ -d "venv" ]; then
    rm -r venv
fi
python3 -m build
virtualenv venv
. venv/bin/activate
pip install ./dist/*.whl
