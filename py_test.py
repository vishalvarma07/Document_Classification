from werkzeug.datastructures import FileStorage
from classify import search_document_type, extract_text, find_min_positive_index, identify_document_type
import cv2

def test_invalid_document():
    """
    Tests the search_document_type function for invalid document
    """
    text = 'This is a sample text'

    # getting the key indices
    key_indices = search_document_type(text)

    # checking if the key indices are correct
    assert key_indices == [-1,-1,-1]

def test_invalid_file_type():
    """
    Tests the identify_document_type function for invalid file type
    """
    file = open('invalid.txt','w')
    file = FileStorage(file)

    # getting the file type
    file_type = identify_document_type(file)

    # checking if the file type is correct
    assert file_type == 'invalid'

def test_extract_text():
    """
    Tests the extract_text function
    """
    img_file = cv2.imread('sample.png')

    # extracting the text from the image
    text = extract_text(img_file)

    # checking if the text is correct
    assert text == 'google\n'

def test_low_quality_image():
    """
    Tests the search_document_type function for low quality image
    """
    img_file = cv2.imread('sampledocs/philipinvoice.webp')

    # extracting the text from the image
    text = extract_text(img_file)

    # getting the key indices
    key_indices = search_document_type(text)

    # checking if the key indices are correct
    assert key_indices == [-1,-1,-1]