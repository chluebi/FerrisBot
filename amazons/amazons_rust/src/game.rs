extern crate queues;

use std::io;
use std::collections::HashMap;
use rand::prelude::*;
use queues::*;

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
enum Piece {
    Nothing,
    Black,
    White,
    Arrow,
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
struct Coordinate {
    y: u8,
    x: u8
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
struct Game {
    board: [[Piece; 10]; 10],
    turn: bool,
}

#[derive(Copy, Clone, PartialEq, Eq)]
struct Move {
    from: Coordinate,
    to: Coordinate
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
struct FullMove {
    from: Coordinate,
    to: Coordinate,
    shoot: Coordinate
}

fn int_to_piece(i: u8) -> Piece {
    if i == 0 {
        Piece::Nothing
    } else if i == 1 {
        Piece::White
    } else if i == 2 {
        Piece::Black
    } else if i == 3 {
        Piece::Arrow
    } else {
        println!("Oh no {i}");
        Piece::Nothing
    }
}

fn piece_to_int(piece: Piece) -> u8 {
    if piece == Piece::Nothing {
        0
    } else if piece == Piece::White {
        1
    } else if piece == Piece::Black {
        2
    } else if piece == Piece::Arrow {
        3
    } else {
        0
    }
}

fn opposite_piece(piece: Piece) -> Piece {
    if piece == Piece::White {
        Piece::Black
    } else if piece == Piece::Black {
        Piece::White
    } else {
        Piece::Nothing
    }
}

fn turn_to_piece(turn: bool) -> Piece {
    if turn {
        Piece::White
    } else {
        Piece::Black
    }
}

fn turn_string_to_bool(turn: &str) -> bool {
    if turn == "0" {
        true
    } else {
        false
    }
}

fn full_move_to_move(full_move: FullMove) -> Move {
    Move {
        from: full_move.from,
        to: full_move.to
    }
}

fn full_move_to_shoot_move(full_move: FullMove) -> Move {
    Move {
        from: full_move.to,
        to: full_move.shoot
    }
}

fn game_to_string(game: Game) -> String {
    let mut output_game: String = "".to_owned();


    for y in 0..10 {
        for x in 0..10 {
            let c = piece_to_int(game.board[y][x]);
            let c = c.to_string();
            output_game.push_str(&c);
        }
    }

    let turn = game.turn.to_string();
    output_game.push_str(&turn);

    output_game
}

fn string_to_game(input_game: String) -> Game {
    let mut game = empty_game();

    for y in 0..10 {
        for x in 0..10 {
            let index = 10*y + x;
            let el = &input_game[index..index+1];
            let el = el.parse::<u8>().unwrap();

            game.board[y][x] = int_to_piece(el);
        }
    }

    game
}

fn empty_game() -> Game {
    let game = Game {
        board: [[Piece::Nothing; 10]; 10],
        turn: true
    };

    game
}

fn start_game() -> Game {
    let mut game = empty_game();

    game.board[0][3] = Piece::Black;
    game.board[0][6] = Piece::Black;
    game.board[3][0] = Piece::Black;
    game.board[3][9] = Piece::Black;

    game.board[9][3] = Piece::White;
    game.board[9][6] = Piece::White;
    game.board[6][0] = Piece::White;
    game.board[6][9] = Piece::White;

    game
}

fn find_possible_moves(game: Game, coord: Coordinate) -> Vec<Move> {
    let mut possible_moves: Vec<Move> = vec![];

    for i in 0..3 {
        for j in 0..3 {
            if i == 1 && j == 1 {
                continue;
            }

            let mut k = 1;

            loop {
                let new_y: i8 = coord.y as i8 + (i-1)*k;
                let new_x: i8 = coord.x as i8 + (j-1)*k;

                if new_y < 0 || new_x < 0 || new_y > 9 || new_x > 9 {
                    break;
                }

                let new_y: usize = new_y as usize;
                let new_x: usize = new_x as usize;

                if game.board[new_y][new_x] == Piece::Nothing {
                    let new_y: u8 = new_y as u8;
                    let new_x: u8 = new_x as u8;

                    possible_moves.push(Move {
                        from: coord,
                        to: Coordinate {
                            y: new_y,
                            x: new_x
                        }
                    });
                } else {
                    break;
                }
                k += 1;
            }
        } 
    }

    possible_moves
}

fn is_valid_move(game: Game, move_: Move) -> bool {
    if game.board[move_.from.y as usize][move_.from.x as usize] != turn_to_piece(game.turn) {
        return false;
    }
    if game.board[move_.to.y as usize][move_.to.x as usize] != Piece::Nothing {
        return false;
    }
    let x_diff = move_.to.x as i8 - move_.from.x as i8;
    let y_diff = move_.to.y as i8 - move_.from.y as i8;
    if x_diff.abs() != y_diff.abs() && x_diff.abs() != 0 && y_diff.abs() != 0 {
        return false;
    }
    if x_diff.abs() == 0 && y_diff.abs() == 0 {
        return false;
    }
    let x_sign = if x_diff.abs() == 0 {0 as i8} else {x_diff / x_diff.abs() as i8};
    let y_sign = if y_diff.abs() == 0 {0 as i8} else {y_diff / y_diff.abs() as i8};
    let mut k: i8 = 1;
    while k < x_diff.abs() {
        let new_y: usize = (move_.from.y as i8 + k*y_sign as i8) as usize;
        let new_x: usize = (move_.from.x as i8 + k*x_sign as i8) as usize;
        if game.board[new_y][new_x] != Piece::Nothing {
            return false;
        }
        k += 1;
    }

    true
}

fn is_valid_full_move(game: Game, full_move: FullMove) -> bool {
    let valid_move = is_valid_move(game, full_move_to_move(full_move));
    if !valid_move {
        return false;
    }

    let game_after_move = move_piece(game, Move {
        from: full_move.from,
        to: full_move.to
    });
    let valid_shoot_move = is_valid_move(game_after_move, full_move_to_shoot_move(full_move));

    valid_shoot_move
}

fn move_piece(game: Game, move_: Move) -> Game {
    let mut new_game = game;
    let to_y: usize = move_.to.y as usize;
    let to_x: usize = move_.to.x as usize;
    let from_y: usize = move_.from.y as usize;
    let from_x: usize = move_.from.x as usize;
    new_game.board[to_y][to_x] = game.board[from_y][from_x];
    new_game.board[from_y][from_x] = Piece::Nothing;
    new_game
}

fn play_move(game: Game, move_: FullMove) -> Game {
    if !is_valid_full_move(game, move_) {
        panic!("not a valid full move");
    }

    let mut new_game = game;
    let to_y: usize = move_.to.y as usize;
    let to_x: usize = move_.to.x as usize;
    let from_y: usize = move_.from.y as usize;
    let from_x: usize = move_.from.x as usize;
    let shoot_y: usize = move_.shoot.y as usize;
    let shoot_x: usize = move_.shoot.x as usize;

    new_game.board[to_y][to_x] = game.board[from_y][from_x];
    new_game.board[from_y][from_x] = Piece::Nothing;
    new_game.board[shoot_y][shoot_x] = Piece::Arrow;
    new_game.turn = !new_game.turn;
    new_game
}

fn find_possible_moves_side(game: Game, side: Piece) -> Vec<FullMove> {
    let mut possible_moves: Vec<FullMove> = vec![];

    for y in 0..10 {
        for x in 0..10 {
            if game.board[y][x] == side {
                let y = y as u8;
                let x = x as u8;

                let moves = find_possible_moves(game, Coordinate { y: y, x: x });

                for m in moves {
                    let game_after_move = move_piece(game, m);
                    let arrow_moves = find_possible_moves(game_after_move, m.to);
                    for arrow_move in arrow_moves {
                        possible_moves.push(FullMove {
                            from: m.from,
                            to: m.to,
                            shoot: arrow_move.to
                        });
                    }
                }
            }
        }
    }
    possible_moves
}

struct OverStatus {
    over: bool,
    winner: bool,
}

fn can_move(game: Game, coord: Coordinate) -> bool {
    let mut can_move = false;
    let mut possible_moves = find_possible_moves(game, coord);
    if possible_moves.len() > 0 {
        can_move = true;
    }
    can_move
}


fn is_over(game: Game) -> OverStatus {
    let mut over = OverStatus {
        over: false,
        winner: false,
    };
    let mut possible_moves = find_possible_moves_side(game, Piece::White);
    if possible_moves.len() == 0 {
        over.over = true;
        over.winner = false;
    }
    possible_moves = find_possible_moves_side(game, Piece::Black);
    if possible_moves.len() == 0 {
        over.over = true;
        over.winner = true;
    }
    over
}

fn random_full_move(game: Game, side: Piece) -> FullMove {
    let mut possible_moves = find_possible_moves_side(game, side);
    let mut rng = rand::thread_rng();
    let index = rng.gen_range(0, possible_moves.len());
    possible_moves[index]
}

// print with emoji 
fn print_game(game: Game, last_move: FullMove) {
    println!("");
    for y in 0..10u8 {
        for x in 0..10u8 {
            if y == last_move.shoot.y && x == last_move.shoot.x {
                print!("🔵");
            } else if y == last_move.to.y && x == last_move.to.x {
                if game.turn {
                    print!("⚫");
                } else {
                    print!("⚪");
                }
            } else if y == last_move.from.y && x == last_move.from.x {
                let grid_tile = if (y+x) % 2 == 0  {"🟡"} else {"🟠"};
                print!("{grid_tile}");
            } else {
                let grid_tile = if (y+x) % 2 == 0 {"🟨"} else {"🟧"};
                match game.board[y as usize][x as usize] {
                    Piece::Nothing => print!("{grid_tile}"),
                    Piece::Black => print!("⬛"),
                    Piece::White => print!("⬜"),
                    Piece::Arrow => print!("🟦"),
                }
            }
        }
        println!("");
    }
}

#[derive(Clone, Copy)]
struct CoordinateDistance {
    coord: Coordinate,
    distance: i8,
}

fn distances(game: Game, piece: Piece) -> [[i8; 10]; 10] {
    let mut score : i32 = 0;
    let mut q: Queue<CoordinateDistance> = queue![];
    let mut distances: [[i8; 10]; 10] = [[-1; 10]; 10];

    for y in 0..10 {
        for x in 0..10 {
            if game.board[y][x] == piece {
                q.add(CoordinateDistance {
                    coord: Coordinate { y: y as u8, x: x as u8 },
                    distance: 0,
                });
                distances[y as usize][x as usize] = 0;
            }
        }
    }

    while q.size() > 0 {
        let coordinate_distance = q.remove().unwrap();
        let mut possible_moves = find_possible_moves(game, coordinate_distance.coord);
        for m in possible_moves {
            if distances[m.to.y as usize][m.to.x as usize] == -1 {
                q.add(CoordinateDistance {
                    coord: m.to,
                    distance: coordinate_distance.distance + 1,
                });
                distances[m.to.y as usize][m.to.x as usize] = coordinate_distance.distance + 1;
            }
        }
    }
    distances
}

fn area_control_evaluation(game: Game, piece: Piece) -> i32 {
    let distances_me = distances(game, piece);
    let distances_opponent = distances(game, opposite_piece(piece));

    let mut score = 0;
    for y in 0..10 {
        for x in 0..10 {
            if distances_me[y][x] == -1 && distances_opponent[y][x] != -1 {
                continue;
            } else if distances_me[y][x] != -1 && distances_opponent[y][x] == -1 {
                score += 10;
            } else if distances_me[y][x] == -1 && distances_opponent[y][x] != 1 {
                score -= 10;
            } else {
                score += (distances_opponent[y][x] - distances_me[y][x]) as i32;
            }
        }
    }
    score
}

fn full_evaluation(game: Game, piece: Piece) -> i32 {
    let turn_piece: Piece = turn_to_piece(game.turn);

    let possible_evaluation = (find_possible_moves_side(game, turn_piece).len() as i32) - (find_possible_moves_side(game, opposite_piece(turn_piece)).len() as i32);
    let area_control_evaluation = area_control_evaluation(game, turn_piece) - area_control_evaluation(game, opposite_piece(turn_piece));

    let sum_evaluation =  possible_evaluation + area_control_evaluation;

    if turn_piece == piece {
        sum_evaluation
    } else {
        -sum_evaluation
    }
}


fn basic_AI(game: Game) -> FullMove {
    let piece: Piece = turn_to_piece(game.turn);
    
    let mut best_move: FullMove;
    let mut best_score: usize = 0;

    let possible_moves = find_possible_moves_side(game, piece);
    best_move = possible_moves[0];

    for move_ in possible_moves {
        let game_after_move = play_move(game, move_);
        let possible_moves_after_move = find_possible_moves_side(game_after_move, piece);
        if possible_moves_after_move.len() > best_score {
            best_score = possible_moves_after_move.len();
            best_move = move_;
        }
    }
    
    best_move
}

fn obstruction_AI(game: Game) -> FullMove {
    let piece: Piece = turn_to_piece(game.turn);
    
    let mut best_move: FullMove;
    let mut best_score: usize = 100000;

    let possible_moves = find_possible_moves_side(game, piece);
    best_move = possible_moves[0];

    for move_ in possible_moves {
        let game_after_move = play_move(game, move_);
        let possible_enemy_moves = find_possible_moves_side(game_after_move, opposite_piece(piece));
        if possible_enemy_moves.len() < best_score {
            best_score = possible_enemy_moves.len();
            best_move = move_;
        }
    }
    
    best_move
}

#[derive(Hash, Eq, PartialEq, Clone, Copy)]
struct FullMoveEvaluation {
    full_move: FullMove,
    score: i32,
}

fn obstruction_AI_alpha_beta(game: Game, max_count: usize) -> FullMove {
    let piece: Piece = turn_to_piece(game.turn);

    let depth: u8 = 4;

    let full_move_evaluation = alpha_beta(max_count, game, piece, depth, depth, -100000, 100000, true);
    full_move_evaluation.full_move
}

fn power(x: usize, y: u8) -> usize {
    let mut result = 1;
    for i in 0..y {
        result *= x;
    }
    result
}

fn alpha_beta(max_count: usize, game: Game, piece: Piece, mut depth: u8, mut start_depth: u8, mut alpha: i32, mut beta: i32, maximizing: bool) -> FullMoveEvaluation {
    let turn_piece: Piece = turn_to_piece(game.turn);

    if is_over(game).over {
        if turn_to_piece(is_over(game).winner) == piece {
            return FullMoveEvaluation {
                full_move: FullMove {
                    from: Coordinate {x: 0, y: 0},
                    to: Coordinate {x: 0, y: 0},
                    shoot: Coordinate {x: 0, y: 0},
                },
                score: 100000,
            };
        } else {
            return FullMoveEvaluation {
                full_move: FullMove {
                    from: Coordinate {x: 0, y: 0},
                    to: Coordinate {x: 0, y: 0},
                    shoot: Coordinate {x: 0, y: 0},
                },
                score: -100000,
            };
        }
    }

    let possible_moves = find_possible_moves_side(game, turn_piece);

    while power(possible_moves.len(), start_depth) > max_count && depth > 0 {
        depth -= 1;
        start_depth -= 1;
    }

    if depth <= 0 {
        return FullMoveEvaluation {
            full_move: FullMove {
                from: Coordinate {x: 0, y: 0},
                to: Coordinate {x: 0, y: 0},
                shoot: Coordinate {x: 0, y: 0},
            },
            score: full_evaluation(game, piece),
        };
    }

    if maximizing {
        let mut best_move: FullMove = possible_moves[0];
        let mut best_score: i32 = -100000;
        
        for move_ in possible_moves {
            let game_after_move = play_move(game, move_);
            let next_recursion : FullMoveEvaluation = alpha_beta(max_count, game_after_move, piece, depth - 1, depth, alpha, beta, false);

            if next_recursion.score > best_score {
                best_score = next_recursion.score;
                best_move = move_;
            }
            if next_recursion.score >= beta {
                break
            }

            if next_recursion.score > alpha {
                alpha = next_recursion.score;
            }
        }
        return FullMoveEvaluation {
            full_move: best_move,
            score: best_score,
        };
    } else {
        let mut worst_move: FullMove = possible_moves[0];
        let mut worst_score: i32 = 100000;
        
        for move_ in possible_moves {
            let game_after_move = play_move(game, move_);
            let next_recursion : FullMoveEvaluation = alpha_beta(max_count, game_after_move, piece, depth - 1, depth, alpha, beta, true);

            if next_recursion.score < worst_score {
                worst_score = next_recursion.score;
                worst_move = move_;
            }
            if next_recursion.score <= alpha {
                break
            }

            if next_recursion.score < beta {
                beta = next_recursion.score;
            }
        }
        return FullMoveEvaluation {
            full_move: worst_move,
            score: worst_score,
        };
    }
}

fn obstruction_AI_monte_carlo(game: Game, max_count: usize) -> FullMove {
    let piece: Piece = turn_to_piece(game.turn);

    let full_move_evaluation = monte_carlo(game, piece, max_count, -100000, 100000, true);
    full_move_evaluation.full_move
}

struct EvaluatedFullMove {
    full_move: FullMove,
    game_after: Game,
    score: i32,
}

fn monte_carlo(game: Game, piece: Piece, alloted_count: usize, mut alpha: i32, mut beta: i32, maximizing: bool) -> FullMoveEvaluation {
    let turn_piece: Piece = turn_to_piece(game.turn);
    
    if is_over(game).over {
        if turn_to_piece(is_over(game).winner) == piece {
            return FullMoveEvaluation {
                full_move: FullMove {
                    from: Coordinate {x: 0, y: 0},
                    to: Coordinate {x: 0, y: 0},
                    shoot: Coordinate {x: 0, y: 0},
                },
                score: 100000,
            };
        } else {
            return FullMoveEvaluation {
                full_move: FullMove {
                    from: Coordinate {x: 0, y: 0},
                    to: Coordinate {x: 0, y: 0},
                    shoot: Coordinate {x: 0, y: 0},
                },
                score: -100000,
            };
        }
    }

    let possible_moves = find_possible_moves_side(game, turn_piece);

    if alloted_count <= possible_moves.len() {
        return FullMoveEvaluation {
            full_move: possible_moves[0],
            score: full_evaluation(game, piece)
        };
    }

    let mut sum_score = 0;

    let mut evaluated_possible_moves: Vec<EvaluatedFullMove> = possible_moves.iter().map(|full_move| {
        let game_after_move = play_move(game, *full_move);
        let score = full_evaluation(game_after_move, turn_piece);
        sum_score += score;
        EvaluatedFullMove {
            full_move: *full_move,
            game_after: game_after_move,
            score: score,
        }
    }).collect();

    evaluated_possible_moves.sort_by(|a, b| b.score.cmp(&a.score));

    let mut k: usize = 5;
    let step_size = {
        if evaluated_possible_moves.len() > 1000 {
            2
        } else if evaluated_possible_moves.len() > 500 {
            2
        } else if evaluated_possible_moves.len() > 100 {
            1
        } else if evaluated_possible_moves.len() > 5 {
            0
        } else {
            0
        }
    };
    let mut count_sum = 0;

    if maximizing {
        let mut best_move: FullMove = evaluated_possible_moves[0].full_move;
        let mut best_score: i32 = -100000;

        for move_ in evaluated_possible_moves {
            let new_count = alloted_count/k;
            count_sum += new_count;
            if count_sum > alloted_count || new_count <= 0 {
                break
            }
            k += step_size;

            let game_after_move = move_.game_after;
            let next_recursion : FullMoveEvaluation = monte_carlo(game_after_move, piece, new_count, alpha, beta, false);

            if next_recursion.score > best_score {
                best_score = next_recursion.score;
                best_move = move_.full_move;
            }
            if next_recursion.score >= beta {
                break
            }

            if next_recursion.score > alpha {
                alpha = next_recursion.score;
            }
        }
        return FullMoveEvaluation {
            full_move: best_move,
            score: best_score,
        };
    } else {
        let mut worst_move: FullMove = evaluated_possible_moves[0].full_move;
        let mut worst_score: i32 = 100000;
        
        for move_ in evaluated_possible_moves {
            let new_count = alloted_count/k;
            count_sum += new_count;
            if count_sum > alloted_count || new_count <= 0 {
                break
            }
            k += step_size;

            let game_after_move = move_.game_after;
            let next_recursion : FullMoveEvaluation = monte_carlo(game_after_move, piece, new_count, alpha, beta, true);

            if next_recursion.score < worst_score {
                worst_score = next_recursion.score;
                worst_move = move_.full_move;
            }
            if next_recursion.score <= alpha {
                break
            }

            if next_recursion.score < beta {
                beta = next_recursion.score;
            }
        }
        return FullMoveEvaluation {
            full_move: worst_move,
            score: worst_score,
        };
    }

}

fn obstruction_AI_hybrid(game: Game, max_count: usize) -> FullMove {
    let piece: Piece = turn_to_piece(game.turn);

    let depth: u8 = 4;
    let alpha_beta_full_move_evaluation = alpha_beta(max_count, game, piece, depth, depth, -100000, 100000, true);

    let monte_carlo_full_move_evaluation = monte_carlo(game, piece, max_count/10, -100000, 100000, true);


    if alpha_beta_full_move_evaluation.score > monte_carlo_full_move_evaluation.score {
        alpha_beta_full_move_evaluation.full_move
    } else {
        monte_carlo_full_move_evaluation.full_move
    }
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
struct GamePerspective {
    game: Game,
    piece: Piece,
}

fn obstruction_AI_alpha_beta_hashmap(game: Game, max_count: usize) -> FullMoveEvaluation {
    let mut evaluated: HashMap<GamePerspective, FullMoveEvaluation> = HashMap::new();

    let piece: Piece = turn_to_piece(game.turn);

    let depth: u8 = 4;

    let game_perspective = GamePerspective {
        game: game,
        piece: piece,
    };
    let full_move_evaluation = alpha_beta_hashmap(&mut evaluated, max_count, game_perspective, depth, depth, -100000, 100000, true);
    full_move_evaluation
}


fn alpha_beta_hashmap_wrapper(evaluated: &mut HashMap<GamePerspective, FullMoveEvaluation>, max_count: usize, game_perspective: GamePerspective, mut depth: u8, mut start_depth: u8, mut alpha: i32, mut beta: i32, maximizing: bool) -> FullMoveEvaluation {
    if evaluated.contains_key(&game_perspective) {
        return evaluated[&game_perspective];
    }

    let evaluation = alpha_beta_hashmap(evaluated, max_count, game_perspective, depth, start_depth, alpha, beta, maximizing);
    
    evaluated.insert(game_perspective, evaluation);

    evaluation
}

fn alpha_beta_hashmap(evaluated: &mut HashMap<GamePerspective, FullMoveEvaluation>, max_count: usize, game_perspective: GamePerspective, mut depth: u8, mut start_depth: u8, mut alpha: i32, mut beta: i32, maximizing: bool) -> FullMoveEvaluation {
    let game = game_perspective.game;
    let piece = game_perspective.piece;
    let turn_piece: Piece = turn_to_piece(game.turn);

    if is_over(game).over {
        if turn_to_piece(is_over(game).winner) == piece {
            return FullMoveEvaluation {
                full_move: FullMove {
                    from: Coordinate {x: 0, y: 0},
                    to: Coordinate {x: 0, y: 0},
                    shoot: Coordinate {x: 0, y: 0},
                },
                score: 100000,
            };
        } else {
            return FullMoveEvaluation {
                full_move: FullMove {
                    from: Coordinate {x: 0, y: 0},
                    to: Coordinate {x: 0, y: 0},
                    shoot: Coordinate {x: 0, y: 0},
                },
                score: -100000,
            };
        }
    }

    let possible_moves = find_possible_moves_side(game, turn_piece);

    while power(possible_moves.len(), start_depth) > max_count && depth > 0 {
        depth -= 1;
        start_depth -= 1;
    }

    if depth <= 0 {
        return FullMoveEvaluation {
            full_move: FullMove {
                from: Coordinate {x: 0, y: 0},
                to: Coordinate {x: 0, y: 0},
                shoot: Coordinate {x: 0, y: 0},
            },
            score: full_evaluation(game, piece),
        };
    }

    if maximizing {
        let mut best_move: FullMove = possible_moves[0];
        let mut best_score: i32 = -100000;
        
        for move_ in possible_moves {
            let game_after_move = play_move(game, move_);
            let new_perspective = GamePerspective {
                game: game_after_move,
                piece: piece,
            };
            let next_recursion : FullMoveEvaluation = alpha_beta_hashmap_wrapper(evaluated, max_count, new_perspective, depth - 1, depth, alpha, beta, false);

            if next_recursion.score > best_score {
                best_score = next_recursion.score;
                best_move = move_;
            }
            if next_recursion.score >= beta {
                break
            }

            if next_recursion.score > alpha {
                alpha = next_recursion.score;
            }
        }
        return FullMoveEvaluation {
            full_move: best_move,
            score: best_score,
        };
    } else {
        let mut worst_move: FullMove = possible_moves[0];
        let mut worst_score: i32 = 100000;
        
        for move_ in possible_moves {
            let game_after_move = play_move(game, move_);
            let new_perspective = GamePerspective {
                game: game_after_move,
                piece: piece,
            };
            let next_recursion : FullMoveEvaluation = alpha_beta_hashmap_wrapper(evaluated, max_count, new_perspective, depth - 1, depth, alpha, beta, true);

            if next_recursion.score < worst_score {
                worst_score = next_recursion.score;
                worst_move = move_;
            }
            if next_recursion.score <= alpha {
                break
            }

            if next_recursion.score < beta {
                beta = next_recursion.score;
            }
        }
        return FullMoveEvaluation {
            full_move: worst_move,
            score: worst_score,
        };
    }
}


pub fn play_game() {
    let mut game = start_game();
    let mut over = is_over(game);
    while !over.over {
        let mut turn = game.turn;
        let mut move_;
        if turn {
            move_ = obstruction_AI_alpha_beta_hashmap(game, 10_000);
            game = play_move(game, move_.full_move);
        } else {
            move_ = obstruction_AI_alpha_beta_hashmap(game, 10_000);
            game = play_move(game, move_.full_move);
        }
        println!("Current Evaluation: {}", full_evaluation(game, turn_to_piece(turn)));
        print_game(game, move_.full_move);
        over = is_over(game);
    }
    if over.winner {
        println!("White wins");
    } else {
        println!("Black wins");
    }
}

pub fn read_and_print_move() {
    // read in input
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("Failed to read line");
    // remove characters "["", "]", "," and " "
    input = input.replace("[", "");
    input = input.replace("]", "");
    input = input.replace(",", "");
    input = input.replace(" ", "");

    let turn = &input[0..1];
    let board_string = &input[1..];

    let mut game = string_to_game(board_string.to_string());
    game.turn = turn == "0";

    let full_move_evaluation = obstruction_AI_alpha_beta_hashmap(game, 10_000);
    let move_ = full_move_evaluation.full_move;

    println!("({},{}) ({},{}) ({},{}) My evaluation of this is {}", move_.from.x, move_.from.y, move_.to.x, move_.to.y, move_.shoot.x, move_.shoot.y, full_move_evaluation.score);
}