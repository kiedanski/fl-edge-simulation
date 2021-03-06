import flwr as fl
from pathlib import Path
import sys
import pytorch_lightning as pl
from collections import OrderedDict

from config import settings as st
from copy import deepcopy

import json
import torch
import numpy as np
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from torchvision.datasets import MNIST


from src.datasets.map import name_to_dataset
from src.models.map import name_to_model
from src.models.base import MetricsCallback
from src.path_utils import final_assignmnet_path, save_metrics


class FlowerClient(fl.client.NumPyClient):
    def __init__(self, model, data_loaders):
        self.model = model
        self.metrics_callback = MetricsCallback()

        self.data_loaders = data_loaders

    def get_parameters(self):
        return self.model.get_parameters()

    def fit(self, parameters, config):
        self.model.set_parameters(parameters)

        round = config["round"]

        train_loader = self.data_loaders[round]["train"]
        val_loader = self.data_loaders[round]["val"]
        L = len(train_loader.sampler)

        if L > 0:
            trainer = pl.Trainer(
                max_epochs=1,
                accelerator="auto",
                devices="auto",
                callbacks=[self.metrics_callback],
            )
            trainer.fit(self.model, train_loader)
            trainer.validate(self.model, dataloaders=val_loader)

            self.metrics_callback.persist_round(round)
            params = self.get_parameters()
        else:
            # params = [np.zeros_like(x) for x in self.get_parameters()]
            params = self.get_parameters()

        return params, L, {}

    def evaluate(self, parameters, config):
        pass


def start_client(client_id: str) -> None:
    # Model and data

    model = name_to_model[st.MODEL_NAME]

    assignment_path = final_assignmnet_path()
    with open(assignment_path, "r") as fh:
        assignment_order = json.load(fh)[client_id]

    data_loaders = name_to_dataset[st.DATASET_NAME].client_loader(
        assignment_order, batch_size=32
    )

    # Flower client
    client = FlowerClient(model, data_loaders)
    fl.client.start_numpy_client("0.0.0.0:8080", client)

    save_metrics(client.metrics_callback.metrics, f"client_{client_id}")


if __name__ == "__main__":
    id_ = sys.argv[1]
    start_client(id_)
