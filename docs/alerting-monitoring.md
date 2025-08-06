# 🔔 Alerting and Monitoring

The project includes basic alerting capabilities for monitoring Airflow DAG failures using a **Discord webhook**.


## 📣 How to Create a Discord Webhook

### 1. Choose the Target Channel
- Open **Discord** and go to the **server** where you have permission to manage channels.
- Hover over the text channel where you want to send messages.
- Click the **gear icon** (⚙️) next to the channel name.

### 2. Go to the "Integrations" Tab
- In the channel settings menu, click on **"Integrations"**.
- Then, click on **"Webhooks"**.

### 3. Create a New Webhook
- Click **"Create Webhook"**.
- Give your webhook a **name**.
- *(Optional)* Upload an **avatar** for the webhook.
- Make sure the **channel** is correct (you can change it).
- Click **“Copy Webhook URL”** — this is the URL you’ll use to send messages via HTTP POST.

## 🚨 Failure Notifications

If any task in a DAG fails, an alert will be sent to a Discord channel with the following structure:

```bash
❌ **DAG `your_dag_id` failed**
Task: `your_task_id`
Execution time: `2025-08-04T12:00:00Z`
🔍 View logs
```

This allows for faster debugging and immediate awareness of issues in the pipeline execution.
## ⚙️ How It Works

- A function named `send_discord_alert` is registered as the `on_failure_callback` of each DAG.
- It constructs a message with DAG name, failed task ID, execution timestamp, and a link to the logs in the Airflow UI.
- The message is posted to a Discord channel via a webhook URL defined as an environment variable (`DISCORD_WEBHOOK_URL`).

✉️ Make sure your `.env` file inside `local_container/` includes:

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url_here
```
✅ This alerting system is designed for **local development monitoring** and can be easily adapted to Slack or email in
production.
