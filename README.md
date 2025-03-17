**Inventory Image Embedding**

**Description**

The Book Cover Detection module in this project leverages image embedding and Optical Character Recognition (OCR) to identify books based on their cover images. Instead of relying on traditional barcode scanning, this approach extracts textual information directly from the book cover, enabling seamless book identification and retrieval of details such as title, author, year, page count and book id.
Technologies used:

Python (version > 13.2)
Tesseract OCR
OpenCV
Pandas
PyQt5

**Pre-requisite:**

Please ensure you have installed python of version 13.2 or above. You can check your python version using the following commands in command prompt
python --version
**Installation Guide:
1. Clone the Repository:**
git clone https://github.com/Anusha806/sdpproject1.git
cd bookdetector


**2. Tesseract SetUp:**


Download and install Tesseract OCR from here


After successful installation open your environmental variables and add the path of the tesseract ocr to your devices Environmental varialbes.


After this step verify the installation by opening command prompt in the location of your tesseract folder and run the following command.


tesseract --version

version of the installed tesseract OCR will be displayed. if the version is not displayed then repeat the above steps carefully once again.

**3. Installation of required dependencies:**


After cloning the project, open the project in an IDE(preferably Visual Studio Code).
Open the project in the terminal and install the dependencies required by using the following commands:

Tesseract OCR:
pip install tesseract
Pandas:
pip install pandas
OpenCV:
pip install opencv-python
PyQt5:
pip install pyqt5

command to install all dependencies at once:

pip install opencv-python pandas pytesseract pyqt5

**4. Run the project**


go to the bookdetector.py file and right click on it , go to "Run python" option and choose "Run python file in terminal" option to run the project.
