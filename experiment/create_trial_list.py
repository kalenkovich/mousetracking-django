#################################################################################
# 1_prepare_experimental_sheets.py
# !/usr/bin/env python
# coding: utf-8

from collections import OrderedDict
from itertools import cycle
from itertools import product
from random import seed as random_seed, choice
from random import shuffle
from zlib import adler32
from pathlib import Path

import numpy as np
import pandas as pd

from .models import Image
import experiment


def deterministic_hash(bytes_):
    return adler32(bytes_)


def deterministic_string_hash(string):
    return deterministic_hash(string.encode('utf-8'))


# # Fully-crossed factors

non_random_factor_levels = OrderedDict(
    polarity=('positive', 'negative'),
    orientation=('rows', 'columns'),
    order=('polarity_first', 'polarity_last'),
    object_number=(2, 3, 4))

non_random_factors = pd.DataFrame(
    data=product(*non_random_factor_levels.values()),
    columns=non_random_factor_levels.keys(),
    index=range(1, 25)
)

# # Randomly assigned factors

# ## Configuration

configurations = {
    2: (np.array([[1, 0],
                  [0, 1]]),

        np.array([[0, 1],
                  [1, 0]])),

    3: (np.array([[0, 1],
                  [1, 1]]),

        np.array([[1, 0],
                  [1, 1]]),

        np.array([[1, 1],
                  [0, 1]]),

        np.array([[1, 1],
                  [1, 0]])),

    4: (np.array([[1, 1],
                  [1, 1]]),)
}


def pick_configuration(object_number):
    return choice(configurations[object_number])


# ## Side
# Which row/column contains the target

sides = dict(
    rows=('top', 'bottom'),
    columns=('left', 'right')
)


def pick_side(orientation):
    return choice(sides[orientation])


# ## Target and lure cells
# Both objects are selected randomly from the non-empty cells in the corresponding row/columns determined by *configuration* and *side*.

coordinates = {
    'left': [(0, 0), (1, 0)],
    'right': [(0, 1), (1, 1)],
    'top': [(0, 0), (0, 1)],
    'bottom': [(1, 0), (1, 1)],
}


def pick_random_object(side, configuration):
    side_coordinates = coordinates[side]
    non_empty_coordinates = list(zip(*np.where(configuration == 1)))
    choices = [c for c in side_coordinates if c in non_empty_coordinates]
    assert len(choices) in (1, 2)
    return choice(choices)


the_other = {
    'left': 'right',
    'right': 'left',
    'top': 'bottom',
    'bottom': 'top'
}


def pick_target_and_lure(side, configuration):
    return (
        pick_random_object(side, configuration),
        pick_random_object(the_other[side], configuration))


# ## Target position
# Either left or right

def pick_target_position():
    return choice(('left', 'right'))


# # Make all trials

# The number of trils per combination of the fully-crossed factors

REPEATS = 12


def make_trials():
    trials = non_random_factors.loc[np.repeat(non_random_factors.index.values, REPEATS)]
    trials.reset_index()
    trials['configuration'] = trials.object_number.apply(pick_configuration)
    trials['side'] = trials.orientation.apply(pick_side)
    trials[['target_cell', 'lure_cell']] = trials.apply(lambda x: pick_target_and_lure(x.side, x.configuration),
                                                        axis='columns', result_type='expand')
    trials['target_position'] = trials.apply(lambda x: pick_target_position(), axis='columns')
    trials.reset_index(drop=True, inplace=True)
    return trials


# # Assign objects

# Load object names

non_object_images = ('frame', 'empty')
objects = [image.name for image in Image.objects.all() if image.name not in non_object_images]
objects = sorted(objects)

# Remove certain objects

sub_par_objects = ('axe', 'basket', 'battery', 'beer', 'bowl', 'briefcase', 'brush', 'butter', 'cherry',
                   'chocolate', 'cookie', 'doughnut', 'drum', 'fork', 'fountain', 'holepunch', 'jelly',
                   'kite', 'ladle', 'lighter', 'perfume', 'pie', 'plate', 'pliers', 'stapler', 'teapot',
                   'watch', 'wine')
