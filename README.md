
# Alumni Engagement Platform

## Prerequisites

- **Python 3.8+** installed and added to your PATH  
- **MySQL Server** installed and running  
- **Git** (optional, for cloning the repo)

## Setup (Windows)

1. **Clone the repository**  
   ```bat
   git clone https://github.com/your‑username/alumni‑engagement.git
   cd alumni‑engagement
   ```

2. **Initialize the database**
   Run the provided batch script to create the `alumni_db` database and all required tables:

   ```bat
   prep_mysql.bat
   ```

3. **Install Python dependencies**

   ```bat
   python -m pip install -r requirements.txt
   ```

4. **Start the Flask server**

   ```bat
   python app.py
   ```
   (Ensure the command prompt is opened in the folder of the project.)
   
5. **Open in your browser**
   Go to:

   ```
   http://localhost:5000/login
   ```
