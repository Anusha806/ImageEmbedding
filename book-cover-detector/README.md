# Book Cover Detector

This is an OCR based book search tool which can find a book from a give catalog by detecting the title of the book using OCR.


## Using

Have a folder containing your books in the same directory as this Python program is in. The folder location by default is "previewfiles".

## Troubleshooting
This currently uses Tesseract. Make sure you have tesseract installed and if the path is different from /usr/bin, update it accordingly. And have the trained data for your languges installed as well. Change languages in custom_config if you want to experiment with other languages. currently it is set to 'tel' (Telugu). If you want to use a mix of languages, you can change the config to something like 'tel+eng'.

The camera index should be changed based on your preferences (0, 1, or 2 etc) in line #23