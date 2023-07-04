import argparse
import collections
import gzip
import logging
import os

from tabulate import tabulate

from create_opusfilter_config import LANGUAGES, LANGCODE, get_work_files


def get_num_lines(fname):
    with gzip.open(fname, 'r') as fobj:
        num_lines = sum(1 for line in fobj)
    return num_lines


def count_extra_raw(lang, workdir):
    total_lines = 0
    for i in range(13):
        src, tgt = get_work_files(lang, f'extra-part-{i}')
        fname = os.path.join(workdir, tgt)
        if os.path.isfile(fname):
            total_lines += get_num_lines(fname)
    return total_lines

def get_en_work_files(prefix):
    src = f'english/{prefix}.es.gz'
    tgt = f'english/{prefix}.en.gz'
    return [src, tgt]


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('workdir', type=str, help='OpusFilter work directory')
    parser.add_argument('-en', action='store_true', help='Count Spanish-English data only')
    args = parser.parse_args()
    print(args)

    logging.basicConfig(level=logging.INFO)

    if args.en:
        print("ENGLISH MODE")
        dataparts = {
            'default': 'default_unfiltered',
            'default_filt': 'default_filtered', # already deduped
            'ost': 'ost_unfiltered',
            'ost_filt': 'ost_filtered', # already deduped
            'bible_filt': 'bibles', # already deduped
            'wmt_labeled': 'dev'
        }

        table = {}
        table['language'] = ['english']
        table['code'] = ['en']
        for prefix, label in dataparts.items():
            row = []
            src, tgt = get_en_work_files(prefix)
            fname = os.path.join(args.workdir, tgt)
            if os.path.isfile(fname):
                lines = get_num_lines(fname)
            else:
                lines = 0
            row.append(lines)
            logging.info("%s %s", fname, lines)
            table[label] = row
        print(tabulate(table, headers=table.keys(), tablefmt='latex'))

    else:
        # {prefix_in_workdir: header_in_output_table}
        dataparts = {
            'train': 'train_unfiltered',
            'train_filtered': 'train_filtered',
            'extra_all': 'extra_unfiltered',
            'extra': 'extra_filtered',
            #'combined': 'combined',
            'dedup': 'combined_dedup',
            'bibles': 'bibles',
            'dev_labeled': 'dev'
            }

        table = {}
        table['language'] = [l.replace('_', '-').title() for l in LANGUAGES]
        table['code'] = [LANGCODE[l] for l in LANGUAGES]
        for prefix, label in dataparts.items():
            row = []
            for lang in LANGUAGES:
                if prefix == 'extra_all':
                    lines = count_extra_raw(lang, args.workdir)
                else:
                    src, tgt = get_work_files(lang, prefix)
                    fname = os.path.join(args.workdir, tgt)
                    if os.path.isfile(fname):
                        lines = get_num_lines(fname)
                    else:
                        lines = 0
                row.append(lines)
                logging.info("%s %s", fname, lines)
            table[label] = row

        print(tabulate(table, headers=table.keys(), tablefmt='latex'))
