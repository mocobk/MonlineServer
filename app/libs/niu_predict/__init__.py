#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : mocobk
# @Email : mailmzb@qq.com
# @Time : 2021/4/24 12:00

import numpy as np
import pickle
from pathlib import Path


def load_model(model_file_path):
    with open(model_file_path, "rb") as fp:
        model = pickle.load(fp)
    return model


loaded_model = load_model(Path(__file__).parent.joinpath('model.dat'))


def get_predict(features: list):
    data_array = np.array([features])
    predict_value = loaded_model.predict(data_array)
    predict_proba_value = loaded_model.predict_proba(data_array)
    return predict_value.tolist()[0], predict_proba_value.tolist()[0]
