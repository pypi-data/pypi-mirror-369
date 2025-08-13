import sys
import csv
import argparse


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Brazil Cup Statistics")
    parser.add_argument("csvfile", nargs="?", help="Path to the CSV file")
    parser.add_argument("--output", help="save results instead of printing")
    return parser.parse_args()


def read_csv_file(filepath):
    """Read the CSV file and return its contents as a list of dictionaries"""
    try:
        with open(filepath, newline="", encoding="utf-8") as csvfile:
            return list(csv.DictReader(csvfile))
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)


def analyze_stats(data):
    """Analyze the player statistics and return a summary"""
    if not data:
        return "No data available."
    try:
        nationalities = {row["Nação"] for row in data if row.get("Nação")}
        total_goals = sum(int(row["Gols"]) for row in data if row.get("Gols", "").isdigit())
        total_assists = sum(int(row["Assis."]) for row in data if row.get("Assis.", "").isdigit())
        summary = [
            f"Unique Nationalities: {len(nationalities)}",
            f"Total goals: {total_goals}",
            f"Total assists: {total_assists}"]
        return "\n".join(summary)
    except KeyError as e:
        return f"Error: missing expected column in CSV file: {e}"


def save_output(text, filepath):
    """Save texts to a file"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Results saved to {filepath}")
    except Exception as e:
        print(f"Error saving file to {filepath}: {e}")


def main():
    args = parse_arguments()
    if not args.csvfile:
        print("Error: You need to provide a CSV file path.")
        print("Use --help for usage instructions")
        sys.exit(1)

    data = read_csv_file(args.csvfile)
    results = analyze_stats(data)

    if args.output:
        save_output(results, args.output)
    else:
        print(results)


if __name__=="__main__":
    main()