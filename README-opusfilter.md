# Data preparation

Steps:

1) Install OpusFilter >= 2.0

```
pip install opusfilter
```

2) Create OpusFilter configuration using `processed_data` as work directory:

```
python create_opusfilter_config.py --add-labels --no-monolingual opusfilter.yaml processed_data
```

3) Run OpusFilter on the configuration:

```
PYTHONPATH=$PYTHONPATH:. opusfilter opusfilter.yaml
```
(PYTHONPATH added to include custom preprocessors in `create_opusfilter_config.py`.)

The filtered and labeled output files are in: `processed_data/[LANGUAGE]/*_labeled.[LANGCODE].gz`

The data preparation for English-Spanish can be run as follows:

```
PYTHONPATH=$PYTHONPATH:. opusfilter opusfilter_english.yaml
PYTHONPATH=$PYTHONPATH:. opusfilter opusfilter_english_opensubs.yaml
```

The script `collect_data_sizes.py` can be used to collect a table of the number of lines in the produced files.
