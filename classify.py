# importing the required modules
from pdf2image import convert_from_bytes
from flask import Flask, jsonify, request
import sys, cv2, pytesseract
from werkzeug.datastructures import FileStorage

app = Flask(__name__)

def search_document_type(text):
    """
    Searches for the document type in the text

    Parameters:
        text (string): text extracted from the image

    Returns:
        list: list of indices of the document type occurences
    """
    # initializing the list of document types
    key_indices = []

    # searching for document type in the text
    # suggested update :- use regex to search for the document type
    key_indices.append(text.find('invoice'))
    key_indices.append(text.find('purchaseorder'))
    key_indices.append(text.find('salesorder'))

    # returning indices of the document type occurences
    return key_indices

def extract_text(img):
    """
    Extracts the text from the image

    Parameters:
        img (numpy.ndarray): image

    Returns:
        string: extracted text
    """
    # extracting the text from the image and converting it to lowercase
    text = pytesseract.image_to_string(img)
    text = text.lower()
    return text

def identify_document_type(document):
    """
    Identifies the type of the document
    
    Parameters:
        document (file): document to be identified
    
    Returns:
        string: type of the document
        invalid: if the document type is invalid
    """
    #document_type = None
    if document != None:
        extension = document.filename.split('.')[-1].lower()
        if extension == 'pdf':
            document_type = 'pdf'

            # converting the pdf to bytes
            # document = document.read()
            document = document.read()
            # converting the bytes to image
            pages = convert_from_bytes(document)
            pages[0].save('page0.jpg', 'JPEG')
        elif extension == 'jpg' or extension == 'jpeg' or extension == 'png' or extension == 'webp':
            document_type = 'image'
            document.save('page0.jpg')
        else:
            document_type = 'invalid'
    return document_type

def find_min_positive_index(list):
    """
    Returns the index of the minimum positive value in the list

    Parameters:
        list (list): list of integers

    Returns:
        int: index of the minimum positive value in the list
        -1: if no positive value is found
    """
    min = sys.maxsize
    min_index = -1
    for i in range(len(list)):
        if list[i] < min and list[i] >= 0:
            min = list[i]
            min_index = i
    return min_index

def check_quality(text):
    """
    Checks the quality of the image

    Parameters:
        text (string): text extracted from the image

    Returns:
        bool: False if the quality of the image is low 
    """
    if len(text) > 40:
        return True
    return False

@app.route('/classify', methods=['POST'])
def classify_document():
    """
    Extracts the text from the document and classifies it into one of the following categories:
    1. Invoice
    2. Purchase Order
    3. Sales Order

    Parameters:
        None
    
    POST Request: 
        description: Upload a document (file) to classify its type.
        responses: 
            200 :
                content:
                    json: file_type (string)
            415 :
                content:
                    json: error (string)

    Returns:
        json: {"file_type": "invoice"/"purchase order"/"sales order"}
    """
    # reading file from request
    document = None
    document = request.files.get('document')
    
    # check document type and store the image
    document_type = identify_document_type(document)

    # return error if document type is invalid
    if document_type == 'invalid':
        if len(list(document.read())) == 0:
            return jsonify({"error": "No file selected"}), 404
        return jsonify({"error": "Invalid document"}), 415

    # cropping the image to the top 1/2th
    img = cv2.imread('page0.jpg')
    height, width = img.shape[:2]
    img = img[:height//2, :]

    # extracting the text from the image and converting it to lowercase
    text = extract_text(img)

    #removing all whitespaces from the text
    text = ''.join(text.split())

    keys = ['invoice', 'purchase order', 'sales order']

    # searching for the document type in the text
    key_indices = search_document_type(text)

    # returning the document type
    min_index = find_min_positive_index(key_indices)
    if min_index == -1:
        if(check_quality(text)):
            return jsonify({"file_type": "supporting document", "document_type": document_type}), 200
        return jsonify({"error": "Invalid Document or Low Quality Image. Please reupload."}), 415
    return jsonify({"file_type": keys[min_index], "document_type": document_type}), 200

if __name__ == '__main__':
    app.run(debug=True)