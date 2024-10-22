# Hisnul Muslim API

This API provides access to duas (supplications) from the book "Hisnul Muslim" (Fortress of the Muslim). It allows users to retrieve duas organized by chapters, access all duas at once, or get a random dua daily.

## Features

- Retrieve all duas
- Get duas for a specific chapter
- Get a random dua daily
- Rate limiting to prevent abuse
- Error handling for common HTTP status codes

## Installation

0. Bismillah

1. Clone the repository:
   ```
   git clone https://github.com/imranye/hisnul-muslim-api.git
   cd hisnul-muslim-api
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the Flask application:
   ```
   python app.py
   ```

2. The API will be available at `http://localhost:5000/api/v1/`

## API Endpoints

- `GET /api/v1/duas`: Retrieve all duas
- `GET /api/v1/duas/<chapter_id>`: Retrieve duas for a specific chapter
- `GET /api/v1/duadaily`: Retrieve a random dua (inspired by [duadaily.fyi](https://duadaily.fyi))

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 200 requests per day for all endpoints
- 50 requests per hour for all endpoints
- 100 requests per day for the `/api/v1/duas` endpoint
- 200 requests per day for the `/api/v1/duas/<chapter_id>` endpoint
- 200 requests per day for the `/api/v1/duadaily` endpoint

## Error Handling

The API handles common HTTP status codes:
- 404: Not Found
- 429: Rate Limit Exceeded
- 500: Internal Server Error

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Public Access

The API is also publicly hosted. You can access the deployed version at `https://hisnulmuslimapi-94ff7d621ce8.herokuapp.com/`.

Here are the curl commands to interact with the deployed API:

1. Get All Duas:
   ```
   curl -X GET https://hisnulmuslimapi-94ff7d621ce8.herokuapp.com/api/v1/duas
   ```

2. Get Duas for a Specific Chapter (replace `<chapter_id>` with the actual chapter ID):
   ```
   curl -X GET https://hisnulmuslimapi-94ff7d621ce8.herokuapp.com/api/v1/duas/<chapter_id>
   ```

3. Get a Specific Dua from a Specific Chapter (replace `<chapter_id>` and `<dua_id>` with the actual chapter ID and dua ID):
   ```
   curl -X GET https://hisnulmuslimapi-94ff7d621ce8.herokuapp.com/api/v1/duas/<chapter_id>/<dua_id>
   ```

4. Get Dua of the Day:
   ```
   curl -X GET https://hisnulmuslimapi-94ff7d621ce8.herokuapp.com/api/v1/duadaily
   ```

These commands will help you test the different endpoints of the publicly hosted API.
