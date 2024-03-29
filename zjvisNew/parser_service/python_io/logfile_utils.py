# -*- coding: UTF-8 -*-
#  Copyright 2020 Zhejiang Lab. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  =============================================================
from pathlib import Path


def get_runinfo(logdir):
    p = Path(logdir)
    dirs = sorted(f for f in p.rglob('*') if f.is_dir())
    res = {}
    files = [f for f in p.glob('*')]
    if files:
        res['.'] = p.absolute()
    for dir in dirs:
        res[dir.name] = dir.absolute()
    return res


def is_available_flie(filename):
    filename = Path(filename)
    return True if filename.suffix == '.json' or "events" in filename.name\
                   or "projector" in filename.name else False
