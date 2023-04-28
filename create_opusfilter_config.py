#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import copy
import logging
import os
import re

import opusfilter
from yaml import dump, Dumper

# Variant handling:
# 1. Extra data in different variant than train and dev data:
#    a. Extra variant can be normalized to train variant
#       => normalize and use same label as train (e.g. Bribri)
#    b. Extra variant cannot be normalized to train variant
#       => use distinct label (e.g. Chatino)
# 2. All training data in different variant than dev data:
#    => No distinct labels, just use what we have

LANGUAGES = ['ashaninka', 'aymara', 'bribri', 'chatino', 'guarani', 'hñähñu', 'nahuatl',
             'quechua', 'raramuri', 'shipibo_konibo', 'wixarika']

LANGCODE = {
    'ashaninka': 'cni',
    'aymara': 'aym',
    'bribri': 'bzd',
    'chatino': 'czn',
    'guarani': 'gn',
    'hñähñu': 'oto',
    'nahuatl': 'nah',
    'quechua': 'quy',
    'raramuri': 'tar',
    'shipibo_konibo': 'shp',
    'wixarika': 'hch',
    'spanish': 'es'
}

TOKENIZED_TRAIN = {
    'ashaninka': False,
    'aymara': False,
    'bribri': True,
    'chatino': False,
    'guarani': False,
    'hñähñu': True,
    'nahuatl': True,
    'quechua': False,
    'raramuri': True,
    'shipibo_konibo': False,
    'wixarika': False
}

EXTRA = {
    'ashaninka': [
        {'prefix': 'synt/bt_yves21'}
    ],
    'aymara': [
        {'prefix': 'extra/sent-boconst_aym'},
        {'prefix': 'extra/flores200'},
        {'prefix': 'extra/OPUS.aym-es', 'quality': 'noisy'},
        {'prefix': 'synt/bt_yves21', 'quality': 'bt'},
        {'prefix': 'synt/nllb.md'},
        {'prefix': 'synt/globalvoices_pivot'}
    ],
    'bribri': [
        {'prefix': 'extra/uicn', 'variant': 'jara'},
        {'prefix': 'extra/enciclopedia_final', 'variant': 'constenla', 'quality': 'noisy'}
    ],
    'chatino': [
        {'prefix': 'extra/sent-mxconst', 'variant': 'plain'},
        {'prefix': 'synt/ctp-eng', 'code': 'ctp'},
    ],
    'guarani': [
        {'prefix': 'extra/sent-pyconst'},
        {'prefix': 'synt/bt_yves21', 'quality': 'bt'},
        {'prefix': 'extra/jojajovai/jojajovai'},
        {'prefix': 'extra/noticias'},
        {'prefix': 'extra/flores200'},
        {'prefix': 'synt/nllbseed'},
        {'prefix': 'extra/OPUS.gn-es', 'quality': 'noisy'}
    ],
    'hñähñu': [
        {'prefix': 'extra/sent-mxconst'},
        {'prefix': 'extra/dict', 'code': 'ote'}
    ],
    'nahuatl': [
        {'prefix': 'extra/sent-mxconst'},
        {'prefix': 'synt/bt_yves21', 'quality': 'bt'},
        {'prefix': 'extra/texts', 'quality': 'noisy'},
        {'prefix': 'extra/dictexamplesents.spa-nah'},
        {'prefix': 'synt/dictexamplesents_eng'},
        {'prefix': 'extra/OPUS.nah-es', 'quality': 'noisy'}
    ],
    'quechua': [
        {'prefix': 'parallel_data/es-quy/minedu.quy-es'},
        {'prefix': 'parallel_data/es-quy/dict_misc.quy-es'},
        {'prefix': 'synt/jw300_quy_pivot'},
        {'prefix': 'parallel_data/es-quz/jw300.es-quz', 'code': 'quz', 'variant': 'quz'},
        {'prefix': 'synt/jw300_quz_pivot', 'code': 'quz', 'variant': 'quz'},
        {'prefix': 'extra/sent-boconst_que', 'code': 'que', 'variant': 'quh'},
        {'prefix': 'extra/sent-peconst', 'code': 'que'},
        {'prefix': 'synt/bt_yves21', 'quality': 'bt'},
        {'prefix': 'extra/flores200'},
        {'prefix': 'extra/OPUS.quy-es', 'quality': 'noisy'}
    ],
    'raramuri': [
        {'prefix': 'extra/sent-mxconst'}
    ],
    'shipibo_konibo': [
        {'prefix': 'extra/Educational_0.4_2.4_35/all-es-shi', 'code': 'shi'},
        {'prefix': 'extra/Religious_0.2_2.4_35/all-es-shi', 'code': 'shi'},
        {'prefix': 'extra/tsanas1'},
        {'prefix': 'extra/covid19'},
        {'prefix': 'extra/sent-leyartesano', 'code': 'shi'},
        {'prefix': 'synt/bt_yves21', 'quality': 'bt'}
    ],
    'wixarika': [
        {'prefix': 'extra/sent-mxconst'},
        {'prefix': 'extra/corpora', 'code': 'wix'},
        {'prefix': 'extra/paral_own', 'code': 'wix'},
        {'prefix': 'extra/segcorpus', 'code': 'wix'},
        {'prefix': 'synt/bt_yves21', 'quality': 'bt'}
        # Note: train.wix/hch is the combination of these:
        # {'prefix': 'extra/corp-train', 'code': 'wix'},
        # {'prefix': 'extra/corp-dev', 'code': 'wix'},
        # {'prefix': 'extra/corp-test', 'code': 'wix'}
    ]
}

