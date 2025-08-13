# lib_sudoku

A python library for solving sudoku puzzles written in Rust.

It can read and solve 9 million puzzles in under 10 seconds.

## Installation

For easy installation, run:
```bash
pip install lib_sudoku
```

If you prefer, you can build the code yourself from source. To do this, run
```bash
git clone https://github.com/shaggysa/lib_sudoku.git
cd lib_sudoku
maturin build --release
pip install target/wheels/lib_sudoku*.whl
```

## Basic Usage

A solver function, generator function, and reader class are currently available. A sample of python code to test each of these functions is available below:

First, import the sudoku library and the time library:

```python
import lib_sudoku as sudoku
import time
```

Then, create a puzzle reader class with the puzzles you want to solve:

```python
reader = sudoku.PuzzleReader("https://raw.githubusercontent.com/shaggysa/lib_sudoku/master/puzzles.csv", True)
```

To test the solver, run a speedtest function and pass in the reader:

```python
sudoku.async_speedtest(reader)
sudoku.synchronous_speedtest(reader)
```

To test the generator, simply call the gen_unsolved function and pass in the number of hints you want the final puzzle to have

you can also time it if you would like:
```python
num_hints = 24
start_gen = time.time()
sudoku.gen_unsolved(num_hints)
print(f"Generated a puzzle with {num_hints} hints in {(time.time() - start_gen)*1000} milliseconds.")
```

Note that the less hints you want in your unsolved puzzle, the longer it will take for the generator to make it.

In my testing, it usually takes under a millisecond to generate a puzzle with 30 hints, but it can take up to 50ms for a puzzle with 24 hints.

Generating puzzles with under 23 hints does not work because it will get stuck.

Note: If you want to try out the speedtest function on the large (9 million puzzle dataset), you can download it at https://www.kaggle.com/datasets/rohanrao/sudoku.

Just make sure to move the extracted file into your working directory and to adjust the PuzzleReader class parameters to be ("sudoku.csv", False)