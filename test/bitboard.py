# Constants for chessboard squares
A1, B1, C1, D1, E1, F1, G1, H1 = 0, 1, 2, 3, 4, 5, 6, 7
A2, B2, C2, D2, E2, F2, G2, H2 = 8, 9, 10, 11, 12, 13, 14, 15
# ... (up to H8)

# Initial position of 8 white pawns
white_pawns_bitboard = (1 << A2) | (1 << B2) | (1 << C2) | (1 << D2) | (1 << E2) | (1 << F2) | (1 << G2) | (1 << H2)

# Function to print the bitboard as a chessboard
def print_chessboard(bitboard):
    for rank in range(7, -1, -1):
        for file in range(0, 8):
            square = rank * 8 + file
            if bitboard & (1 << square):
                print('1', end=' ')
            else:
                print('0', end=' ')
        print()

# Function to move a specific pawn forward by one rank
def move_pawn_forward(bitboard, pawn_square):
    return bitboard ^ (1 << pawn_square) ^ (1 << (pawn_square + 8))

# Move the pawn at square E2 forward by one rank
white_pawns_bitboard = move_pawn_forward(white_pawns_bitboard, E2)

# Print the updated chessboard
print_chessboard(white_pawns_bitboard)
