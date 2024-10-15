# generating-vehicular-icon-descriptions

Welcome! The repository holds data and code associated with our paper titled "Generating Vehicular Icon Descriptions and Indications Using Large Vision-Language Models" (ID: 267) at the [Industry Track of the EMNLP 2024 conference](https://2024.emnlp.org/program/industry/).

## Contents

This repository contains 4 sub-folders. Here is an overview:

- `clipscore` is a submodule, using the [jmhessel/clipscore](https://github.com/jmhessel/clipscore) repository by Jack Hessel. CLIPscore and RefCLIPscore are automated evaluation metrics. 

  ```git submodule update --init --recursive```

- `data` contains the all original/unprocessed data, such as icon images from the 42 vehicle manuals and crowdsourced icon descriptions.

- `outputs` contains model outputs (model-generated descriptions), ground truth (human-generated descriptions) and summary outputs from the human and automatic evaluations of those outputs.

  Copies of the icon images themselves are in the `icons` folder. Generated and ground truth descriptions can be found in the various `.json` files. `zero-shot.json` is probably the best place to start.

- `code` contains python code for running 3 LVLMs (GPT, Claude, LLaVA) on our dashboard icon dataset and for collecting and evaluating the results.
