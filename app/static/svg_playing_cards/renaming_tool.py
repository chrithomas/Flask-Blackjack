import sys
import os

path = './fronts/'
suit_changes = {'hearts' : 'H', 'diamonds' : 'D', 'clubs' : 'C', 'spades' : 'S'}
key_changes = {'ace' : 'A', 'jack' : 'J', 'queen' : 'Q', 'king' : 'K' }
for file in os.listdir(path):
    suit, key = file.split('_')[0], file.split('_')[1]
    if key in key_changes:
        key = key_changes[key]
    if suit in suit_changes:
        suit = suit_changes[suit]
    os.rename(path + file, path + suit + '_' + key + '.svg')

# for file in os.listdir(path):
#     if file.endswith('.svg'):
#         os.rename(path + file, path + file[:-4])