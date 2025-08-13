use pyo3::pyfunction;
use crate::libraries::puzzle_reader;
use crate::libraries::puzzle_solver::{async_solve, solve};


#[pyfunction]
#[pyo3(signature = (puzzle_reader, verbose = false))]
pub fn async_speedtest(puzzle_reader: &puzzle_reader::PuzzleReader, verbose: bool) {

    println!("---------------\nStarting Async Speedtest\n---------------");
    let start_solve = std::time::Instant::now();
    
    let rt = tokio::runtime::Runtime::new().unwrap();

    let mut solved_puzzles = Vec::new();

    rt.block_on(async {
        let handles: Vec<_> = puzzle_reader.clone()
            .unsolved
            .into_iter()
            .map(|puzz| tokio::spawn(async_solve(puzz)))
            .collect();

        for handle in handles {
            solved_puzzles.push(handle.await.unwrap());
        }
    });
    
    let solve_time = start_solve.elapsed();

    let start_validate = std::time::Instant::now();

    for i in 0..solved_puzzles.len() {
        let pc_solved: Vec<u8>;

        match &solved_puzzles[i] {
            Ok(puzz) => {
                pc_solved = puzz.clone();
            },
            Err(_e) => {println!("Found an unsolvable puzzle at line {}", i + 2); break;},

        }
        if verbose {
            println!("\nLine {}:", i + 2);
            println!("Unsolved: ",);
            puzzle_reader::print_puzz(puzzle_reader.unsolved[i].clone());
            println!("\nSolved:");
            puzzle_reader::print_puzz(pc_solved.clone());


        }
        if pc_solved != puzzle_reader.solved[i] {
            println!("Solver Failed at line {}!", i + 2);
            break;
        }
    }
    println!("Solved {} Puzzles in {:?}", puzzle_reader.size, solve_time);
    if verbose {
        println!("Printed and validated {} puzzles in {:?}", puzzle_reader.size, start_validate.elapsed());
    } else {
        println!("Validated {} puzzles in {:?}", puzzle_reader.size, start_validate.elapsed());
    }
}

#[pyfunction]
#[pyo3(signature = (puzzle_reader, verbose = false))]
pub fn synchronous_speedtest(puzzle_reader: &puzzle_reader::PuzzleReader, verbose: bool) {
    println!("---------------\nStarting Synchronous Speedtest\n---------------");
    let mut solved_puzzles = Vec::new();
    let start_solve = std::time::Instant::now();
    for i in 0..puzzle_reader.unsolved.len() {
        solved_puzzles.push(solve(puzzle_reader.unsolved[i].clone()));
    }
    let solve_time = start_solve.elapsed();
    let start_validate = std::time::Instant::now();

    for i in 0..solved_puzzles.len() {
        let pc_solved: Vec<u8>;

        match &solved_puzzles[i] {
            Ok(puzz) => {
                pc_solved = puzz.clone();
            },
            Err(_e) => {println!("Found an unsolvable puzzle at line {}", i + 2); break;},

        }
        if verbose {
            println!("\nLine {}:", i + 2);
            println!("Unsolved: ",);
            puzzle_reader::print_puzz(puzzle_reader.unsolved[i].clone());
            println!("\nSolved:");
            puzzle_reader::print_puzz(pc_solved.clone());


        }
        if pc_solved != puzzle_reader.solved[i] {
            println!("Solver Failed at line {}!", i + 2);
            break;
        }
    }
    println!("Solved {} Puzzles in {:?}", puzzle_reader.size, solve_time);
    if verbose {
        println!("Printed and validated {} puzzles in {:?}", puzzle_reader.size, start_validate.elapsed());
    } else {
        println!("Validated {} puzzles in {:?}", puzzle_reader.size, start_validate.elapsed());
    }
}
