mod libraries;

use libraries::puzzle_reader::PuzzleReader;
use libraries::speedtest;
/*
#[tokio::main]
async fn main() {
    let puzzle_reader: PuzzleReader;
    if std::env::args().count() < 2 {
        println!("No puzzle file argument found, using default.");
        let start_time = std::time::Instant::now();
        puzzle_reader = PuzzleReader::load_puzzles("puzzles.csv".parse().unwrap()).expect("REASON");
        println!(
            "Loaded {} puzzles in {:?}",
            puzzle_reader.size,
            start_time.elapsed()
        );
    } else {
        let start_time = std::time::Instant::now();
        puzzle_reader =
            PuzzleReader::load_puzzles(std::env::args().nth(1).unwrap()).expect("REASON");
        println!(
            "Loaded {} puzzles in {:?}",
            puzzle_reader.size,
            start_time.elapsed()
        );
    }
    speedtest::tokio_speedtest(puzzle_reader.clone());
    speedtest::synchronous_speedtest(puzzle_reader);
}
*/
fn main() {

}