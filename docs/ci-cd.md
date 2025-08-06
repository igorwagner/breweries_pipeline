# Continuous Integration & Continuous Deployment (CI/CD)

This project includes automated CI and CD workflows configured using GitHub Actions to ensure code quality and
demonstrate deployment automation.

## Continuous Integration (CI)

- The CI pipeline triggers automatically on every push or pull request to the `main` branch.
- It runs unit tests using `pytest` to verify the correctness and stability of the codebase.
- Dependencies are installed from the `requirements/all.txt` file along with PySpark and pytest.
- This ensures that all code changes are validated before merging or deployment.

## Continuous Deployment (CD)

- A simple CD workflow runs on every push to the `main` branch.
- Instead of deploying to a production environment, it sends a POST request to a configured Discord webhook ([Alerting and Monitoring](docs/alerting-monitoring.md)). 
- This notifies the team that new code has been pushed and validates the CD process.
- The webhook URL must be securely stored as a GitHub secret  (`DISCORD_WEBHOOK_URL`).
- This setup demonstrates automated deployment triggers and can be extended to real deployment steps in the future.

### How to Use

- Ensure your Discord webhook URL is added as a GitHub secret named `DISCORD_WEBHOOK_URL`.
- Push your code to the `main` branch to trigger both CI tests and the CD webhook notification.
- Check the Actions tab in GitHub to monitor workflow runs and results.
