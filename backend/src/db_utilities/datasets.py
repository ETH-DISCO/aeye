import json
import os
import sys
from abc import ABC, abstractmethod

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, SequentialSampler
from torch.utils.data import Dataset as TorchDataset

from ..CONSTANTS import *


# COLLATE FUNCTIONS


def wikiart_collate_fn(batch):
    try:
        return {
            "images": {key: torch.cat([x["images"][key] if isinstance(x["images"][key], torch.Tensor)
                                       else torch.Tensor(np.array(x["images"][key])) for x in batch], dim=0).detach()
                       for key in batch[0]["images"].keys()},
            "index": [x["index"] for x in batch],
            "path": [x["path"] for x in batch],
            "width": [x["width"] for x in batch],
            "height": [x["height"] for x in batch],
            "genre": [x["genre"] for x in batch],
            "author": [x["author"] for x in batch],
            "title": [x["title"] for x in batch],
            "date": [x["date"] for x in batch]
        }
    except Exception as e:
        print(e.__str__())
        print("Error in collate_fn of best_artworks.")
        return


def best_artworks_collate_fn(batch):
    try:
        return {
            "images": {key: torch.cat([x["images"][key] if isinstance(x["images"][key], torch.Tensor)
                                       else torch.Tensor(np.array(x["images"][key])) for x in batch], dim=0).detach()
                       for key in batch[0]["images"].keys()},
            "index": [x["index"] for x in batch],
            "author": [x["author"] for x in batch],
            "path": [x["path"] for x in batch],
            "width": [x["width"] for x in batch],
            "height": [x["height"] for x in batch]
        }
    except Exception as e:
        print(e.__str__())
        print("Error in collate_fn of best_artworks.")
        return


def common_collate_fn(batch):
    try:
        return {
            "images": {key: torch.cat([x["images"][key] if isinstance(x["images"][key], torch.Tensor)
                                       else torch.Tensor(np.array(x["images"][key])) for x in batch], dim=0).detach()
                       for key in batch[0]["images"].keys()},
            "index": [x["index"] for x in batch],
            "path": [x["path"] for x in batch],
            "width": [x["width"] for x in batch],
            "height": [x["height"] for x in batch]
        }
    except Exception as e:
        print(e.__str__())
        print("Error in collate_fn of celebahq.")
        return


# SUPPORT DATASET FOR IMAGES

class SupportDatasetForImages(TorchDataset):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.file_list = []

        for file in os.listdir(root_dir):
            if not os.path.isdir(os.path.join(self.root_dir, file)) and "minimap.png" != file and "minimap.jpg" != file:
                self.file_list.append(file)

        self.transform = None

    def append_transform(self, transform):
        self.transform = transform

    def __len__(self):
        return len(self.file_list)


class SupportDatasetForImagesBestArtworks(SupportDatasetForImages):
    def __init__(self, root_dir):
        super().__init__(root_dir)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.file_list[idx])
        # Get image height and width
        image = Image.open(img_name)
        width, height = image.size
        if self.transform:
            image = self.transform(image)

        return {
            'images': image,
            'index': idx,
            'author': " ".join(self.file_list[idx].split("-")[1].removesuffix(".jpg").split("_")),
            'path': self.file_list[idx],
            'width': width,
            'height': height
        }


class SupportDatasetForImagesWikiArt(SupportDatasetForImages):
    def __init__(self, root_dir):
        super().__init__(root_dir)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.file_list[idx])
        # Get image height and width
        image = Image.open(img_name)
        width, height = image.size
        if self.transform:
            image = self.transform(image)

        # Create dictionary to return
        return_value = {
            'images': image,
            'index': idx,
            'path': self.file_list[idx],
            'width': width,
            'height': height,
            'genre': '',
            'author': '',
            'title': '',
            'date': -1,
        }

        # Get elements from filename. Remove initial number and extension, and split by "_"
        elements = self.file_list[idx].removesuffix(".jpg").split("_")[1:]
        if len(elements) > 0:
            return_value['genre'] = " ".join(elements[0].split("-"))
        if len(elements) > 1:
            # Get author and capitalize first letter of each word
            return_value['author'] = " ".join(elements[1].split("-")).capitalize()
        if len(elements) > 2:
            # If at the end there are 4 consecutive numbers, it is a date. Remove it from the title and assign it to
            # date
            title_elements = elements[2].split("-")
            if len(title_elements) > 0 and title_elements[-1].isdigit() and len(title_elements[-1]) == 4:
                return_value['date'] = int(title_elements[-1])
                title_elements = title_elements[:-1]

            # First, assign single s to previous word with "'s"
            for i in range(len(title_elements)):
                if title_elements[i] == "s" and i > 0:
                    title_elements[i - 1] = title_elements[i - 1] + "'s"

            # Then, assign single l to next word with "l'"
            for i in range(len(title_elements)):
                if title_elements[i] == "l" and i < len(title_elements) - 1:
                    title_elements[i + 1] = "l'" + title_elements[i + 1]

            # Remove all standalone "s" from the list
            title_elements = [x for x in title_elements if x != "s"]
            # Remove all standalone "l" from the list
            title_elements = [x for x in title_elements if x != "l"]
            # Capitalize first letter of each word
            return_value['title'] = " ".join(title_elements).capitalize()

        return return_value


class SupportDatasetForImagesCommon(SupportDatasetForImages):
    def __init__(self, root_dir):
        super().__init__(root_dir)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.file_list[idx])
        # Get image height and width
        image = Image.open(img_name)
        width, height = image.size
        if self.transform:
            image = self.transform(image)

        return {
            'images': image,
            'index': idx,
            'path': self.file_list[idx],
            'width': width,
            'height': height
        }


# DATASET ABSTRACT CLASS

class Dataset(ABC):
    def __init__(self, dataset, collate_fn):
        self.dataset = dataset
        self.collate_fn = collate_fn

    @abstractmethod
    def get_size(self):
        pass

    @abstractmethod
    def get_dataloader(self, batch_size, num_workers, data_processor):
        pass

    def __getitem__(self, idx):
        return self.dataset[idx]


# DATASET CLASSES


class LocalArtworksDataset(Dataset):
    def __init__(self, dataset: TorchDataset, collate_fn):
        super().__init__(dataset, collate_fn)

    def get_size(self):
        return len(self.dataset)

    def get_dataloader(self, batch_size, num_workers, data_processor):
        # Create sampler
        sampler = SequentialSampler(self.dataset)
        self.dataset.append_transform(data_processor)
        return DataLoader(self.dataset,
                          batch_size=batch_size,
                          num_workers=num_workers,
                          collate_fn=self.collate_fn,
                          sampler=sampler)


# FUNCTION FOR GETTING DATASET OBJECT

def get_dataset_object(dataset_name) -> Dataset:
    # Load datasets information from ../datasets.json
    dataset = None
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        content = json.load(f)
        for d in content["datasets"]:
            if d["name"] == dataset_name:
                dataset = d
                break

    if dataset is None:
        print("Dataset not found.")
        sys.exit(1)

    ds = globals()[dataset["dataset_class"]](os.path.join(os.getenv(HOME), dataset["dir_name"]))
    return LocalArtworksDataset(ds, globals()[dataset["collate_fn"]])
