#################################################################################
# 1_prepare_experimental_sheets.py
#!/usr/bin/env python
# coding: utf-8

from collections import OrderedDict
from itertools import cycle
from itertools import product
from random import seed as random_seed, choice
from random import shuffle
from zlib import adler32

import joblib
import numpy as np
import pandas as pd
from IPython.display import HTML
from folders import individual_images_dir
from folders import original_audio_folder, audio_folder, sheets_folder, new_audio_folder
from pydub import AudioSegment


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

non_random_factors

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


random_seed(31)
for object_number in non_random_factor_levels['object_number']:
    print('{} objects:'.format(object_number))
    for sample in range(4):
        print('Sample {}:'.format(sample + 1))
        configuration = pick_configuration(object_number)
        print(configuration)
    print('\n')

# ## Side
# Which row/column contains the target

sides = dict(
    rows=('top', 'bottom'),
    columns=('left', 'right')
)


def pick_side(orientation):
    return choice(sides[orientation])


random_seed(57)
for orientation in non_random_factor_levels['orientation']:
    print('Orientaion: {}'.format(orientation))
    for sample in range(8):
        print(pick_side(orientation))
    print('\n')

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


def pick_random_side():
    # Used for demonstration purposes only
    # First choice selects between rows and columns, the second one - between two corresponding sides.
    return choice(choice(list(sides.items()))[1])


random_seed(32)
for object_number in non_random_factor_levels['object_number']:
    print('{} objects:'.format(object_number))
    for sample in range(4):
        print('\nSample {}:'.format(sample + 1))

        configuration = pick_configuration(object_number)
        print('configuration:')
        print(configuration)

        side = pick_random_side()
        print('target side: {}'.format(side))

        target, lure = pick_target_and_lure(side, configuration)
        configuration = configuration.astype(str)
        configuration[target] = '+'
        configuration[lure] = '-'
        print('Target (+) and lure (-)')
        print(configuration)
    print('\n')


# ## Target position
# Either left or right

def pick_target_position():
    return choice(('left', 'right'))


random_seed(31)
for _ in range(6):
    print(pick_target_position())

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


random_seed(3132)
trials = make_trials()
np.random.seed(3132)
trials.sample(15)

# # Assign objects

# Load object names

non_object_images = ('frame', 'empty')
objects = [image.stem for image in individual_images_dir.glob('*.png') if image.stem not in non_object_images]
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


random_seed(3132)
np.random.seed(3132)
assign_objects(trials).head(15)

# # Make sheets

N_PARTICIPANTS = 32
SEED = 31313131


def make_sheet(file_path):
    trials = make_trials()
    sheet = assign_objects(trials)
    sheet.to_pickle(file_path)


random_seed(SEED)
np.random.seed(SEED)
for i in range(N_PARTICIPANTS):
    n = i + 1
    print('Making sheet {:02d}'.format(n))
    file_path = sheets_folder / 'participant-{:02d}.pkl'.format(n)
    assert not file_path.exists()
    make_sheet(file_path)

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
filter_

random_seed(SEED + 1)
np.random.seed(SEED + 1)
trials = make_trials()
sheet = assign_objects(trials)

file_path = sheets_folder / 'training.pkl'

np.random.seed(SEED + 1)
practice_trials = pd.merge(
    # Take 1 for each combination
    sheet.groupby(['side', 'polarity', 'object_number', 'order']).apply(lambda x: x.sample(1)).reset_index(drop=True),
    # Inner-join with the required combination
    filter_,
    on=['side', 'polarity', 'object_number', 'order']
)
practice_trials

practice_trials.to_pickle(file_path)

# # Output hashes

# It is not obvious what random seed to set (`np.random.seed` for `pandas` and `numpy`, `random.seed` for `random`.
# So, to check that the results are reproducible, we calculate hashes for all the objects.

for file in sorted(list(sheets_folder.glob('*.pkl'))):
    print(file.name, joblib.hash(pd.read_pickle(file)))


#################################################################################
# 3_Make_and_assign_audio.py
# !/usr/bin/env python
# coding: utf-8

# # Create the audio
# The audio has been spliced and marked for the onsets of the disambiguating word manually.
# Here we add the beeps at the onset of the disambiguating word and save a copy.

disambiguating_onsets = pd.read_csv(new_audio_folder / 'polarity_first' / 'disambiguation_onsets.csv').append(
    pd.read_csv(new_audio_folder / 'polarity_last' / 'disambiguation_onsets.csv'), ignore_index=True)
disambiguating_onsets

