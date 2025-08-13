mod libraries;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;



#[pymodule]
fn lib_sudoku(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<libraries::puzzle_reader::PuzzleReader>()?;
    m.add_function(wrap_pyfunction!(libraries::puzzle_reader::print_puzz, m)?)?;
    m.add_function(wrap_pyfunction!(libraries::speedtest::synchronous_speedtest, m)?)?;
    m.add_function(wrap_pyfunction!(libraries::speedtest::async_speedtest, m)?)?;
    m.add_function(wrap_pyfunction!(libraries::puzzle_solver::solve, m)?)?;
    m.add_function(wrap_pyfunction!(libraries::puzzle_generator::gen_unsolved, m)?)?;
    Ok(())

}