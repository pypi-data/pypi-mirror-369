import lib_sudoku as sudoku
import time


def tests():
    reader = sudoku.PuzzleReader(
        "https://raw.githubusercontent.com/shaggysa/lib_sudoku/master/puzzles.csv", True
    )
    sudoku.async_speedtest(reader)
    sudoku.synchronous_speedtest(reader)

    num_hints = 24
    start_gen = time.time()
    sudoku.gen_unsolved(num_hints)
    print(
        f"Generated a puzzle with {num_hints} hints in {(time.time() - start_gen)*1000} milliseconds."
    )


if __name__ == "__main__":
    tests()
