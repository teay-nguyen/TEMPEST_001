import os
import pygame as pyg

def get_pieces(interface):
    PIECES = {}
    for fn in os.listdir('pieces'):
        full_path = os.path.join('pieces', fn)
        name = fn.replace('.png', '')
        PIECES[name] = pyg.transform.scale(pyg.image.load(full_path), (interface.SIZE, interface.SIZE))

    return PIECES
