@ECHO OFF
SETLOCAL ENABLEEXTENSIONS

SET "MYSQL_EXE="
WHERE mysql.exe >NUL 2>&1 && SET "MYSQL_EXE=mysql"

IF NOT DEFINED MYSQL_EXE (
    IF EXIST "%ProgramFiles%\MySQL\MySQL Server 8.0\bin\mysql.exe" (
        SET "MYSQL_EXE=%ProgramFiles%\MySQL\MySQL Server 8.0\bin\mysql.exe"
    )
)

IF NOT DEFINED MYSQL_EXE (
    IF EXIST "%ProgramFiles(x86)%\MySQL\MySQL Server 8.0\bin\mysql.exe" (
        SET "MYSQL_EXE=%ProgramFiles(x86)%\MySQL\MySQL Server 8.0\bin\mysql.exe"
    )
)

IF NOT DEFINED MYSQL_EXE (
    ECHO [ERROR] MySQL client not found. Install MySQL 8.0 or add mysql.exe to your PATH.
    GOTO END
)

ECHO Using MySQL client at: %MYSQL_EXE%
ECHO.

:ASKUSER
SET /P "ADMIN_USER=Enter MySQL admin username (e.g., root): "
IF "%ADMIN_USER%"=="" (
    ECHO [ERROR] Username cannot be empty.
    GOTO ASKUSER
)
SET /P "ADMIN_PASS=Enter MySQL admin password: "
ECHO.

ECHO === Creating database alumni_db ===
"%MYSQL_EXE%" --user="%ADMIN_USER%" --password="%ADMIN_PASS%" -e "CREATE DATABASE IF NOT EXISTS alumni_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
IF ERRORLEVEL 1 (
    ECHO [ERROR] Failed to create database. Check credentials & MySQL service.
    GOTO END
)

ECHO === Creating user alumni_user@localhost ===
"%MYSQL_EXE%" --user="%ADMIN_USER%" --password="%ADMIN_PASS%" -e "CREATE USER IF NOT EXISTS 'alumni_user'@'localhost' IDENTIFIED BY 'StrongPassword!';"
IF ERRORLEVEL 1 (
    ECHO [ERROR] Failed to create user. Ensure admin can create users.
    GOTO END
)

ECHO === Granting privileges on alumni_db to alumni_user ===
"%MYSQL_EXE%" --user="%ADMIN_USER%" --password="%ADMIN_PASS%" -e "GRANT ALL ON alumni_db.* TO 'alumni_user'@'localhost'; FLUSH PRIVILEGES;"
IF ERRORLEVEL 1 (
    ECHO [ERROR] Failed to grant privileges.
    GOTO END
)

IF NOT EXIST "schema.sql" (
    ECHO [ERROR] schema.sql not found in the current directory.
    GOTO END
)
ECHO === Importing schema from schema.sql ===
"%MYSQL_EXE%" --user="%ADMIN_USER%" --password="%ADMIN_PASS%" alumni_db < "schema.sql"
IF ERRORLEVEL 1 (
    ECHO [ERROR] Failed to import schema. Check schema.sql for errors.
    GOTO END
)

ECHO.
ECHO [SUCCESS] MySQL setup complete!
ECHO   • Database: alumni_db
ECHO   • User:     alumni_user@localhost
ECHO   • Schema:   schema.sql imported

:END
PAUSE
ENDLOCAL