beeps_file_path = original_audio_folder / '..' / 'beepsrampamp.wav'
beeps = AudioSegment.from_wav(beeps_file_path)
beeps

original_audio = pd.DataFrame.from_dict(dict(file_path=new_audio_folder.glob('*/*.wav')))
original_audio.index = original_audio.file_path.apply(lambda x: x.name)
original_audio.index.name = 'filename'
original_audio

audio_df = disambiguating_onsets.join(original_audio, on='filename')
audio_df


def overlay_beeps(audio_path, onset):
    audio = AudioSegment.from_wav(audio_path)

    # Pad at the end if beeps should finish after the audio does
    final_duration = onset + len(beeps)
    if final_duration > len(audio):
        audio += AudioSegment.silent(duration=(final_duration - onset), )

    # "- 2" makes the beeps quiter
    return audio.overlay(beeps - 2, onset)


audio_df['audio'] = audio_df.apply(lambda x: (overlay_beeps(x.file_path, x.onset)), axis='columns')


def print_with_playable_audio(df: pd.DataFrame, audio_columns=['audio']):
    # Remember the option before changing it
    max_colwidth = pd.get_option('display.max_colwidth')

    # Otherwise most of the tag will be replaced with ...
    pd.set_option('display.max_colwidth', -1)

    html = df.to_html(
        escape=False,
        formatters={audio_column: lambda a: a._repr_html_()
                    for audio_column in audio_columns})

    # Set the option back
    pd.set_option('display.max_colwidth', max_colwidth)

    return HTML(html)


print_with_playable_audio(audio_df)

first_audio = audio_df.audio.iloc[0]


def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


audio_dir = audio_folder
audio_dir.mkdir(exist_ok=True)

for row in audio_df.itertuples():
    output_path = audio_dir / row.filename
    assert not output_path.exists()
    match_target_amplitude(row.audio, first_audio.dBFS).export(output_path, format='wav')

# # Determine the location that should be indicated in the sentences
# Which row or column is indicated in the sentence.
# Polarity of the sentence and the side containing the target object determine this factor.

the_other = {
    'left': 'right',
    'right': 'left',
    'top': 'bottom',
    'bottom': 'top'
}

sides = list(the_other.keys())


def compute_location(polarity, side):
    if polarity == 'positive':
        return side
    elif polarity == 'negative':
        return the_other[side]


random_seed(57)
for polarity in ('positive', 'negative'):
    print('Polarity: {}'.format(polarity))
    for sample in range(8):
        random_side = choice(sides)
        print('side: {:>10}, location: {:>10}'.format(random_side, compute_location(polarity, random_side)))
    print('\n')


# # Assign audio to trials

def select_audio(location, polarity, order):
    """
    Return the name of the audio file that should be played in a trial
    """
    prefix = choice(('this-time', 'in-this-picture'))
    if order == 'polarity_first':
        return '{}_{}_{}.wav'.format(prefix, polarity, location)
    elif order == 'polarity_last':
        return '{}_{}_{}.wav'.format(prefix, location, polarity)


random_seed(9182736450)
for location, polarity, order in product(
        ['left', 'right', 'bottom', 'top'],
        ['positive', 'negative'],
        ['polarity_first', 'polarity_last']):
    print('{:<10} {:<12} {:<18}- {}'.format(location, polarity, order, select_audio(location, polarity, order)))

random_seed(918273645)
for sheet_file_path in sheets_folder.glob('*.pkl'):
    sheet = pd.read_pickle(sheet_file_path)
    sheet['location'] = sheet.apply(lambda x: compute_location(x.polarity, x.side), axis='columns')
    trial_audio = (sheet
        .apply(  # Select audio
        lambda x: select_audio(x.location, x.polarity, x.order),
        axis='columns')
        .to_frame(name='audio_filename')
        .join(  # Add onsets
        audio_df.set_index('filename')[['onset']],
        on='audio_filename')
    )
    audio_df_file_path = audio_dir / sheet_file_path.name
    assert not audio_df_file_path.exists()
    trial_audio.to_pickle(audio_df_file_path)

# # Output hashes

# It is not obvious what random seed to set (`np.random.seed` for `pandas` and `numpy`, `random.seed` for `random`.
# So, to check that the results are reproducible, we calculate hashes for all the objects.
#
# It might be a good idea to check the sounds as well but, since they are not random, we'll just assume that the same code will produce the same sounds.

for file in sorted(list(audio_folder.glob('*.pkl'))):
    print(file.name, joblib.hash(pd.read_pickle(file)))
