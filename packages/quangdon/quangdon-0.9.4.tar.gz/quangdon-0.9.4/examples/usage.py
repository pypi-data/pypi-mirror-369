"""
To run:
uv venv --seed -p 3.11
uv pip install ".[en]"
uv run examples/usage.py    
"""

from quangdon import en

g2p = en.G2P(trf=False, british=False, fallback=None) # no transformer, American English

text = '[quangdon](/kwɑŋˈdɑn/) is a G2P engine designed for [vansarah](/vænˈsærə/) models.'

phonemes, tokens = g2p(text)

print(phonemes) # kwɑŋˈdɑn ɪz ə ʤˈitəpˈi ˈɛnʤən dəzˈInd fɔɹ vænˈsærə mˈɑdᵊlz.