assert all([sub_par_object in objects for sub_par_object in sub_par_objects])

objects = [object_ for object_ in objects if object_ not in sub_par_objects]
objects = sorted(objects)

# Check that at least the names have not changed since the last run
assert deterministic_string_hash(''.join(sorted(objects))) == 1312403687


# - Shuffle trials
# - Shuffle objects
# - Assign objects to trials circularly

def assign_objects(trials):
    # Shuffle trials
    trials_shuffled = trials.sample(frac=1).copy().reset_index(drop=True)

    # Shuffle objects
    objects_shuffled = objects.copy()
    shuffle(objects_shuffled)
    objects_cycle = cycle(objects_shuffled)

    # Assign objects in cycle
    def get_another_n_objects(n):
        return [next(objects_cycle) for _ in range(n)]

    trials_shuffled['objects'] = trials_shuffled.object_number.apply(get_another_n_objects)

    return trials_shuffled


# # Make sheets

def make_sheet():
    trials = make_trials()
    return assign_objects(trials)


# ## Training trials

# Six trials:
# - left, affirmative, 2 objects, polarity_last
# - top, negative, 3 objects, polarity_last,
# - left, negative, 4 objects, polarity_first
# - bottom, positive, 3 objects, polarity_last
# - right, positive, 4 objects, polarity_first
# - right, negative, 2 objects, polarity_first

filter_ = pd.DataFrame.from_dict(dict(
    side=['left', 'top', 'left', 'bottom', 'right', 'right'],
    polarity=['positive', 'negative', 'negative', 'positive', 'positive', 'negative'],
    object_number=[2, 3, 4, 3, 4, 2],
    order=['polarity_last', 'polarity_last', 'polarity_first', 'polarity_last', 'polarity_first', 'polarity_first']
))


practice_sheet = pd.merge(
    # Take 1 for each combination
    make_sheet().groupby(['side', 'polarity', 'object_number', 'order']).apply(lambda x: x.sample(1)).reset_index(drop=True),
    # Inner-join with the required combination
    filter_,
    on=['side', 'polarity', 'object_number', 'order']
)


#################################################################################
# 3_Make_and_assign_audio.py
# !/usr/bin/env python
# coding: utf-8

app_dir = Path(experiment.__file__).parent
disambiguating_onsets = pd.read_csv(app_dir / 'disambiguation-onsets_polarity-first.csv').append(
    pd.read_csv(app_dir / 'disambiguation-onsets_polarity-last.csv'), ignore_index=True)
disambiguating_onsets['audio_name'] = disambiguating_onsets.filename.str.replace('.wav', '')

# # Determine the location that should be indicated in the sentences
# Which row or column is indicated in the sentence.
# Polarity of the sentence and the side containing the target object determine this factor.

the_other = {
    'left': 'right',
    'right': 'left',
    'top': 'bottom',
    'bottom': 'top'
}


def compute_location(polarity, side):
    if polarity == 'positive':
        return side
    elif polarity == 'negative':
        return the_other[side]


# # Assign audio to trials

def select_audio_name(location, polarity, order):
    """
    Return the name of the audio file that should be played in a trial
    """
    prefix = choice(('this-time', 'in-this-picture'))
    if order == 'polarity_first':
        return '{}_{}_{}'.format(prefix, polarity, location)
    elif order == 'polarity_last':
        return '{}_{}_{}'.format(prefix, location, polarity)


def add_audio_info(sheet):
    sheet['location'] = sheet.apply(lambda x: compute_location(x.polarity, x.side), axis='columns')
    sheet['audio_name'] = sheet.apply(lambda x: select_audio_name(x.location, x.polarity, x.order), axis='columns')
    sheet = sheet.join(disambiguating_onsets.set_index('audio_name')[['onset']], on='audio_name')

    return sheet
