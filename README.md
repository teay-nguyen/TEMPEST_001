
![Logo](logo.png)

# OVERVIEW

The TEMPEST Chess Engine is an open-source didactic minimal chess engine with basic features you would find in a mediocre chess engine  
This engine is an incomplete terminal-based engine with basic UCI features implemented  
TEMPEST has not yet supported NNUE evaluation, and has only been implemented with the classic handcrafted evaluation function

## Installation

```
git clone https://github.com/HashingTerry/TEMPEST_001.git
```

## Usage

```
pypy3 main.py
```

or  

```
python main.py
```

## Testing

There is no viable and elaborate way to test the engine  
Test FEN strings are stored in the tests folder in a seperate files named differently according to the purpose of the positions  
You can copy one of the FEN strings into the UCI for it to parse the string, the doing what you want since the fen string is loaded

## Contributing

Pull Requests are highly encouraged, as doing this alone would take a long time  
For major changes, please open an issue first to discuss what you would like to change

# TODO

- Implement fully functional Search Routine, with Transposition Tables
- Engine playing stupid moves sometimes when searching at depth 6, e.g losing knight because engine thinks fork on f7 is fine
- Improve pawn evaluation and overall evaluation of pieces
- Optimize move generation
- Migrate from copy-make to a make-undo structure
