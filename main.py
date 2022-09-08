import os
from chess import Chess

def main():
    game : Chess = Chess()
    os.system('cls' if os.name == 'nt' else 'clear')
    game.print_board()



if __name__ == "__main__":
    main()