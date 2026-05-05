# Hunter Auto 1.0

Autonomous B2B lead generation and cold outreach agent for the Tunisian market.

## Step-by-Step Deployment on Windows

Follow these steps to deploy Hunter Auto 1.0 on a Windows machine.

### Prerequisites

1. **Install Git**: Download and install from [git-scm.com](https://git-scm.com/download/win).
2. **Install Docker Desktop**: 
   - Download from [docker.com](https://www.docker.com/products/docker-desktop/).
   - Ensure WSL 2 (Windows Subsystem for Linux) is enabled during installation.
   - Start Docker Desktop and wait for the engine to be running.
3. **Install VS Code** (Optional, but recommended for editing configs): Download from [code.visualstudio.com](https://code.visualstudio.com/).

### 1. Configure the Project

1. Open PowerShell or Command Prompt.
2. Navigate to the `hunter_auto` directory (or clone it if hosted on a repo).
3. Create your `.env` file:
   - Copy the `.env.example` file and rename it to `.env`.
   - Open `.env` in a text editor (like Notepad or VS Code).
   - Fill in all the API keys and configurations:
     - `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD`
     - `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` (Create an App Password in your Google Account security settings).
     - `TELEGRAM_BOT_TOKEN` (From BotFather) and `TELEGRAM_CHAT_ID`.
     - `GOOGLE_SHEETS_ID` (The ID found in your Google Sheet URL).
     - `HUNTER_IO_API_KEY` (Get a free API key from hunter.io).

### 2. Setup Google Sheets Database

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project, enable the **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account**, generate a JSON key, and download it.
4. Rename the downloaded file to `credentials.json` and place it in the `hunter_auto/config/` directory.
5. Open your Google Sheet, and share it with the email address of the Service Account (it looks like a long email ending in `.iam.gserviceaccount.com`), giving it **Editor** access.
6. Make sure your Google Sheet has two tabs exactly named:
   - `Hunter_Auto_Leads`
   - `Hunter_Auto_Log`
7. Add the column headers in the first row of `Hunter_Auto_Leads`:
   - ID, Company, Name, Title, Phone, Email, LinkedIn URL, Source, Score, Status, Message Sent, Sent At, Notes

### 3. Deploy via Docker Compose

1. Open PowerShell and navigate to the `hunter_auto` folder.
2. Run the following command to build and start the containers:
   ```powershell
   docker-compose up -d --build
   ```
   *(Note: The first run will take several minutes as it downloads image dependencies and Playwright browsers.)*

### 4. Setup Ollama (Local AI)

Ollama is running inside a Docker container, but it needs to pull the `qwen2.5:7b` model on its first run.
1. In PowerShell, run the following command to enter the Ollama container and pull the model:
   ```powershell
   docker exec -it hunter_auto-ollama-1 ollama run qwen2.5:7b
   ```
   *(Note: The container name might differ slightly depending on folder name, if it fails, check the name using `docker ps`)*
2. Once the prompt `>>>` appears, type `/bye` to exit. The model is now cached.
3. *Alternative:* If `docker-compose.yml` has the GPU access enabled, ensure your Nvidia drivers and WSL2 GPU support are working properly, or remove the `deploy` block from `docker-compose.yml` if you do not have a dedicated GPU to fall back to CPU.

### 5. Access the Dashboard

1. Open a web browser (Chrome, Edge, etc.).
2. Go to: [http://localhost:5000](http://localhost:5000)
3. You should see the Hunter Auto Dashboard. From here, you can trigger Scrape or Outreach tasks manually, or leave it running to process automatically.

## Features
- Scrapes Google Maps and LinkedIn for leads.
- Enriches data via company websites.
- Scores leads and generates localized, non-salesy messages via local Ollama.
- Uses Telegram for human handoffs when phone numbers are found.
- Has a complete HTMX dashboard.
