import os
import csv
import argparse


def scan_folder_and_write_csv(input_folder, output_folder):
    # Specify the data folder used to mount into the docker container
    parent_folder = "/images"

    # Create a list to store image file paths
    image_filepaths = []

    # Iterate through files in the specified folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            # Create the full filepath
            filepath = os.path.join(parent_folder, filename)

            # Append the filepath to the list
            image_filepaths.append([filepath])

    print(image_filepaths)

    # Write the list to a CSV file
    csv_filename = "stdin.csv"
    csv_filepath = os.path.join(os.path.abspath(output_folder), csv_filename)
    with open(csv_filepath, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(image_filepaths)

    print(f"CSV file '{csv_filename}' created successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan a folder for images and create a CSV file with their file paths."
    )
    parser.add_argument(
        "--img_folder",
        type=str,
        required=True,
        help="Path to the folder containing images.",
    )

    parser.add_argument(
        "--output_folder",
        type=str,
        required=False,
        default="../local_test/test_stdin/",
        help="Path to the folder to store your generated stdin",
    )

    args = parser.parse_args()
    input_folder = args.img_folder
    output_folder = args.output_folder

    scan_folder_and_write_csv(input_folder, output_folder)
