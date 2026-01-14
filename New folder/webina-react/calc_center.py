
import sys

def get_center(file_path):
    x_sum, y_sum, z_sum = 0.0, 0.0, 0.0
    count = 0
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                try:
                    parts = line.split()
                    # PDBQT atom coordinates are usually in columns 6, 7, 8 (0-indexed: 5, 6, 7) or fixed width
                    # Fixed width is safer: 30-38 (x), 38-46 (y), 46-54 (z)
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    x_sum += x
                    y_sum += y
                    z_sum += z
                    count += 1
                except (ValueError, IndexError):
                    pass
    
    if count > 0:
        print(f"CENTER: {x_sum/count:.3f} {y_sum/count:.3f} {z_sum/count:.3f}")
    else:
        print("CENTER: 0 0 0")

if __name__ == "__main__":
    get_center(sys.argv[1])
