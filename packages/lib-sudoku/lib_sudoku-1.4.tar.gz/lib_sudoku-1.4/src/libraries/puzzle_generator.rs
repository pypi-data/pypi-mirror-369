use std::cmp::PartialEq;
use pyo3::PyResult;
use rand::Rng;
use rand::seq::SliceRandom;
use crate::libraries::puzzle_solver;
use puzzle_solver::Puzzle;
use crate::libraries::puzzle_generator::Order::{RANDOM, REVERSE};

#[derive(PartialEq)]
pub enum Order {
    REVERSE,
    RANDOM,
}

fn alt_get_possibilities(puzz: &Vec<u8>, pos: u8, order: &Order) -> Vec<u8> {
    let mut possibilities: Vec<u8> = Vec::new();
    let mut seen: [bool; 10] = [false; 10];
    let row: usize = (pos / 9) as usize;
    let col: usize = (pos % 9) as usize;
    let root_row = (row / 3) * 3;
    let root_col = (col / 3) * 3;

    for r in root_row..root_row + 3 {
        for c in root_col..root_col + 3 {
            seen[puzz[r * 9 + c] as usize] = true;
        }
    }
    for i in 0..9 {
        seen[puzz[i + (row * 9)] as usize] = true;
        seen[puzz[col + (i * 9)] as usize] = true;
    }

    if *order == REVERSE {
        for i in (1..10).rev() {
            if !seen[i as usize] {
                possibilities.push(i)
            }
        }
    }
    else if *order == RANDOM {
        let mut nums: Vec<u8> = (1..10).collect();
        nums.shuffle(&mut rand::rng());
        for i in nums.iter() {
            if !seen[*i as usize] {
                possibilities.push(*i)
            }
        }
    }
    possibilities
}

fn alt_solver_prep(puzz: Vec<u8>, order: Order) -> Puzzle {
    let mut p: Puzzle = Puzzle {
        puzz,
        blank_positions: Vec::new(),
        possibilities: Vec::new(),
        cached_possibilities: Vec::new(),
        current_pos: Vec::new(),
        solved: false,
    };
    for i in 0..81 {
        if p.puzz[i] == 0 {
            p.blank_positions.push(i as u8);
        }
    }
    loop {
        let mut to_remove: Vec<u8> = Vec::new();
        let mut progressed = false;
        for i in p.blank_positions.iter().rev() {
            let possibilities = puzzle_solver::get_possibilities(&p.puzz, *i);
            if possibilities.len() == 1 {
                p.puzz[*i as usize] = possibilities[0];
                to_remove.push(*i);
                progressed = true;
            }
        }
        if progressed {
            p.blank_positions.retain(|&x| {
                if let Some(&last_item) = to_remove.last() {
                    if x == last_item {
                        to_remove.pop();
                        return false;
                    }
                }
                true
            });
        } else {
            if p.blank_positions.len() == 0 {
                p.solved = true;
            } else {
                for i in 0..p.blank_positions.len() {
                    p.possibilities
                        .push(alt_get_possibilities(&p.puzz, p.blank_positions[i], &order));
                    p.current_pos.push(-1);
                }
            }
            break;
        }
    }
    p
}

pub fn alt_solve(puzz: Vec<u8>, order: Order) -> PyResult<Vec<u8>> {
    if puzz.len() != 81 {
        return Err(pyo3::exceptions::PyValueError::new_err("A puzzle must have a length of 81!"));
    }

    let mut p = alt_solver_prep(puzz, order);
    if p.solved {
        return Ok(p.puzz);
    }

    let mut position: i8 = 0;
    let max_pos = p.blank_positions.len();
    let mut progressed_forward = true;
    loop {
        if position < 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(format!("The following puzzle is unsolvable!\n{:?}", p.puzz)));
        } else if position == max_pos as i8 {
            p.solved = true;
            return Ok(p.puzz);
        }
        let pos_usize = position as usize;
        let spot = p.blank_positions[pos_usize];
        let max = p.possibilities[pos_usize].len() - 1;
        let mut failed = true;
        if progressed_forward {
            if pos_usize == p.cached_possibilities.len() {
                p.cached_possibilities
                    .push(puzzle_solver::get_possibilities_as_array(&p.puzz, spot as usize));
            } else {
                p.cached_possibilities[pos_usize] =
                    puzzle_solver::get_possibilities_as_array(&p.puzz, spot as usize);
            }
        }
        while p.current_pos[pos_usize] < max as i8 {
            p.current_pos[pos_usize] += 1;
            if p.cached_possibilities[pos_usize]
                [p.possibilities[pos_usize][p.current_pos[pos_usize] as usize] as usize]
            {
                p.puzz[spot as usize] =
                    p.possibilities[pos_usize][p.current_pos[pos_usize] as usize];
                failed = false;
                position += 1;
                progressed_forward = true;
                break;
            }
        }
        if failed {
            p.puzz[spot as usize] = 0;
            p.current_pos[pos_usize] = -1;
            position -= 1;
            progressed_forward = false;
        }
    }
}

fn gen_random_solved() -> Vec<u8> {
    let puzzle: Vec<u8> = vec![0; 81];
    alt_solve(puzzle, RANDOM).unwrap()
}

fn is_legal(puzzle: &Vec<u8>) -> bool {
    puzzle_solver::solve(puzzle.clone()).unwrap() == alt_solve(puzzle.clone(), REVERSE).unwrap()
}

#[pyo3::pyfunction]
pub fn gen_unsolved(num_hints: usize) -> PyResult<Vec<u8>> {

    if num_hints < 23 || num_hints > 40 {
        return Err(pyo3::exceptions::PyValueError::new_err("Please specify a value between 23 and 40 for num_hints."));
    }

    let rng = &mut rand::rng();

    let mut puzzle = gen_random_solved();
    let mut filled: Vec<usize> = (0..81).collect();
    let mut num_filled = 81;

    while num_filled > num_hints {
        if filled.is_empty() {
            println!("Generator got stuck at {} hints! Restarting.", num_filled);
            puzzle = gen_random_solved();
            filled = (0..81).collect();
            num_filled = 81;
        }
        let num = rng.random_range(..filled.len());
        let old = puzzle[filled[num]];
        puzzle[filled[num]] = 0;

        if is_legal(&puzzle) {
            num_filled -= 1;
        } else {
            puzzle[filled[num]] = old;
        }
        filled.remove(num);
    }
    return Ok(puzzle);
}