
use std::fs::File;
use std::io::prelude::*;

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
enum Color {
    Black,
    White
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
enum PieceType {
    King,
    Queen,
    Rook,
    Bishop,
    Knight,
    Pawn,
    None
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
struct Piece {
    color: Color,
    piece_type: PieceType
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
struct Empty {
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
struct Game {
    board: [[Piece; 8]; 8],
    turn: Color,
}

#[derive(Copy, Clone, PartialEq, Hash, Eq)]
struct Coordinate {
    y: u8,
    x: u8
}

#[derive(Copy, Clone, PartialEq, Eq)]
struct Move {
    from: Coordinate,
    to: Coordinate
}

fn coordinate_to_FAN(c: Coordinate) -> String {
    let mut s = String::new();
    s.push_str(&((c.x + 97) as char).to_string());
    s.push_str(&((56 - c.y) as char).to_string());
    s
}

fn string_to_piece(s: String) -> Piece {
    let t_string = &s[0..1];
    let c_string = &s[1..2];

    let t: PieceType = {
        if t_string == "K" {
            PieceType::King
        } else if t_string == "Q" {
            PieceType::Queen
        } else if t_string == "R" {
            PieceType::Rook
        } else if t_string == "B" {
            PieceType::Bishop
        } else if t_string == "N" {
            PieceType::Knight
        } else if t_string == "P" {
            PieceType::Pawn
        } else {
            panic!("Invalid piece type");
        }
    };

    let c = {
        if c_string == "B" {
            Color::Black
        } else if c_string == "W" {
            Color::White
        } else {
            panic!("Invalid color");
        }
    };

    Piece {
        color: c,
        piece_type: t
    }
}

fn piece_to_string(p: Piece) -> String {
    let t_string = {
        if p.piece_type == PieceType::King {
            "K"
        } else if p.piece_type == PieceType::Queen {
            "Q"
        } else if p.piece_type == PieceType::Rook {
            "R"
        } else if p.piece_type == PieceType::Bishop {
            "B"
        } else if p.piece_type == PieceType::Knight {
            "N"
        } else if p.piece_type == PieceType::Pawn {
            "P"
        } else {
            panic!("Invalid piece type");
        }
    };

    let c_string = {
        if p.color == Color::Black {
            "B"
        } else if p.color == Color::White {
            "W"
        } else {
            panic!("Invalid color");
        }
    };

    String::from(t_string) + c_string
}

fn piece_visual(p: Piece) -> String {
    if p.color == Color::Black {
        if p.piece_type == PieceType::King {
            String::from("♚")
        } else if p.piece_type == PieceType::Queen {
            String::from("♛")
        } else if p.piece_type == PieceType::Rook {
            String::from("♜")
        } else if p.piece_type == PieceType::Bishop {
            String::from("♝")
        } else if p.piece_type == PieceType::Knight {
            String::from("♞")
        } else if p.piece_type == PieceType::Pawn {
            String::from("♟")
        } else {
            panic!("Invalid piece type");
        }
    } else if p.color == Color::White {
        if p.piece_type == PieceType::King {
            String::from("♔")
        } else if p.piece_type == PieceType::Queen {
            String::from("♕")
        } else if p.piece_type == PieceType::Rook {
            String::from("♖")
        } else if p.piece_type == PieceType::Bishop {
            String::from("♗")
        } else if p.piece_type == PieceType::Knight {
            String::from("♘")
        } else if p.piece_type == PieceType::Pawn {
            String::from("♙")
        } else {
            panic!("Invalid piece type");
        }
    } else {
        panic!("Invalid color");
    }
}

fn board_visual (board: [[Piece; 8]; 8]) -> String {
    let mut s = String::new();
    for y in 0..(8*3) {
        for x in 0..(8*4) {
            let piece = board[y / 3][x / 4];
            if y % 3 == 1 && x % 4 == 1 && piece.piece_type != PieceType::None {
                s.push_str(&piece_visual(piece));
            } else if (y / 3) % 2 == (x / 4) % 2 {
                s.push_str(" ");
            } else {
                if y % 3 == 1 && x % 4 == 2 && piece.piece_type != PieceType::None {
                    s.push_str(" ");
                } else {
                    s.push_str("█");
                }
            }
        }
        s.push_str("\n");
    }
    s
}

fn board_visual_text (board: [[Piece; 8]; 8]) -> String {
    let mut s = String::new();
    for y_full in 0..((8*3)+2) {
        for x_full in 0..((8*3)+2) {
            if (y_full == 0 || y_full == (8*3)+1) && (x_full == 0 || x_full == (8*3)+1) {
                s.push_str(".");
            }
            else if y_full == 0 || y_full == (8*3)+1 {
                // chess letters
                let x = x_full - 1;
                if x % 3 == 1 {
                    s.push_str(&(((x / 3 + 97) as u8 as char).to_string() + " "));
                } else {
                    s.push_str(" ");
                }
            } else if x_full == 0 || x_full == (8*3)+1 {
                // numbers
                let y = y_full - 1;
                if y % 3 == 1 {
                    let n = 8 - (y / 3);
                    s.push_str(&n.to_string());
                } else {
                    s.push_str(" ");
                }
            } else {
                let y = y_full - 1;
                let x = x_full - 1;
                
                let piece = board[y / 3][x / 3];
                if x % 3 == 1  {
                    if y % 3 == 1 && piece.piece_type != PieceType::None {
                        s.push_str(&piece_to_string(piece));
                    } else if (y / 3) % 2 == (x / 3) % 2 {
                        s.push_str("  ");
                    } else {
                        s.push_str("██");
                    }
                } else if (y / 3) % 2 == (x / 3) % 2 {
                    s.push_str(" ");
                } else {
                    s.push_str("█");
                }
            }
        }
        s.push_str("\n");
    }
    s
}

fn starting_board () -> [[Piece; 8]; 8] {
    let mut board = [[Piece { color: Color::Black, piece_type: PieceType::None }; 8]; 8];

    
    board[0][0] = Piece { color: Color::Black, piece_type: PieceType::Rook };
    board[0][1] = Piece { color: Color::Black, piece_type: PieceType::Knight };
    board[0][2] = Piece { color: Color::Black, piece_type: PieceType::Bishop };
    board[0][3] = Piece { color: Color::Black, piece_type: PieceType::Queen };
    board[0][4] = Piece { color: Color::Black, piece_type: PieceType::King };
    board[0][5] = Piece { color: Color::Black, piece_type: PieceType::Bishop };
    board[0][6] = Piece { color: Color::Black, piece_type: PieceType::Knight };
    board[0][7] = Piece { color: Color::Black, piece_type: PieceType::Rook };

    for x in 0..8 {
        board[1][x] = Piece { color: Color::Black, piece_type: PieceType::Pawn };
    }

    board[7][0] = Piece { color: Color::White, piece_type: PieceType::Rook };
    board[7][1] = Piece { color: Color::White, piece_type: PieceType::Knight };
    board[7][2] = Piece { color: Color::White, piece_type: PieceType::Bishop };
    board[7][3] = Piece { color: Color::White, piece_type: PieceType::Queen };
    board[7][4] = Piece { color: Color::White, piece_type: PieceType::King };
    board[7][5] = Piece { color: Color::White, piece_type: PieceType::Bishop };
    board[7][6] = Piece { color: Color::White, piece_type: PieceType::Knight };
    board[7][7] = Piece { color: Color::White, piece_type: PieceType::Rook };

    for x in 0..8 {
        board[6][x] = Piece { color: Color::White, piece_type: PieceType::Pawn };
    }

    board
}

fn apply_move (board: [[Piece; 8]; 8], m: Move) -> [[Piece; 8]; 8] {
    let mut new_board = board;
    new_board[m.to.y as usize][m.to.x as usize] = new_board[m.from.y as usize][m.from.x as usize];
    new_board[m.from.y as usize][m.from.x as usize] = Piece { color: Color::Black, piece_type: PieceType::None };
    new_board
}


pub fn main() {
    let mut board = starting_board();
    println!("{}", board_visual_text(board));
    board = apply_move(board, Move { from: Coordinate { x: 0, y: 0 }, to: Coordinate { x: 0, y: 1 } });
    println!("{}", board_visual_text(board));
}