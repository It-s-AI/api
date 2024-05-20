# API Module

## Overview

This project consists of a FastAPI application that provides an endpoint to query miners in **Subnet32: It's AI** based on certain criteria. The application is defined in `api_module.py` and can be run using the `main.py` script.

## Setup

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before setting up the project, ensure you have the following installed:
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1.	Clone the repository:
```bash
git clone git@github.com:It-s-AI/api.git
```

2.  Navigate to the project directory:
```bash
cd api_module
```

3.  Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

4.  Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Configuration

The configuration for the application is set up using an argument parser in the config function in `api_module.py`. You can modify the default configuration by updating the arguments in this function.

### Arguments

- `--auth_key`: Auth key for authorization.
- `--wallet.name`: coldkey name
- `--wallet.hotkey`: hotkey name
- `--port`: port to run API on
- `--subtensor.chain_endpoint`: ws:// address of your local node

## Running the Application

To run the FastAPI application, use the `main.py` script:
```bash
python3 main.py --auth_key <YOUR_API_KEY> --wallet.name <COLDKEY_NAME> --wallet.hotkey <HOTKEY_NAME> --port 13337
```
This will start the server on `0.0.0.0:13337`. You can access the API at http://0.0.0.0:13337/detect/.

> If you do not specify a port, the server will default to running on port **18889**.

## Usage

### Endpoints

**POST /detect/**  
This endpoint accepts a JSON payload to query axons based on the provided parameters.

**Request Body:**
```json
{
  "text": ["sample text", "another text"],
  "N_AXONS": 10,
  "SORT_TYPE": "uid",
  "TIMEOUT": 3
}
```
- **text**: A list of texts to be processed.
- **N_AXONS**: Number of axons to query (must be between 1 and 256).
- **SORT_TYPE**: The type of sorting to use `[emission, incentive, uid]` .
- **TIMEOUT**: Timeout duration for the query. If you want to query all miners it's better to set this value to 60.

**Response:**  
Responses objects are sorted by **SORT_TYPE** in descending order for "emission" and "incentive". By default it's sorted by UIDs in ascending order.
```json
{
  "responses": [
    {
      "axon1_hotkey": ["prediction1", "prediction2"]
    }
  ]
}
```

## Testing

The `test.py` script is provided to test the functionality of the **/detect/** endpoint.

## Logging

Logs are saved to `app.log` with the format `%(asctime)s - %(levelname)s - %(message)s`.


