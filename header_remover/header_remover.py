import PySimpleGUI as sg
import os

def main():
    layout = [
        [sg.FilesBrowse()],
        [sg.Button("Convert")]
    ]

    window = sg.Window("CCO File Cleaner", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancel":
            break

        if event == "Convert":
            files = values["Browse"].split(";")
            for f in files:
                file_to_txt(f)

def file_to_txt(filename):
    print(f"Processing {filename}...")

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
