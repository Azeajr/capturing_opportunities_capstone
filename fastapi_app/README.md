## Capturing Opportunities Flask App
Welcome to the Capturing Opportunities Flask App. This application is designed to allow users to upload images, process them using machine learning techniques, and group them accordingly.

## Features
- Upload images for training and collection purposes.
- Process images using a pre-trained MobileNetV3 model and OneClassSVM for anomaly detection.
- View and manage uploaded and processed images through a simple web interface.
## Installation
To set up the project, ensure you have Python 3.11.6 and Poetry package manager installed.

1. Clone the repository:
```bash
git clone https://github.com/Azeajr/capturing_opportunities_capstone.git
cd capturing_opportunities_capstone/fastapi_app
```
2. Install dependencies using Poetry:
```bash
poetry shell
poetry install
```

3. Run the Flask application:
```bash
ENV=dev MODEL=auto_encoder uvicorn main:app --reload 
```
## Usage
After starting the application, navigate to http://localhost:8000 in your web browser to access the application.

- To upload training images, use the form on the main page.
- To upload images to your collection, use the corresponding form.
- Processed images will be displayed on the main page after processing.
## Configuration
The application can be configured for different environments (development, testing, production) by setting the `ENV` variable in `cap_opp/config.py`. Each environment has its own set of configurations.

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

