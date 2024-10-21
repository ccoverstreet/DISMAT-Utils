import sys

def main():
    for arg in sys.argv[1:]:
        print(f"Processing {arg}")
        file_to_txt(arg)

def file_to_txt(filename):
    new_name = f"{filename}.txt"

    in_file = open(filename)
    out_file = open(new_name, "w")

    for line in in_file:
        if line.startswith("#"):
            continue
        
        out_file.write(line)

    in_file.close()
    out_file.close()
        

if __name__ == "__main__":
    main()
