CREATE TABLE alumni (
    alumniID INT PRIMARY KEY AUTO_INCREMENT,
    fName VARCHAR(100),
    lName VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    DOB DATE,
    gender CHAR(1),
    ethnicity VARCHAR(50),
    website VARCHAR(255),
    linkedIn_link VARCHAR(255),
    twitter_link VARCHAR(255),
    facebook_link VARCHAR(255),
    instagram_link VARCHAR(255),
    guestSpeakerYN CHAR(1),
    newsLetterYN CHAR(1),
    imageThumb VARCHAR(255),
    imageNormal VARCHAR(255),
    description TEXT,
    deceasedYN CHAR(1),
    deceasedDT DATE,
    deceasedNotes TEXT
);

CREATE TABLE address (
    addressID INT PRIMARY KEY AUTO_INCREMENT,
    alumniID INT,
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zipCode VARCHAR(20),
    activeYN CHAR(1),
    primaryYN CHAR(1),
    FOREIGN KEY (alumniID) REFERENCES alumni(alumniID) ON DELETE CASCADE
);

CREATE TABLE employment (
    EID INT PRIMARY KEY AUTO_INCREMENT,
    alumniID INT,
    company VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    jobTitle VARCHAR(100),
    startDate DATE,
    endDate DATE,
    currentYN CHAR(1),
    notes TEXT,
    FOREIGN KEY (alumniID) REFERENCES alumni(alumniID) ON DELETE CASCADE
);

CREATE TABLE skillset (
    SID INT PRIMARY KEY AUTO_INCREMENT,
    alumniID INT,
    skill VARCHAR(100),
    proficiency VARCHAR(50),
    description TEXT,
    FOREIGN KEY (alumniID) REFERENCES alumni(alumniID) ON DELETE CASCADE
);

CREATE TABLE degree (
    degreeID INT PRIMARY KEY AUTO_INCREMENT,
    alumniID INT,
    major VARCHAR(100),
    minor VARCHAR(100),
    graduationDT DATE,
    university VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    FOREIGN KEY (alumniID) REFERENCES alumni(alumniID) ON DELETE CASCADE
);

CREATE TABLE donation (
    donationID INT PRIMARY KEY AUTO_INCREMENT,
    alumniID INT,
    donationAmt FLOAT,
    donationDT DATE,
    reason VARCHAR(255),
    description TEXT,
    FOREIGN KEY (alumniID) REFERENCES alumni(alumniID) ON DELETE CASCADE
);

CREATE TABLE newsLetter (
    id INT PRIMARY KEY AUTO_INCREMENT,
    newsDate DATE,
    headline VARCHAR(255),
    content TEXT,
    category VARCHAR(50),
    author VARCHAR(100),
    imageFilename VARCHAR(255)
);

CREATE TABLE sentTo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    newsletterID INT,
    alumniID INT,
    FOREIGN KEY (newsletterID) REFERENCES newsLetter(id) ON DELETE CASCADE,
    FOREIGN KEY (alumniID) REFERENCES alumni(alumniID) ON DELETE CASCADE
);

CREATE TABLE engagement (
    id INT PRIMARY KEY AUTO_INCREMENT,
    newsletterID INT,
    date DATE,
    recipients INT,
    clicks INT,
    FOREIGN KEY (newsletterID) REFERENCES newsLetter(id) ON DELETE CASCADE
);

CREATE TABLE `user` (
    UID INT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(255),
    fName VARCHAR(100),
    lName VARCHAR(100),
    jobDescription VARCHAR(255),
    viewPriveledgeYN CHAR(1),
    insertPriveledgeYN CHAR(1),
    updatePriveledgeYN CHAR(1),
    deletePriveledgeYN CHAR(1)
);