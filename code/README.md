# dashboard-icons/code

`code` contains python code for running 3 LVLMs (GPT, Claude, LLaVA) on our dashboard icon dataset and for collecting and evaluating the results. The LLaVA model implementation uses the Ollama API, so it can be easily modified to test any other models. Several of the scripts contained in this folder reference files resident elsewhere:

- The original dataset of dashboard icon-specific pages from 42 vehicle manuals is contained in the `data` folder. 

- The `outputs` folder contains human- and model-generated descriptions based on those icon images and descriptions.

## What's in this folder?

There are 3 types of python scripts in this folder:

- Preprocessing scripts that extract data and clean raw data (e.g. original manual files, human-generated descriptions, etc.).

  `make-dataset.py`, `icons_preprocess-labels.ipynb`, `model.py`

- Model run scripts that supply prompts + images + context to the 3 LVLMs and collect the generated icon descriptions.

  `icons_runs-k-shot.ipynb`, `icons_runs-zero-shot.ipynb`, `llm.py`

- Evaluation and post-processing scripts that and compute various automated metrics and statistics.

  `run_eval.py`, `select_he_samples.py`, `clip.sh`