BIBLES = {
    'ashaninka': [
        {'file': 'cni-x-bible-cni-v1.txt'}
    ],
    'aymara': [
        {'file': 'ayr-x-bible-2011-v1.txt'}
    ],
    'bribri': [
        {'file': 'bzd-x-bible-bzd-v1.txt', 'variant': 'constenla'}
    ],
    'chatino': [
        {'file': 'cta-x-bible-cta-v1.txt', 'variant': 'plain'},
        {'file': 'ctp-x-bible-ctp-v1.txt', 'variant': 'plain'},
        {'file': 'cya-x-bible-cya-v1.txt', 'variant': 'plain'}
    ],
    'guarani': [{'file': 'gug-x-bible-gug-v1.txt'}],
    'hñähñu': [{'file': 'ote-x-bible-ote-v1.txt'}],
    'nahuatl': [
        {'file': 'nhi-x-bible-nhi-v1.txt'},  # ce = 0.2671 (excluded in 2021)
        {'file': 'ncj-x-bible-ncj-v1.txt'},  # ce = 1.05 (excluded in 2021)
        {'file': 'azz-x-bible-azz-v1.txt'},  # ce = 1.9494 (excluded in 2021)
        # {'file': 'nah-NHXNTV.txt'},          # ce = 3.5871 (excluded in 2021)
        # {'file': 'nhy-x-bible-nhy-v1.txt'},  # ce = 3.8592 (excluded in 2021)
        # {'file': 'nhe-x-bible-nhe-v1.txt'},  # ce = 5.1487 (included in 2021)
        # {'file': 'ngu-x-bible-ngu-v1.txt'},  # ce = 5.363 (included in 2021)
        # {'file': 'nhw-x-bible-nhw-v1.txt'},  # ce = 5.555 (included in 2021)
        # {'file': 'nch-x-bible-nch-v1.txt'},  # ce = 5.9472 (included in 2021)
    ],
    'quechua': [
        {'file': 'quy-x-bible-quy-v1.txt'},
        {'file': 'quz-x-bible-quz-v1.txt', 'variant': 'quz'}
    ],
    'raramuri': [
        {'file': 'tac-x-bible-tac-v1.txt'}
    ],
    'shipibo_konibo': [
        {'file': 'shp-SHPTBL.txt'}
    ],
    'wixarika': [
        {'file': 'hch-x-bible-hch-v1.txt'}
    ],
    'spanish': [
        {'file': 'spa-x-bible-americas.txt.jhubc'},
        {'file': 'spa-x-bible-hablahoi-latina.txt.jhubc'},
        {'file': 'spa-x-bible-lapalabra.txt.jhubc'},
        {'file': 'spa-x-bible-newworld.txt.jhubc'},
        {'file': 'spa-x-bible-nuevadehoi.txt.jhubc'},
        {'file': 'spa-x-bible-nuevaviviente.txt.jhubc'},
        {'file': 'spa-x-bible-nuevointernacional.txt.jhubc'},
        {'file': 'spa-x-bible-reinavaleracontemporanea.txt.jhubc'}
    ]
}


MONOLINGUAL = {
    'ashaninka': [
        {'file': 'test.txt'},
        {'file': 'train.txt'},
        {'file': 'valid.txt'}
    ],
    'aymara': [{'file': 'wiki.ay.aa'}],
    'guarani': [{'file': 'wiki.gn.aa'}],
    'hñähñu': [{'file': 'ote.txt'}],
    'nahuatl': [
        {'file': 'wikibooks.nah.aa'},
        {'file': 'wiki.nah.aa'}
    ],
    'quechua': [
        {'file': 'wikibooks.qu.aa'},
        {'file': 'wiki.qu.aa'}
    ],
    'shipibo_konibo': [
        {'file': 'test.txt'},
        {'file': 'train.txt'},
        {'file': 'valid.txt'}
    ],
    'wixarika': [{'file': 'social.wix'}]
}


def get_bible_files(lang):
    for entry in BIBLES[lang]:
        fn = f'data/bibles/{lang}/{entry["file"]}'
        if not os.path.isfile(fn):
            logging.warning("No file at", fn)
    return [(f'../data/bibles/{lang}/{entry["file"]}', entry.get('variant', 'default')) for entry in BIBLES[lang]]


def get_monolingual_files(lang):
    for entry in MONOLINGUAL[lang]:
        fn = f'data/{lang}-spanish/mono/{entry["file"]}'
        if not os.path.isfile(fn):
            logging.warning("No file at", fn)
    return [f'../data/{lang}-spanish/mono/{entry["file"]}' for entry in MONOLINGUAL[lang]]


def get_input_files(lang, prefix='train', code=None, variant=None, quality=None):
    code = LANGCODE[lang] if code is None else code
    if not os.path.isfile(f'data/{lang}-spanish/{prefix}.es'):
        logging.warning(f'No file at data/{lang}-spanish/{prefix}.es')
    if not os.path.isfile(f'data/{lang}-spanish/{prefix}.{code}'):
        logging.warning(f'No file at data/{lang}-spanish/{prefix}.{code}')
    src = f'../data/{lang}-spanish/{prefix}.es'
    tgt = f'../data/{lang}-spanish/{prefix}.{code}'
    return [src, tgt]


def get_work_files(lang, prefix):
    code = LANGCODE[lang]
    src = f'{lang}/{prefix}.es.gz'
    tgt = f'{lang}/{prefix}.{code}.gz'
    return [src, tgt]


def get_score_file(lang, prefix):
    return f'{lang}/{prefix}.scores.jsonl.gz'


