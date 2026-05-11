import os

async def process_file(file):
    # Read file contents
    contents = await file.read()

    # Ensure uploads directory exists
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Return metadata
    return {
        "filename": file.filename,
        "size": len(contents),
        "saved_to": file_path
    }
