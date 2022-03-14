from abc import ABC, abstractmethod
from collections import deque
from pdb import Pdb
import pdb
from tkinter import W
from typing import Union, List, Dict
import pandas as pd
from config import settings as st

def get_cache_capacities() -> List[int]:
    """
    Parses the parameter file and generates a list
    of the cache capacities of each player
    """
    param_type = st.CACHE_CAPACITY["type"]
    if param_type == "constant":
        quantity = st.CACHE_CAPACITY["quantity"]
        capacities = [quantity for _ in range(st.NUM_CLIENTS)]

    return capacities

class Policy(ABC):
    """
    Abstact class representing a general policy
    to be implemented in the administriation of a local cache
    """

    def __init__(self, client_id: int, columns: List[str]):

        self.client_id = client_id
        self.cache_capacity = get_cache_capacities()[client_id]
        self.cache = pd.DataFrame(columns=columns)

        self.most_recent_store_idx = []
        self.most_recent_drop_idx = []
        self.most_recent_share_dict = dict()

    def _compute_policy(self, new_sampels: pd.DataFrame):
        """"
        new samples dataframe example 
        |item_id|class|arrival_time|client_id|
        |-------|-----|------------|---------|
        |  27366|    3|           0|        0|
        |  23152|    4|           0|        0|
        |  59450|    0|           0|        0|
        """

    def _update_cache(self, new_samples: pd.DataFrame):
        
        self._compute_policy(new_samples)

        cache = self.cache
        self.old_cache = cache.copy()

        cache = cache.drop(self.most_recent_drop_idx)
        df_append = new_samples.loc[self.most_recent_store_idx]
        cache = pd.concat([cache, df_append], axis=0)

        # import pdb; pdb.set_trace()

        self.cache = cache


    def get_samples(self, new_samples: pd.DataFrame, fl_round: bool = False):

        self._update_cache(new_samples)
        if fl_round is True:
            train_samples = list(new_samples["item_id"].values) 
            if self.old_cache.shape[0] > 0:
                train_samples.extend(list(self.old_cache["item_id"].values))
        else:
            train_samples = list(self.cache["item_id"].values)

        train_samples = [int(x) for x in train_samples]

        return train_samples, self.most_recent_share_dict