def get_lm_file(lang, prefix):
    code = LANGCODE.get(lang, lang)
    return os.path.join('..', 'char_lms', f'{prefix}.{code}.arpa.gz')


def guaraniNormalize(text):
    text = re.sub(r"[ãäā]", "â", text, flags=re.IGNORECASE)
    text = re.sub(r"[ẽëē]", "ê", text, flags=re.IGNORECASE)
    text = re.sub(r"[ĩïī]", "î", text, flags=re.IGNORECASE)
    text = re.sub(r"[õöō]", "ô", text, flags=re.IGNORECASE)
    text = re.sub(r"[ũüū]", "û", text, flags=re.IGNORECASE)
    text = re.sub(r"[ỹŷ]", "ÿ", text, flags=re.IGNORECASE)
    text = re.sub(r"g̃", "ĝ", text, flags=re.IGNORECASE)
    return text

class GuaraniNormalizer(opusfilter.PreprocessorABC):
    """Normalizer for Guarani. Normalizes all nasal diacritics (ã, ä, ā to â).
    ~ is most standard, but ^ is used in the dev set.
    Normalizes only the second input file.
    """

    def process(self, pairs):
        for segments in pairs:
            output = []
            for idx, segment in enumerate(segments):
                output.append(guaraniNormalize(segment) if idx == 1 else segment)
            yield output

