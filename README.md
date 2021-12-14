
This is a scuffed and kindof messy chess engine, still haven't implemented a proper ai with minmax search yet (im lazy so i leave making the ai to another day)

I initialize the board with numpy and named the pieces after the images in the folder
I then load the key value pair into a table named PIECES with the name of the piece as the key and the pygame object as the value

I update the board every 15 ticks so it is responsive :)

Algorithms are thought out of my mind so you may find the code to may or may not be messy


------
I initialize the essentials and the castle and moves log, so i can revert back moves
I use 2 main functions to figure out the valid moves of chess, function GetALlPossibleMoves gets everything raw and the FilterValidMoves handles the pins, checks and such.
Everything else is it's own thing

I have 2 classes in the engine file, Move and State, Move is the class that handles moving the pieces and updating positions and looks of the board
The engine does the heavy lifting and everything essential goes there.

Ideally i would do something more simple like a use a library, but somehow I ended up doing this from scratch

I state the valid moves in each function for its own piece: Queen, Pawn, etc

For this chess engine I used the naive algoithm to check if there are checks or pins, I loop through the enemies possible moves and if one of those moves involve checking my king, I remove them from the valid moves list

Thats it for now, :)


PROGRESS: Just implemented castling, fixed a weird bug, but its fine now
