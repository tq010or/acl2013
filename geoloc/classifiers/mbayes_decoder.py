#! /usr/bin/env python

"""
Multinominal Bayes decoder (supporting multicore processing)
"""

import os
import marshal
import math
import ujson as json


class decoder:
    def __init__(self, model_file):
        self.pred_num = 10
        self.grid_size = 0.5
        if os.path.exists(model_file):
            self.priori_dict, self.posterior_dict, self.fea_set = marshal.load(open(model_file, "rb"))
            assert(self.fea_set)
            assert(self.priori_dict)
            assert(self.posterior_dict)
        else:
            print model_file
            raise IOError("Model is not generated yet ...") 

    def _predict_list(self, tokens):
        """    Predict tweet location into one of the predefined classes    """
        results = None
        tokens = [token for token in tokens if token in self.fea_set]
        try:
            preds = list()
            for c in self.priori_dict:
                # log linear add-up
                pred = math.log(self.priori_dict[c]) # priori
                pred += sum(math.log(self.posterior_dict[c][token]) for token in tokens if token in self.posterior_dict[c]) # seen feature in the class
                pred += sum(1 for token in tokens if token not in self.posterior_dict[c]) * math.log(self.posterior_dict[c][""]) # unseen feature smoothing
                preds.append((c, pred))
            s_preds = sorted(preds, key = lambda k:k[1], reverse=True) # sort by prediction confidence
            results = s_preds[0:self.pred_num]
        except TypeError:
            raise SystemExit("Please load model first.")
        return results[0][0]


    def _predict_dict(self, fea_dict):
        """    Predict tweet location into one of the predefined classes    """
        results = None
        for k in fea_dict.keys():
            if k not in self.fea_set:
                del fea_dict[k]
        try:
            preds = list()
            for c in self.priori_dict:
                pred = math.log(self.priori_dict[c]) # priori
                for k, v in fea_dict.items():
                    if k in self.posterior_dict[c]:
                        pred += math.log(self.posterior_dict[c][k]) * v
                    else:
                        pred += math.log(self.posterior_dict[c][""]) * v
                preds.append((c, pred))
            s_preds = sorted(preds, key = lambda k:k[1], reverse=True) # sort by prediction confidence
            results = s_preds[0:self.pred_num]
        except TypeError:
            raise SystemExit("Please load model first.")
        return results[0][0]


    def predict(self, data):
        """    Predict tweet location into one of the predefined classes    """
        if isinstance(data, list):
            return self._predict_list(data)
        elif isinstance(data, dict):
            return self._predict_dict(data)
        else:
            raise ValueError("Mal-formed internal data format")