# From https://github.com/pywirrarika/wixnlp/blob/master/normwix.py
def normwix(text):
    text = text.lower()
    text = re.sub(r"´", "'", text, flags=re.IGNORECASE)
    #text = re.sub(r"'", "", text, flags=re.IGNORECASE)
    text = re.sub(r"v", "w", text, flags=re.IGNORECASE)
    text = re.sub(r"(c|qu)", "k", text, flags=re.IGNORECASE)
    text = re.sub(r"[0-9]+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"ch", "ts", text, flags=re.IGNORECASE)
    text = re.sub(r"rr", "x", text, flags=re.IGNORECASE)
    text = re.sub(r" +", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"[üï]", "+", text, flags=re.IGNORECASE)
    text = re.sub(r"^ ", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?<!t|\[)s", "ts", text, flags=re.IGNORECASE)
    text = re.sub(r"[áàä]", "a", text, flags=re.IGNORECASE)
    text = re.sub(r"[éèë]", "e", text, flags=re.IGNORECASE)
    text = re.sub(r"[íì]", "i", text, flags=re.IGNORECASE)
    text = re.sub(r"[óòö]", "o", text, flags=re.IGNORECASE)
    text = re.sub(r"[úù]", "u", text, flags=re.IGNORECASE)
    text = re.sub(r"([a-z+])\1+", r"\1", text, flags=re.IGNORECASE)
    return text


class WixarikaNormalizer(opusfilter.PreprocessorABC):
    """Normalizer for the Wixarika bible corpus. Normalizes only the 2nd input file."""

    def process(self, pairs):
        for segments in pairs:
            output = []
            for idx, segment in enumerate(segments):
                output.append(normwix(segment) if idx == 1 else segment)
            yield output


# From data/bribri-spanish/bribri-orthography-conversion.ipynb
# This isn't used in the shared task - it's just for displaying the examples in a human-readable way.
def intermediate2constenla(s):
    # These use Sofía Flores' diacritic conventions,
    # where the line is a COMBINING MINUS SIGN BELOW 0x0320
    diacriticChars = {
        "ã":"a̠", "ẽ":"e̠","ĩ":"i̠", "õ":"o̠","ũ":"u̠",                  # Nasal low tone
        "áx":"á̠", "éx":"é̠", "íx":"í̠", "óx":"ó̠", "úx":"ú̠",           # Nasal falling tone
        "àx":"à̠", "èx":"è̠", "ìx":"ì̠", "òx":"ò̠", "ùx":"ù̠",           # Nasal high tone
        "âx":"â̠", "êx":"ê̠", "îx":"î̠", "ôx":"ô̠", "ûx":"û̠",           # Nasal rising tone
        "éq":"ë́", "óq":"ö́", "èq":"ë̀", "òq":"ö̀", "êq":"ë̂", "ôq":"ö̂"  # Lax vowels
    }
    for c in diacriticChars:
        s = s.replace(c, diacriticChars.get(c))
    return s

def constenla2intermediate(s):
    diacriticChars = {
        "a̠":"ã", "e̠":"ẽ", "i̠":"ĩ", "o̠":"õ", "u̠":"ũ",               # Nasal low tone
        "á̠":"áx", "é̠":"éx", "í̠":"íx", "ó̠":"óx", "ú̠":"úx",           # Nasal falling tone
        "à̠":"àx", "è̠":"èx", "ì̠":"ìx", "ò̠":"òx", "ù̠":"ùx",           # Nasal high tone
        "â̠":"âx", "ê̠":"êx", "î̠":"îx", "ô̠":"ôx", "û̠":"ûx",           # Nasal rising tone
        "ë́":"éq", "ö́":"óq", "ë̀":"èq", "ö̀":"òq", "ë̂":"êq", "ö̂":"ôq"  # Lax vowels
    }
    for c in diacriticChars:
        s = s.replace(c, diacriticChars.get(c))
    return s

def jara2intermediate(s):
    diacriticChars = {
        "ã":"ã", "ẽ":"ẽ", "ĩ":"ĩ", "õ":"õ", "ũ":"ũ",                # Nasal low tone
        "ã́":"áx", "ẽ́":"éx", "ĩ́":"íx", "ṍ":"óx", "ṹ":"úx",           # Nasal falling tone
        "ã̀":"àx", "ẽ̀":"èx", "ĩ̀":"ìx", "õ̀":"òx", "ũ̀":"ùx",           # Nasal high tone
        "ã̂":"âx", "ẽ̂":"êx", "ĩ̂":"îx", "õ̂":"ôx", "ũ̂":"ûx",           # Nasal rising tone
        "ë́":"éq", "ö́":"óq", "ë̀":"èq", "ö̀":"òq", "ë̂":"êq", "ö̂":"ôq"  # Lax vowels
    }
    coromaChanges = {
        "tch":"tk",
        "Ñõlòx":"Ñãlàx", "ñõlòx":"ñãlàx",                   # road
        "Kóx":"Káx", "kóx":"káx",                           # place
        "Kòxlĩ":"Kàxlĩ", "kòxlĩ":"kàxlĩ",                   # rain
        "Kóxwötã'":"Káxwötã'", "kóxwötã'":"káxwötã'",       # need
        "Kóxwötã":"Káxwötã", "kóxwötã":"káxwötã",           # need
        "Krò":"Dakarò", "krò":"dakarò"                      # chicken
    }
    for c in diacriticChars:
        s = s.replace(c, diacriticChars.get(c))
    for c in coromaChanges:
        s = s.replace(c, coromaChanges.get(c))
    return s

class BribriNormalizer(opusfilter.PreprocessorABC):
    """Normalizer for the Bribri train/dev corpora. Normalizes only the 2nd input file."""

    def __init__(self, orthography, **kwargs):
        super().__init__(**kwargs)
        self.srcOrthography = orthography

    def process(self, pairs):
        for segments in pairs:
            output = []
            for idx, segment in enumerate(segments):
                if self.srcOrthography == 'constenla':
                    output.append(constenla2intermediate(segment) if idx == 1 else segment)
                elif self.srcOrthography == 'jara':
                    output.append(jara2intermediate(segment) if idx == 1 else segment)
                elif self.srcOrthography == 'intermediate':
                    output.append(intermediate2constenla(segment) if idx == 1 else segment)
                else:
                    output.append(segment)
            yield output


class RaramuriNormalizer(opusfilter.PreprocessorABC):
    """Normalizer for Raramuri data. Assumes Spanish - Raramuri input.

    Applies conversions mentioned in https://github.com/AmericasNLP/americasnlp2021/pull/5

    """

    tz2ch = (re.compile(r'tz'), 'ch')
    star_token = (re.compile(r' \* '), '')
    two_apostrophes_token = (re.compile(r" ` ' "), "’")
    apostrophe_token = (re.compile(r" ' "), "’")
    apostrophe_any = (re.compile(r"['`´]"), "’")

    def process(self, pairs):
        for segments in pairs:
            esp, tar = segments
            for pat, rep in [self.tz2ch, self.star_token, self.two_apostrophes_token,
                             self.apostrophe_token, self.apostrophe_any]:
                tar = re.sub(pat, rep, tar)
            yield esp, tar


class RaramuriTrainCleaner(opusfilter.PreprocessorABC):
    """Cleaner for Raramuri train data. Assumes Spanish - Raramuri input."""

    starting_cparen = re.compile(r'^[0-9a-z] \) ')
    starting_paren = re.compile(r'^(\( ([0-9]{1,2}|[a-z]) \) )+')
    ending_paren = re.compile(r' \( [0-9a-z] \)$')
    middle_paren = re.compile(r'\( [^\)]+? \)')

    def process(self, pairs):
        for segments in pairs:
            esp, tar = segments
            if re.match(self.starting_cparen, tar):
                # e ) ŕekó perá
                # 3 ) kepi tzo
                # a ) empolvarse
                tar = re.sub(self.starting_cparen, '', tar)
            if re.match(self.starting_cparen, esp):
                # a ) empolvarse
                # a ) hacerse neblina , formarse niebla
                esp = re.sub(self.starting_cparen, '', esp)
            if re.match(self.starting_paren, tar):
                # ( 1 ) ga'rá ka rá asiba !
                tar = re.sub(self.starting_paren, '', tar)
            if re.match(self.starting_paren, esp):
                # ( 1 ) hacer que se limpie
                esp = re.sub(self.starting_paren, '', esp)
            if re.search(self.ending_paren, tar):
                # bowérema ( 2 )
                tar = re.sub(self.ending_paren, '', tar)
            if not '(' in tar and re.search(self.middle_paren, esp):
                # otro que cayó ! ( en la trampa )
                # ( en ) El Yeso
                # ( se oye ) que ahí va una culebra !
                esp = re.sub(self.middle_paren, '', esp)
                esp = re.sub(r' +', ' ', esp)
            if ' , ' in esp and not ' , ' in tar and len(esp) > 1.5 * len(tar):
                # asiento , silla , banco
                # -> select first
                esp = esp.split(' , ')[0]
            yield esp, tar


class ChatinoNormalizer(opusfilter.PreprocessorABC):
    """Normalizer for Chatino data. Assumes Spanish - Raramuri input.

    Normalizes two tone letters that use different unicode characters.

    """

    replacements = [
        # train & dev set
        ('ᵃ', 'ᴬ'),
        ('ᵇ', 'ᴮ'),
        ('ᵉ', 'ᴱ'),
        ('ⁱ', 'ᴵ'),
        ('ʲ', 'ᴶ'),
        ('ᵏ', 'ᴷ'),
        ('', ''),
        ('', ''),
        # extras
        ('ꟲ', 'ᶜ'),
        ('ꟳ', 'ᶠ')
    ]

    def process(self, pairs):
        for segments in pairs:
            esp, tar = segments
            for old, new in self.replacements:
                tar = tar.replace(old, new)
            yield esp, tar


class BlankFilter(opusfilter.FilterABC):
    """Filter out lines containing only BLANK (for data from Bibles)"""

    def score(self, pairs):
        for pair in pairs:
            yield [(sentence.strip() != 'BLANK') for sentence in pair]

    def accept(self, score):
        return all(score)


class PrefixLabels(opusfilter.PreprocessorABC):
    """Add labels as prefixes to the source sentence"""

    def __init__(self, labels, workdir='', **kwargs):
        super().__init__(workdir, **kwargs)
        self.labels = labels

    def process(self, pairs):
        for segments in pairs:
            src, tgt = segments
            yield ' '.join(self.labels) + ' ' + src, tgt


def main(config_output, workdir, single=None, tokenize=False, bibles=True, dev=True,
         monolingual=True, filtering=True, train_lms=False,
         add_labels=False):
    # WORKDIR = 'processed_data'
    # OUTPUT = 'opusfilter.yaml'

    if single:
        logging.info("Creating config for %s data", single)
    if tokenize:
        logging.info("Tokenization enabled")
    if not bibles:
        logging.info("Bibles disabled")
    if not dev:
        logging.info("Dev sets disabled")
    if not monolingual:
        logging.info("Monolingual sets disabled")
    extra_datasets = EXTRA
    if not filtering:
        logging.info("Filtering disabled")
    if add_labels:
        logging.info("Labels enabled")
        if train_lms:
            logger.warning("Labels should not be used when training char LMs for source language!")


    filter_params = {
        'LengthFilter': {'unit': 'char', 'min_length': 1, 'max_length': 1000},
        'LengthRatioFilter': {'unit': 'char', 'threshold': 4},
        'CharacterScoreFilter': {'scripts': ['Latin', 'Latin'], 'thresholds': [0.9, 0.9]},
        'TerminalPunctuationFilter': {'threshold': -2},
        'NonZeroNumeralsFilter': {'threshold': 0.5}
    }

    active_filters = {
        'ashaninka': ['LengthFilter', 'LengthRatioFilter'],
        'aymara': ['LengthFilter', 'LengthRatioFilter', 'CharacterScoreFilter',
                   'TerminalPunctuationFilter', 'NonZeroNumeralsFilter'],
        'bribri': ['LengthFilter', 'LengthRatioFilter'],
        'chatino': ['LengthFilter', 'LengthRatioFilter'],
        'guarani': ['LengthFilter', 'LengthRatioFilter'],
        'hñähñu': ['LengthFilter', 'LengthRatioFilter'],
        'nahuatl': ['LengthFilter', 'LengthRatioFilter'],
        'quechua': ['LengthFilter', 'LengthRatioFilter', 'CharacterScoreFilter',
                    'TerminalPunctuationFilter', 'NonZeroNumeralsFilter'],
        'raramuri': ['LengthFilter', 'LengthRatioFilter', 'CharacterScoreFilter',
                     'NonZeroNumeralsFilter'],
        'shipibo_konibo': ['LengthFilter', 'LengthRatioFilter'],
        'wixarika': ['LengthFilter', 'LengthRatioFilter', 'NonZeroNumeralsFilter']
    }

    quality_filters = {
        'noisy': [
            {'HtmlTagFilter': {}},
            {'LengthRatioFilter': {'unit': 'word', 'threshold': 2}},
            {'CharacterScoreFilter': {'scripts': ['Latin', 'Latin'], 'thresholds': [0.9, 0.7]}},
        ],
        'bt': [
            {'LengthRatioFilter': {'unit': 'word', 'threshold': 2}},
            {'CharacterScoreFilter': {'scripts': ['Latin', 'Latin'], 'thresholds': [0.9, 0.7]}},
            {'LanguageIDFilter': {'languages': ['es', 'en'], 'thresholds': [0.8, -1]}}
        ]
    }

    steps = []

    # Preprocess/copy train sets
    for lang in LANGUAGES:
        if single and lang != single:
            continue
        code = LANGCODE[lang]
        inputs = get_input_files(lang, 'train')
        outputs = get_work_files(lang, 'train')
        preprocessors = []
        if lang == 'chatino':
            preprocessors.append({'ChatinoNormalizer': {}, 'module': 'create_opusfilter_config'})
        elif lang == 'guarani':
            preprocessors.append({'GuaraniNormalizer': {}, 'module': 'create_opusfilter_config'})
        elif lang == 'raramuri':
            preprocessors.append({'RaramuriTrainCleaner': {}, 'module': 'create_opusfilter_config'})
            preprocessors.append({'RaramuriNormalizer': {}, 'module': 'create_opusfilter_config'})
        elif TOKENIZED_TRAIN[lang]:
            preprocessors.append({'Detokenizer': {
                'tokenizer': 'moses',
                'languages': ['es', LANGCODE[lang]]
            }})
        else:
            pass  # no preprocessing needed
        preprocessors.append({'WhitespaceNormalizer': {}})
        steps.append({
            'type': 'preprocess',
            'parameters': {
                'inputs': inputs,
                'outputs': outputs,
                'preprocessors': preprocessors
            }
        })
        if filtering and active_filters[lang]:
            inputs = outputs
            outputs = get_work_files(lang, 'train_filtered')
            filters = [{filt: filter_params[filt]} for filt in active_filters[lang]]
            steps.append({
                'type': 'filter',
                'parameters': {
                    'inputs': inputs,
                    'outputs': outputs,
                    'filters': filters
                }
            })
        if add_labels:
            inputs = outputs
            outputs = get_work_files(lang, 'train_labeled')
            steps.append({
                'type': 'preprocess',
                'parameters': {
                    'inputs': inputs,
                    'outputs': outputs,
                    'preprocessors': [
                        {'PrefixLabels': {'labels': [f'<{code}>', f'<{code}-default>', '<default>']},
                         'module': 'create_opusfilter_config'}
                    ]
                }
            })

    # Preprocess/copy dev sets
    # - No filtering for dev sets
    if dev or train_lms:
        for lang in LANGUAGES:
            if single and lang != single:
                continue
            code = LANGCODE[lang]
            inputs = get_input_files(lang, 'dev')
            outputs = get_work_files(lang, 'dev_labeled' if add_labels else 'dev')
            preprocessors = []
            if lang == 'chatino':
                preprocessors.append({'ChatinoNormalizer': {}, 'module': 'create_opusfilter_config'})
            else:
                pass  # no preprocessing needed
            preprocessors.append({'WhitespaceNormalizer': {}})
            if add_labels:
                preprocessors.append({'PrefixLabels': {'labels': [f'<{code}>', f'<{code}-default>', '<default>']},
                                      'module': 'create_opusfilter_config'})
            steps.append({
                'type': 'preprocess',
                'parameters': {
                    'inputs': inputs,
                    'outputs': outputs,
                    'preprocessors': preprocessors
                }
            })

    # Preprocess/copy extra corpora
    for lang in extra_datasets:
        if single and lang != single:
            continue
        for idx, extra in enumerate(extra_datasets[lang]):
            inputs = get_input_files(lang, **extra)
            outputs = get_work_files(lang, f'extra-part-{idx}')
            quality_label = extra.get('quality', 'default')
            preprocessors = []
            if lang == 'bribri':
                # if variant label can be handled by normalizer, add the normalizer and remove the label
                if "variant" in extra and extra["variant"] in ("constenla", "jara"):
                    preprocessors.append({'BribriNormalizer': {"orthography": "{}".format(extra["variant"])}, 'module': 'create_opusfilter_config'})
                    extra["variant"] == "default"
            if lang == 'raramuri':
                preprocessors.append({'RaramuriNormalizer': {}, 'module': 'create_opusfilter_config'})
            elif lang == 'chatino':
                preprocessors.append({'ChatinoNormalizer': {}, 'module': 'create_opusfilter_config'})
            elif lang == 'guarani':
               preprocessors.append({'GuaraniNormalizer': {}, 'module': 'create_opusfilter_config'})
            else:
                pass  # no preprocessing needed
            preprocessors.append({'WhitespaceNormalizer': {}})
            steps.append({
                'type': 'preprocess',
                'parameters': {
                    'inputs': inputs,
                    'outputs': outputs,
                    'preprocessors': preprocessors
                }
            })
            if filtering:
                inputs = outputs
                outputs = get_work_files(lang, f'extra-part-{idx}_filtered')
                if active_filters[lang]:
                    filters = [{filt: filter_params[filt]} for filt in active_filters[lang]]
                else:
                    filters = []
                
                # add specific filters for backtranslations and particularly noisy sources
                if quality_label in quality_filters:
                    filters.extend(quality_filters[quality_label])

                steps.append({
                    'type': 'filter',
                    'parameters': {
                        'inputs': inputs,
                        'outputs': outputs,
                        'filters': filters
                    }
                })

            if add_labels:
                inputs = outputs
                outputs = get_work_files(lang, f'extra-part-{idx}_labeled')
                variant = extra.get('variant', 'default')
                steps.append({
                    'type': 'preprocess',
                    'parameters': {
                        'inputs': inputs,
                        'outputs': outputs,
                        'preprocessors': [
                            {'PrefixLabels': {'labels': [f'<{code}>', f'<{code}-{variant}>', f'<{quality_label}>']},
                             'module': 'create_opusfilter_config'}
                        ]
                    }
                })

    # Combine extra data sets
    # - includes filtering and prefix labels when those are enabled
    for lang in extra_datasets:
        if single and lang != single:
            continue
        if add_labels:
            inputs = [get_work_files(lang, f'extra-part-{idx}_labeled') for idx in range(len(extra_datasets[lang]))]
        elif filtering:
            inputs = [get_work_files(lang, f'extra-part-{idx}_filtered') for idx in range(len(extra_datasets[lang]))]
        else:
            inputs = [get_work_files(lang, f'extra-part-{idx}') for idx in range(len(extra_datasets[lang]))]
        for idx in [0, 1]:
            steps.append({
                'type': 'concatenate',
                'parameters': {
                    'inputs': [f[idx] for f in inputs],
                    'output': get_work_files(lang, 'extra')[idx]
                }
            })

    # Combine training and extra data sets
    # - includes filtering and prefix labels when those are enabled
    for lang in LANGUAGES:
        if single and lang != single:
            continue
        if add_labels:
            inputs = [get_work_files(lang, 'train_labeled')]
        else:
            inputs = [get_work_files(lang, 'train')]
        if lang in extra_datasets:
            inputs.append(get_work_files(lang, 'extra'))
        for idx in [0, 1]:
            steps.append({
                'type': 'concatenate',
                'parameters': {
                    'inputs': [f[idx] for f in inputs],
                    'output': get_work_files(lang, 'combined')[idx]
                }
            })

    # Remove duplicates
    # - includes filtering and prefix labels when those are enabled
    for lang in LANGUAGES:
        if single and lang != single:
            continue
        inputs = get_work_files(lang, 'combined')
        steps.append({
            'type': 'remove_duplicates',
            'parameters': {
                'inputs': inputs,
                'outputs': get_work_files(lang, 'dedup')
            }
        })

    # Bibles
    # * k=3 random entries from Spanish bibles
    # * all tokenized -> detokenize
    # * wixarika should use normalization in normwix.py
    if bibles:
        spanish_bibles = [t[0] for t in get_bible_files('spanish')]
        for lang in LANGUAGES:
            if single and lang != single:
                continue
            n_bibles = len(BIBLES[lang])
            # Number of samples from Spanish bibles per sentence
            if n_bibles == 1:
                n_samples = 3
            elif n_bibles <= 3:
                n_samples = 2
            else:
                n_samples = 1
            for idx, (biblefile, variant) in enumerate(get_bible_files(lang)):
                inputs = [spanish_bibles, [biblefile]]
                raw = get_work_files(lang, f'bible-{idx}-raw')
                steps.append({
                    'type': 'product',
                    'parameters': {
                        'inputs': inputs,
                        'outputs': raw,
                        'skip_empty': True,
                        'skip_duplicates': True,
                        'k': n_samples,
                        'seed': 'bibles'
                    }
                })
                outputs = get_work_files(lang, f'bible-{idx}')
                preprocessors = []
                if lang == 'bribri':
                    # if variant label can be handled by normalizer, add the normalizer and remove the label
                    if "variant" in extra and extra["variant"] in ("constenla", "jara"):
                        preprocessors.append({'BribriNormalizer': {"orthography": "{}".format(extra["variant"])}, 'module': 'create_opusfilter_config'})
                        extra["variant"] == "default"
                if lang == 'wixarika':
                    preprocessors.append({'WixarikaNormalizer': {}, 'module': 'create_opusfilter_config'})
                elif lang == 'raramuri':
                    preprocessors.append({'RaramuriNormalizer': {}, 'module': 'create_opusfilter_config'})
                preprocessors.append(
                    {'Detokenizer': {
                        'tokenizer': 'moses',
                        'languages': ['es', LANGCODE[lang]]
                    }}
                )
                preprocessors.append({'WhitespaceNormalizer': {}})
                if add_labels:
                    preprocessors.append({'PrefixLabels': {'labels': [f'<{code}>', f'<{code}-{variant}>', '<bible>']},
                                          'module': 'create_opusfilter_config'})
                steps.append({
                    'type': 'preprocess',
                    'parameters': {
                        'inputs': raw,
                        'outputs': outputs,
                        'preprocessors': preprocessors
                    }
                })
                filtered_outputs = get_work_files(lang, f'bible-{idx}_filtered')
                steps.append({
                    'type': 'filter',
                    'parameters': {
                        'inputs': outputs,
                        'outputs': filtered_outputs,
                        'filters': [
                            {'BlankFilter': {}, 'module': 'create_opusfilter_config'}
                        ]
                    }
                })
            inputs = [get_work_files(lang, f'bible-{idx}_filtered') for idx in range(n_bibles)]
            #logging.warning(inputs)
            for idx in [0, 1]:
                steps.append({
                    'type': 'concatenate',
                    'parameters': {
                        'inputs': [f[idx] for f in inputs],
                        'output': get_work_files(lang, 'bibles')[idx]
                    }
                })

    # Combine monolingual data sets
    if monolingual:
        for lang in MONOLINGUAL:
            if single and lang != single:
                continue
            inputs = get_monolingual_files(lang)
            output = get_work_files(lang, 'monolingual')[1]
            output_filtered = get_work_files(lang, 'monolingual_filtered')[1]
            steps.append({
                'type': 'concatenate',
                'parameters': {
                    'inputs': inputs,
                    'output': output
                }
            })
            steps.append({
                'type': 'filter',
                'parameters': {
                    'inputs': [output],
                    'outputs': [output_filtered],
                    'filters': [
                        {'LengthFilter': {'unit': 'word', 'min_length': 1, 'max_length': 500}}
                    ]
                }
            })

    if tokenize:
        # Tokenize training sets
        # FIXME: does not work properly at least for wixarika
        for lang in LANGUAGES:
            if single and lang != single:
                continue
            inputs = get_work_files(lang, output_prefix)
            outputs = get_work_files(lang, output_prefix + '_tokenized')
            steps.append({
                'type': 'preprocess',
                'parameters': {
                    'inputs': inputs,
                    'outputs': outputs,
                    'preprocessors': [
                        {'Tokenizer': {
                            'tokenizer': 'moses',
                            'languages': ['es', LANGCODE[lang]]
                        }}
                    ]
                }
            })
        # Tokenize dev sets
        for lang in LANGUAGES:
            if single and lang != single:
                continue
            inputs = get_work_files(lang, prefix='dev')
            outputs = get_work_files(lang, prefix='dev_tokenized')
            steps.append({
                'type': 'preprocess',
                'parameters': {
                    'inputs': inputs,
                    'outputs': outputs,
                    'preprocessors': [
                        {'Tokenizer': {
                            'tokenizer': 'moses',
                            'languages': ['es', LANGCODE[lang]]
                        }}
                    ]
                }
            })

    if train_lms:
        # Spanish models
        spanish_dev = 'spanish/all-dev.gz'
        spanish_dev_dedup = 'spanish/all-dev-dedup.gz'
        spanish_combined = 'spanish/all-combined.gz'
        spanish_combined_dedup = 'spanish/all-combined-dedup.gz'
        steps.append({
            'type': 'concatenate',
            'parameters': {
                'inputs': [get_work_files(lang, 'dev')[0] for lang in LANGUAGES],
                'output': spanish_dev
            }
        })
        steps.append({
            'type': 'remove_duplicates',
            'parameters': {
                'inputs': [spanish_dev],
                'outputs': [spanish_dev_dedup]
            }
        })
        steps.append({
            'type': 'train_ngram',
            'parameters': {
                'data': spanish_dev_dedup,
                'parameters': {'norder': 6, 'dscale': 0.01, 'absolute': True},
                'model': get_lm_file('spanish', 'dev')
            }
        })
        steps.append({
            'type': 'concatenate',
            'parameters': {
                'inputs': [get_work_files(lang, 'combined')[0] for lang in LANGUAGES],
                'output': spanish_combined
            }
        })
        steps.append({
            'type': 'remove_duplicates',
            'parameters': {
                'inputs': [spanish_combined],
                'outputs': [spanish_combined_dedup]
            }
        })
        steps.append({
            'type': 'train_ngram',
            'parameters': {
                'data': spanish_combined_dedup,
                'parameters': {'norder': 6, 'dscale': 0.1, 'absolute': True},
                'model': get_lm_file('spanish', 'bg')
            }
        })
        # Target language models
        for lang in LANGUAGES:
            if single and lang != single:
                continue
            steps.append({
                'type': 'train_ngram',
                'parameters': {
                    'data': get_work_files(lang, 'dev')[1],  # target
                    'parameters': {'norder': 6, 'dscale': 0.01, 'absolute': True},
                    'model': get_lm_file(lang, 'dev')
                }
            })
            source_files = ['dedup', 'bibles']
            if lang in MONOLINGUAL:
                source_files.append('monolingual')
            steps.append({
                'type': 'concatenate',
                'parameters': {
                    'inputs': [get_work_files(lang, source)[1] for source in source_files],
                    'output': get_work_files(lang, 'combined_monolingual')[1]
                }
            })
            steps.append({
                'type': 'train_ngram',
                'parameters': {
                    'data': get_work_files(lang, 'combined_monolingual')[1],  # target
                    'parameters': {'norder': 6, 'dscale': 0.1, 'absolute': True},
                    'model': get_lm_file(lang, 'bg')
                }
            })
        # Global background model (for e.g. language identification use, prevents OOVs)
        # TODO: add English?
        global_combined = 'global/all-combined.gz'
        steps.append({
            'type': 'concatenate',
            'parameters': {
                'inputs': [spanish_combined_dedup] + [get_work_files(lang, 'dedup')[0] for lang in LANGUAGES],
                'output': global_combined
            }
        })
        steps.append({
            'type': 'train_ngram',
            'parameters': {
                'data': global_combined,
                'parameters': {'norder': 1, 'dscale': 0, 'absolute': True},
                'model': get_lm_file('global', 'bg')
            }
        })
        # Score training material on cross-entropy difference
        for lang in LANGUAGES:
            if single and lang != single:
                continue
            steps.append({
                'type': 'score',
                'parameters': {
                    'inputs': get_work_files(lang, 'dedup_filtered'),
                    'output': get_score_file(lang, 'dedup_filtered'),
                    'filters': [{
                        'CrossEntropyDifferenceFilter': {
                            'id_lm_params': [
                                {'filename': get_lm_file('spanish', 'dev'), 'interpolate': [[get_lm_file('spanish', 'bg'), 0.1]]},
                                {'filename': get_lm_file(lang, 'dev'), 'interpolate': [[get_lm_file(lang, 'bg'), 0.1]]},
                            ],
                            'nd_lm_params': [
                                {'filename': get_lm_file('spanish', 'bg')},
                                {'filename': get_lm_file(lang, 'bg')},
                            ],
                            'thresholds': 0
                        }
                    }],
                }
            })
            steps.append({
                'type': 'sort',
                'parameters': {
                    'inputs': get_work_files(lang, 'dedup_filtered'),
                    'outputs': get_work_files(lang, 'dedup_filtered_sorted'),
                    'values': get_score_file(lang, 'dedup_filtered'),
                    'key': 'CrossEntropyDifferenceFilter.1'
                }
            })

    logging.info("%s steps generated for %s", len(steps), config_output)

    # Write YAML configuration for opusfilter
    config = {
        'common': {
            'output_directory': workdir
        },
        'steps': steps
    }
    with open(config_output, 'w') as fobj:
        fobj.write(dump(config, Dumper=Dumper))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create OpusFilter configuration')
    parser.add_argument('output', metavar='FILE', help='OpusFilter config file')
    parser.add_argument('workdir', metavar='DIR', help='Work directory for OpusFilter')
    parser.add_argument('--no-bibles', dest='bibles', action='store_false', help='Exclude Bibles')
    parser.add_argument('--no-dev', dest='dev', action='store_false', help='Exclude dev sets')
    parser.add_argument('--no-monolingual', dest='monolingual', action='store_false', help='Exclude monolingual sets')
    parser.add_argument('--no-filtering', dest='filtering', action='store_false', help='Exclude filtering')
    parser.add_argument('--tokenize', action='store_true', help='Include tokenization')
    parser.add_argument('--lm', action='store_true', help='Train char LMs')
    parser.add_argument('--add-labels', action='store_true', help='Include lang / variant / quality labels')
    parser.add_argument('--single', default=None, help='Use single language')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    main(args.output, args.workdir, single=args.single, tokenize=args.tokenize,
         bibles=args.bibles, dev=args.dev, monolingual=args.monolingual,
         filtering=args.filtering, train_lms=args.lm, add_labels=args.add_labels)
