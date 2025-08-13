use pyo3::{pyfunction, PyResult};
pub(crate) struct Puzzle { 
    pub puzz: Vec<u8>,
    pub blank_positions: Vec<u8>,
    pub possibilities: Vec<Vec<u8>>,
    pub cached_possibilities: Vec<[bool;10]>,
    pub current_pos: Vec<i8>,
    pub solved: bool,
}
pub(crate) fn get_possibilities(puzz: &Vec<u8>, pos: u8) -> Vec<u8> {
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
    
    for i in 1..10 {
        if !seen[i as usize] {
            possibilities.push(i)
        }
    }
    possibilities
}
fn solver_prep(puzz: Vec<u8>) -> Puzzle {
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
            let possibilities = get_possibilities(&p.puzz, *i);
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
                        .push(get_possibilities(&p.puzz, p.blank_positions[i]));
                    p.current_pos.push(-1);
                }
            }
            break;
        }
    }
    p
}

pub(crate) fn get_possibilities_as_array(puzz: &Vec<u8>, pos: usize) -> [bool; 10] {
    let mut seen: [bool; 10] = [true; 10];
    let row: usize = pos / 9;
    let col: usize = pos % 9;
    let root_row = (row / 3) * 3;
    let root_col = (col / 3) * 3;

    for r in root_row..root_row + 3 {
        for c in root_col..root_col + 3 {
            seen[puzz[r * 9 + c] as usize] = false;
        }
    }
    for i in 0..9 {
        seen[puzz[i + (row * 9)] as usize] = false;
        seen[puzz[col + (i * 9)] as usize] = false;
    }
    seen
}
#[pyfunction]
pub fn solve(puzz: Vec<u8>) -> PyResult<Vec<u8>> {
    if puzz.len() != 81 {
        return Err(pyo3::exceptions::PyValueError::new_err("A puzzle must have a length of 81!"));
    }

    let mut p = solver_prep(puzz);
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
                    .push(get_possibilities_as_array(&p.puzz, spot as usize));
            } else {
                p.cached_possibilities[pos_usize] =
                    get_possibilities_as_array(&p.puzz, spot as usize);
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

pub async fn async_solve(puzz: Vec<u8>) -> PyResult<Vec<u8>> {
    solve(puzz)
}
