import csv


INPUT_FILE = "data/01_iphone_export.txt"
OUTPUT_FILE = "data/01x_iphone_photos.csv"


def convert_txt_to_csv(input_file: str, output_file: str) -> None:
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    filenames = []
    dates = []
    section = None

    for line in lines:
        line = line.strip()
        if line.startswith("---"):
            section = line.strip("-")
        elif section == "filenames":
            filenames.append(line)
        elif section == "creationTimes":
            dates.append(line)

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["filename", "creationTime"])
        for filename, date in zip(filenames, dates):
            csvwriter.writerow([filename, date])


def main():
    convert_txt_to_csv(INPUT_FILE, OUTPUT_FILE)


if __name__ == "__main__":
    main()
