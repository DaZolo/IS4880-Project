
# Team 2 Alumni Engagement Platform

## Prerequisites

- **Python 3.8+** installed and added to your PATH  
- **MySQL Server 8.0** installed and running  

## Setup (Windows)

1. **Initialize the database**
   Run the provided batch script to create the `alumni_db` database and all required tables:

   ```bat
   prep_mysql.bat
   ```

2. **Install Python dependencies**

   ```bat
   python -m pip install -r requirements.txt
   ```
   (Ensure the command prompt is opened in the folder of the project.)
   
3. **Start the server**

   ```bat
   python app.py
   ```
   (Ensure the command prompt is opened in the folder of the project.)
   
4. **Open in your browser**
   Go to:

   ```
   http://localhost:5000
   ```
