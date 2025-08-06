# 🧪 Local Setup Instructions

Follow these steps to set up and run the project locally.

---

## ✅ 1. Install Python with `pyenv`

Make sure you have [pyenv](https://github.com/pyenv/pyenv) installed. Then run:
```bash
pyenv install 3.12.7
```

## ✅ 2. Create a Virtual Environment

Use the Python version installed by pyenv to create a virtual environment:
```bash
~/.pyenv/versions/3.12.7/bin/python3.12 -m venv venv
```

Then activate the environment:
```bash
source venv/bin/activate
```

## ✅ 3. Install Python Dependencies

With the virtual environment activated, install the required Python packages:
```bash
pip install -r requirements/all.txt
```

## ✅ 4. Run Airflow with Docker

📝 You must have Docker installed. If you don't, follow the instructions at: https://docs.docker.com/get-docker/
Navigate to the `local_container` folder and run:
```bash
echo "AIRFLOW_UID=50000" >> .env
docker compose up airflow-init
docker compose up
```
This will start the Airflow webserver and scheduler. If you encounter any issues with the container installation,
check here for details: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

## ✅ 5. Access Airflow UI

Once the services are up, open your browser and go to: `http://localhost:8080`

Login with the following credentials:
- **Username**: airflow
- **Password**: airflow

## ✅ 6. Code Quality: Pre-commit Hooks

To ensure code quality, install pre-commit and enable it:
```bash
pre-commit install
```

From now on, each commit will run the linters, formatters and tests automatically.
