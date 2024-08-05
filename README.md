# Helmet-and-Number-Plate-Detection-and-Automated-Notification-using-Email

## Introduction 

This project is a prototype for a helmet detection system. The model detects riders without helmets and the number plates of their vehicles, then sends automated email notifications by fetching rider details from the database.

1. **Helmet Violation Detection**: This component focuses on identifying motorcycle riders who are not wearing helmets. It uses computer vision techniques to analyze real-time camera feeds and instantly alerts authorities when a violation is detected.

2. **Capturing Bike Numbers**: This component recognizes and extracts number plate information from vehicles in real-time, which is valuable for law enforcement.

3. **Sending Email Notifications**: This component sends email notifications to users who violate helmet laws.

4. **Database: Fetching and Storing**: This involves creating tables if they do not exist, and inserting and fetching data from the database.

## Helmet Missing Detection

The helmet missing detection module uses computer vision techniques to:

- Detect faces and riders on motorcycles.
- Determine whether the rider is wearing a helmet.
- Trigger alerts or notifications when a violation is detected.

## Capturing Bike Numbers

The number plate recognition module uses Optical Character Recognition (OCR) techniques to:

- Detect number plates on vehicles.
- Recognize the characters and display the number plate information in real-time.

## Dataset

- Acquired a comprehensive dataset from online sources containing 120 images with complete rider information, including the rider, helmet presence, and visible number plate, and annotated it.

[Dataset](https://www.kaggle.com/datasets/aneesarom/rider-with-helmet-without-helmet-number-plate/data)

## Architecture Used

- YOLO
- PaddleOCR

## Email Notification 

- An email is sent to the rider's email if they are not wearing a helmet, fetching the owner's email from the database.

## Upload Interface, Add Owner/Vehicle, and Display Owner Details 

- Uploading through the interface and displaying the detected rider, person with or without helmet, and number plate.
- Add vehicle/owner details interface for adding new vehicles to the database.
- Search owner details for searching the database.

## Flask Backend

- Implemented backend service using the Flask framework for smooth interaction between the frontend, model, and database.

## Database Setup

- Run the MySQL script to create a database using a shell or Workbench.
- After creating, set up the root name, password, and database name.
- Create tables using the script.

## Usage

- Get the dataset from the above-mentioned link and upload both the train and validation datasets.
- Run `training.py` and, once it is completed, run `main.py` (update the model path to the `best.pt` location in `main.py`).
- The interface opens, allowing you to upload videos from the video folder or any video of your choice.

## Demo of Current Status

- A demo video has been saved in the `DEMO` folder.

### Interface 

![Upload Interface](DEMO/upload.png)

![Add Owner Interface](DEMO/addowner.png)

### Output

![Bike Detection Output](DEMO/bike.gif)

### Alert Notification

![Email Notification](DEMO/notification.jpeg)