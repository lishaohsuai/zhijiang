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
import threading
import time
from io import BytesIO
from pathlib import Path
from tbparser import SummaryReader
from tbparser import Projector_Reader
from utils.cache_io import CacheIO
from utils.path_utils import path_parser
from utils.redis_utils import RedisInstance
import pickle


class Trace_Thread(threading.Thread):
    def __init__(self, runname, filename, current_size, uid, cache_path):
        threading.Thread.__init__(self, name=filename.name)
        self.uid = uid
        self.runname = runname
        self.cache_path = cache_path
        self.filename = filename
        self.current_size = current_size
        self.r = RedisInstance
        # 该日志中是否有超参数
        self.has_hparams = False
        self.first_write = False
        self.metrics = []
        # 是否完成初始化
        self._finish_init = 0
        self.redis_tag = []

    def run(self):
        print('监听文件 %s' % self.filename)
        self.trace(self.current_size)

    def trace(self, current_size):
        filename = Path(self.filename)
        if filename.suffix == ".json":
            self.load_model_file(filename)
            self.finish_init = 1
            return
        f = open(filename, "rb")
        # for event file
        if "event" in filename.name:
            _io = BytesIO(
                f.read(current_size)
            )
            self.load_event_file(_io)
            # 设置初始化完成标志
            self.finish_init = 1
            while True:
                rest = f.read()
                if not rest:
                    time.sleep(2)
                    continue
                _io = BytesIO(rest)
                self.load_event_file(_io)
        # for projector file
        elif "projector" in filename.name:
            self.load_projector_file(f)
            # 设置初始化完成标志
            self.finish_init = 1

    @property
    def finish_init(self):
        return self._finish_init

    # 设置标志
    @finish_init.setter
    def finish_init(self, is_finish):
        self.r.set("{}_{}_{}_is_finish".format(self.uid, self.runname,
                                               self.filename.name), 1)
        print(self.name + " is finish")
        self._finish_init = is_finish

    def set_redis_key(self, type, tag, file_path):
        _key = self.uid + '_' + self.runname + '_' + type + '_' + tag
        if _key in self.redis_tag:
            pass
        else:
            self.r.set(_key, str(file_path))
            self.redis_tag.append(_key)

    def set_cache(self, file_name, data):
        if not file_name.parent.exists():
            file_name.parent.mkdir(parents=True, exist_ok=True)
        with open(file_name, 'ab') as f:
            pickle.dump(data, f)
            f.close()

    def load_event_file(self, fileIO):
        reader = SummaryReader(fileIO, types=[
            'scalar',
            'graph',
            'hist',
            'text',
            'image',
            'audio',
            'hparams'
        ])
        for items in reader:
            if items.type == "graph":
                file_path = path_parser(self.cache_path, self.runname,
                                        items.type, tag='c_graph')
                CacheIO(file_path).set_cache(data=items.value)
                self.set_redis_key(items.type, tag='c_graph',
                                   file_path=file_path)
                continue
            elif items.type == "hparams":
                file_path = path_parser(self.cache_path, self.runname,
                                        type='hyperparm',
                                        tag='hparams')
                self.set_cache(file_name=file_path, data=items.value)
                self.set_redis_key(type='hyperparm',
                                   tag='hparams',
                                   file_path=file_path)
                continue

            item_data = {
                'step': items.step,
                'wall_time': items.wall_time,
                'value': items.value,
                'type': items.type
            }
            file_path = path_parser(self.cache_path, self.runname,
                                    type=items.type,
                                    tag=items.tag)
            CacheIO(file_path).set_cache(data=item_data)
            self.set_redis_key(type=items.type, tag=items.tag,
                               file_path=file_path)

    def load_projector_file(self, fileIO):
        p_reader = Projector_Reader(fileIO).read()
        for items in p_reader.projectors:
            item_data = {
                'step': items.step,
                'wall_time': items.wall_time,
                'value': items.value.reshape(items.value.shape[0], -1)
                if items.value.ndim > 2 else items.value,
                'label': items.label,
            }
            file_path = path_parser(self.cache_path, self.runname,
                                    type=p_reader.metadata.type,
                                    tag=items.tag)
            CacheIO(file_path).set_cache(data=item_data)
            self.set_redis_key(type=p_reader.metadata.type, tag=items.tag,
                               file_path=file_path)
        if p_reader.sample:
            file_path = path_parser(self.cache_path, self.runname,
                                    type="embedding",
                                    tag="sample_" + items.tag)
            CacheIO(file_path).set_cache(data=p_reader.sample)
            self.set_redis_key(type="embedding", tag="sample_" + items.tag,
                               file_path=file_path)

    def load_model_file(self, file):
        with open(file, "r") as f:
            _content = f.read()
            file_path = path_parser(self.cache_path, self.runname,
                                    type="graph",
                                    tag="s_graph")
            CacheIO(file_path).set_cache(data=_content)
            self.set_redis_key(type="graph", tag="s_graph",
                               file_path=file_path)
