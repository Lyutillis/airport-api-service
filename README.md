# airport-api-service

This app was created to emulate airport system, withdata on airports, flights, airplanes, tickets, crews and orders.

User Data for testing:
    - email: `user@gmail.com`
    - password: `testpassw`

# Lauching project locally

To launch the application, follow next steps:

1. Fork the repository

2. Clone it:
`git clone <here goes the HTTPS link you could copy on github repositiry page>`

3. Create a new branch:
`git checkout -b <new branch name>`

4. Create virtual environment:
`python3 -m venv venv`

5. Acivate venv:
`source venv/Scripts/activate`

6. Install requirements:
`pip3 install -r requirements.txt`

7. Run migrations:
`python3 manage.py migrate`

8. Load the data from fixture:
`python3 manage.py loaddata fixtures/db_data.json`

9. Run server:
`python3 manage.py runserver`

To run the tests:
`python3 manage.py test airport/tests`

# Running with docker

After installing Docker run:
    - docker-compose build
    - docker-compose up
