
![Logo](logo.png)

# OVERVIEW

The TEMPEST Chess Engine is an open-source didactic minimal chess engine with basic features you would find in a mediocre chess engine  
This engine is an incomplete terminal-based engine with no UCI options implemented yet  
The estimate NPS for this engine is around 10K to 60K nodes per second, dependant on how good your machine is  
TEMPEST has not yet supported NNUE evaluation, and has only been implemented with the classic handcrafted evaluation function

## Installation

```
git clone https://github.com/HashingTerry/TEMPEST_001.git
```

## Usage

```
pypy3 tempest.py
```

or  

```
python tempest.py
```

## Testing

Test FEN strings are stored in the tests folder in a seperate files named differently according to the purpose of the positions  
You can copy one of the FEN strings into the tempest file for it to parse the string, the doing what you want since the fen string is loaded

## Contributing

Pull Requests are highly encouraged, as doing this alone would take a long time  
For major changes, please open an issue first to discuss what you would like to change

# TODO

- Implement Search Routine, with Transposition Tables
- Improve pawn evaluation and overall evaluation of pieces
- Optimize move generation
