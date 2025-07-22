
# Team 2 Alumni Engagement Platform

## Prerequisites

- **Python 3.8+** installed and added to your PATH  
- **MySQL Server 8.0** installed and running  

## Setup (Windows)

1. **Initialize the database**

   ```bat
   prep_mysql.bat
   ```
   (Ensure the command prompt is opened in the folder of the project.)
   
2. **Install Python dependencies**

   ```bat
   python -m pip install -r requirements.txt
   ```
   (Ensure the command prompt is opened in the folder of the project.)
   
3. **Seed the data**

   ```bat
   python seed_data.py
   ```
   (Ensure the command prompt is opened in the folder of the project.)
   
4. **Start the server**

   ```bat
   python app.py
   ```
   (Ensure the command prompt is opened in the folder of the project.)
   
5. **Open in your browser**
   Go to:

   ```
   http://localhost:5000
   ```
