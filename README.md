# Django API: Fuel Route Optimization

## Overview
This project is a Django-based REST API that calculates the optimal route between two locations in the USA, minimizing fuel costs based on vehicle parameters and real-world fuel prices. The API uses external geocoding and routing services and processes a provided CSV file of fuel prices to determine the most cost-effective fuel stops along the route.

---

## Features
- Calculate the optimal route from start to finish.
- Determine the cheapest fuel stops based on a maximum vehicle range of 500 miles.
- Calculate total fuel cost assuming 10 miles per gallon fuel efficiency.
- Fetch real-time routing and geocoding information using an external API.

---

## Prerequisites
- **Python 3.10+**
- **Docker** and **Docker Compose**
- External API key (e.g., OpenRouteService)
- Fuel prices CSV file (provided as `fuel-prices-for-be-assessment.csv`)

---

## Installation
### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set Up the Environment Variables
Create a `.env` file in the project root with the following:
```env
API_KEY=your-api-key
```
Replace `your-api-key` with your API key from the routing/geocoding service (e.g., OpenRouteService).

### 3. Build and Run the Docker Containers
```bash
docker-compose up --build
```
This will:
- Install the required dependencies from `requirements.txt`.
- Start the Django development server on `http://localhost:8000`.

---

## Usage
### API Endpoints
#### **1. Calculate Optimal Route**
**Endpoint**: `/api/get-route/`

**Method**: `GET`

**Query Parameters**:
- `start`: The starting location.
- `finish`: The destination.

**Example Request**:
```bash
curl "http://localhost:8000/api/get-route/?start=<your-start-location>&finish=<your-finish-location>"
```

**Response**:
```json
{
  "optimal_route": { ... },
  "total_cost": 123.45,
  "fuel_stops": [
    {
      "name": "Station A",
      "price": 4.30,
      "location": [37.7749, -122.4194]
    },
    {
      "name": "Station B",
      "price": 4.20,
      "location": [36.7783, -119.4179]
    }
  ],
  "distance_miles": 383.12
}
```

### Testing the API
Use tools like **Postman**, **curl**, or a browser to test the API endpoints.

---

## File Structure
```plaintext
project-root/
├── FuelRouteAPI/            # Main Django application
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI entry point
├── route/                   # Custom app for route and fuel logic
│   ├── views.py             # API views
│   ├── services.py          # Core business logic
│   └── urls.py              # App-specific URLs
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── Dockerfile               # Docker build file
├── docker-compose.yml       # Docker Compose configuration
└── README.md                # Project documentation
```

---

## Development
### Running Locally
To run the project locally without Docker:
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python manage.py runserver
   ```

---


## Acknowledgments
- **Django REST Framework** for providing an excellent API framework.
- **OpenRouteService** for routing and geocoding APIs.
- **Pandas** and **NumPy** for data processing.

