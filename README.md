# AutoDungeonPlayer

## Introduction
AutoDungeonPlayer comes in two parts; a game and an AI. Unfortunately, the game is not meant for humans to play, i.e. it has _no_ UI and no way to control the player in the game. How very fascinating, you must be thinking. Undoubtedly so, for I will now introduce the next part of the project; the Smart AI <sup>TM</sup> algorithm!

## Installation and Running
Simple, clone the repo:
```
git clone https://github.com/lawruixi/AutoDungeonPlayerPublic
```

The file `input2.csv` contains testcases written in the format as stated in the first line of the input file. Edit the file to your liking, then run the game with

```
python3 game.py
```

## The Smart <sup>TM</sup> AI Algorithm
The Smart AI uses a version of the [Monte Carlo Tree Search](en.wikipedia.org/wiki/Monte_Carlo_tree_search) to decide the best move at any given turn. You may inspect the code by viewing the file `mcts.py`.

## Future Work
* Updating AI to be more "smart"
* Possibly making a testcase input generator, given how annoying it is to input test cases.
* Possibly a UI or a nicer way other than ASCII art to display the game.
* Maybe have AI vs Player? (We can dream)

## Built With
love and care <​3

## Contributing
This project is in development. If you encounter any bugs/issues, please open an issue. You may also submit pull requests for minor stuff if you have fixed a bug etc.

## Acknowledgements
You, for viewing this repo :​)
