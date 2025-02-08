import os
import requests
import json
from io import BytesIO
from pdf2docx import Converter

# Token for authentication
TOKEN = "20032|awT3QkqSjixsDW0voWm3A9hUNVFpu4JTzNday3Zz3bb234ad"

# Function to download and save the file, with proper renaming if necessary
def download_file(data, folder_path="BalochistanHighCourt"):
    url = data["FILE_NAME"]
    case_citation = data["caseCitation"].replace("/", "_")  # Replace slashes for a valid filename
    filename = f"{case_citation}.pdf"
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Define the full file path
    file_path = os.path.join(folder_path, filename)

    # Check if the file already exists, if so, append a number to the filename
    counter = 1
    while os.path.exists(file_path):
        filename = f"{case_citation}_{counter}.pdf"
        file_path = os.path.join(folder_path, filename)
        counter += 1

    # Set headers with the token
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # Download the file
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')

        if content_type == 'application/msword':  # If it's a .doc file
            temp_doc_path = os.path.join(folder_path, f"{case_citation}.doc")
            # Save as .doc temporarily
            with open(temp_doc_path, 'wb') as temp_doc:
                temp_doc.write(response.content)
            
            # Convert .doc to .pdf
            convert_doc_to_pdf(temp_doc_path, file_path)
            os.remove(temp_doc_path)  # Clean up the temporary .doc file
            print(f"File downloaded and converted to PDF as {filename}")
        elif content_type == 'application/pdf':  # If it's already a PDF
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded and saved as {filename}")
        else:
            print(f"Unsupported file type for case {case_citation}. Content-Type: {content_type}")
            return data

        # Add the filename to the record
        data["fileName"] = filename
        return data  # Return updated data
    else:
        print(f"Failed to download file for case {case_citation}. Status code: {response.status_code}")
        return data  # Return the record without modification


# Function to convert a .doc file to a .pdf file
def convert_doc_to_pdf(doc_path, pdf_path):
    try:
        # Convert the .doc file to a .pdf file using pdf2docx
        converter = Converter(doc_path)
        converter.convert(pdf_path, start=0, end=None)
        converter.close()
    except Exception as e:
        print(f"Error converting {doc_path} to PDF: {e}")


# Function to process the JSON file with multiple records
def download_files_from_json(json_file, output_file="bloachistanHighCourt4.json"):
    # Read the JSON file
    with open(json_file, 'r') as file:
        records = json.load(file)

    # Loop through each record and download the file
    updated_records = []
    for record in records:
        updated_record = download_file(record)
        updated_records.append(updated_record)

    # Save the updated JSON data with fileName key
    with open(output_file, 'w') as file:
        json.dump(updated_records, file, indent=4)
    print(f"Updated JSON file saved as {output_file}")

# Example usage
json_file = 'bloachistanHighCourt3.json'  # Replace with your actual .json file
download_files_from_json(json_file)
