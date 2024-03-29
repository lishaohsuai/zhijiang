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
from utils.cache_io import CacheIO
from utils.path_utils import get_file_path
from .image_read import image_read
from backend.api.utils import get_api_params
import base64


def image_meta_provider(file_path):
    # read from cache
    res = CacheIO(file_path).get_cache()
    if res:
        image_meta_data = image_read(data=res) \
            .get_meta_data()
        return image_meta_data
    else:
        raise ValueError('Parameter error, no data found')


def image_provider(file_path, step):
    res = CacheIO(file_path).get_cache()
    if res:
        return image_read(data=res, step=step) \
            .get_data()
    else:
        raise ValueError('Parameter error, no data found')


def get_image_meta_data(request):
    params = ['uid', 'trainJobName', 'run', 'tag']
    uid, trainJobName, run, tag = get_api_params(request, params)

    file_path = get_file_path(uid, run, 'image', tag)
    data = image_meta_provider(file_path)
    return {tag: data}


def get_image_data(request):
    params = ['uid', 'trainJobName', 'run', 'tag', 'step']
    uid, trainJobName, run, tag, step = get_api_params(request, params)
    file_path = get_file_path(uid, run, 'image', tag)
    data = base64.b64encode(image_provider(file_path, step=int(step)))
    res = "data:image/png;base64,%s" % data.decode()
    if data:
        return res
    else:
        raise ValueError('No such data')

