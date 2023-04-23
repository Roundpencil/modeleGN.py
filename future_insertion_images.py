from googleapiclient.errors import HttpError


# Yes, you can insert the images backward to avoid messing up the indexes. To do this, you can collect the image
# insertion data first, sort it in descending order based on the startIndex, and then perform the actual image
# insertion. Here's the modified version of the insert_images_to_doc function:
def insert_images_to_doc(drive_service, docs_service, doc_id, name_image_dict):
    try:
        # Get the content of the Google Doc
        doc = docs_service.documents().get(documentId=doc_id).execute()
        content = doc.get('body').get('content')

        image_insertions = []

        for index, item in enumerate(content):
            if 'paragraph' in item:
                elements = item.get('paragraph').get('elements')
                for element in elements:
                    if 'textRun' in element:
                        text = element.get('textRun').get('content')
                        for name, image_id in name_image_dict.items():
                            if name in text:
                                # Get the image's metadata from Google Drive
                                image_metadata = drive_service.files().get(fileId=image_id, fields="mimeType").execute()
                                image_mime_type = image_metadata.get('mimeType')

                                image_insertions.append({
                                    'startIndex': element.get('startIndex'),
                                    'name': name,
                                    'image_id': image_id
                                })

                                # Remove the name-image pair from the dictionary to avoid duplicate insertions
                                del name_image_dict[name]
                                break

        # Sort the image_insertions list in descending order based on startIndex
        image_insertions.sort(key=lambda x: x['startIndex'], reverse=True)

        # Insert images into the Google Doc
        for image_insertion in image_insertions:
            requests = [{
                'insertInlineImage': {
                    'location': {
                        'index': image_insertion['startIndex']
                    },
                    'uri': f'https://drive.google.com/uc?id={image_insertion["image_id"]}',
                    'objectSize': {
                        'height': {
                            'magnitude': 300,
                            'unit': 'PT'
                        },
                        'width': {
                            'magnitude': 200,
                            'unit': 'PT'
                        }
                    }
                }
            }]
            docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
            print(f"Image '{image_insertion['name']}' inserted into the document.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        doc = None

    return doc
