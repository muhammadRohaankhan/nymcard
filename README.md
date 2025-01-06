# Nymcard Project

Welcome to the **Nymcard** project! This project serves as a **Confluence Knowledge Assistant**, enabling users to interact seamlessly with Confluence data through a user-friendly interface. The application comprises a **backend** built with Python and Flask, and a **frontend** developed using React and Material-UI.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
   - [1. Clone the Repository](#1-clone-the-repository)
   - [2. Create a Virtual Environment](#2-create-a-virtual-environment)
   - [3. Activate the Virtual Environment](#3-activate-the-virtual-environment)
   - [4. Install Dependencies](#4-install-dependencies)
   - [5. Configure Environment Variables](#5-configure-environment-variables)
   - [6. Set Up Confluence Permissions](#6-set-up-confluence-permissions)
   - [7. Data Ingestion](#7-data-ingestion)
   - [8. Start the API Server](#8-start-the-api-server)
   - [9. CLI-Based Testing](#9-cli-based-testing)
3. [Frontend Setup](#frontend-setup)
   - [1. Navigate to Frontend Directory](#1-navigate-to-frontend-directory)
   - [2. Install Dependencies](#2-install-dependencies)
   - [3. Run the Frontend](#3-run-the-frontend)
   - [4. Refer to Frontend README](#4-refer-to-frontend-readme)
4. [Troubleshooting](#troubleshooting)
5. [Additional Notes](#additional-notes)
6. [Contributing](#contributing)
7. [License](#license)
8. [Contact](#contact)

---

## Prerequisites

Before setting up the project, ensure you have the following installed on your system:

- **Python 3.8+**
- **Node.js 14+** and **npm**
- **Git**

## Backend Setup

The backend of the Nymcard project handles data ingestion from Confluence, processes queries, and serves API endpoints for the frontend.

### 1. Clone the Repository

If you haven't already, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/nymcard_project.git
cd nymcard_project/backend
```

### 2. Create a Virtual Environment

Creating a virtual environment ensures that dependencies are managed separately from your global Python installation.

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

Activate the virtual environment to start using it:

- **On Linux/macOS:**

  ```bash
  source venv/bin/activate
  ```

- **On Windows:**

  ```bash
  venv\Scripts\activate
  ```

### 4. Install Dependencies

Install the required Python packages using `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Environment variables are crucial for configuring sensitive information like API keys.

1. **Locate the Sample Environment File:**

   The sample environment file is located at:

   ```
   ./sample.env
   ```

2. **Copy and Rename the Sample File:**

   ```bash
   cp sample.env .env
   ```

3. **Edit the `.env` File:**

   Open the `.env` file in your preferred text editor and populate it with the correct keys:

   ```bash
   nano .env
   ```

   **Ensure the following variables are correctly set:**

   ```env
   CONFLUENCE_URL=https://your-confluence-instance.atlassian.net
   CONFLUENCE_USERNAME=your-email@example.com
   CONFLUENCE_API_TOKEN=your_confluence_api_token

   OPENAI_API_KEY=your_openai_api_key

   VECTORSTORE_DIRECTORY=./chroma_db
   CONFLUENCE_SPACE_KEY=TD
   ```

   **Notes:**

   - **Relative Paths:** Use relative paths for directories to maintain portability.
   - **API Tokens:** Ensure that `CONFLUENCE_API_TOKEN` and `OPENAI_API_KEY` are valid and have the necessary permissions.

### 6. Set Up Confluence Permissions

Ensure that your Confluence account has the necessary permissions to access and retrieve data from the specified Confluence space.

1. **Generate a Confluence API Token:**

   - Log in to your Atlassian account.
   - Navigate to [API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens).
   - Create a new token and copy it.

2. **Update the `.env` File:**

   Paste the generated token into the `CONFLUENCE_API_TOKEN` field in your `.env` file.

3. **Verify Access:**

   Ensure that the `CONFLUENCE_USERNAME` has access to the Confluence space defined by `CONFLUENCE_SPACE_KEY`.

### 7. Data Ingestion

Populate the vector store and registry with data from Confluence.

1. **Navigate to the Backend Directory:**

   ```bash
   cd /path/to/nymcard_project/backend
   ```

2. **Run the Ingestion Command:**

   ```bash
   python -m nymcard.main --mode ingest
   ```

   **Expected Output:**

   ```
   INFO:core.vectorstore_manager:[INIT_VECTORSTORE] Initializing VectorStore at ./chroma_db
   INFO:core.vectorstore_manager:[INIT_VECTORSTORE] VectorStore initialized successfully.
   INFO:core.confluence_loader:[CONFLUENCE_LOADER] Loading pages from Confluence...
   INFO:core.doc_processor:[DOC_PROCESSOR] Processing page: "Project Aurora Overview"
   INFO:core.doc_registry:[DOC_REGISTRY] Adding document: "Project Aurora Overview"
   INFO:core.vectorstore_manager:[INGEST] Ingesting document: "Project Aurora Overview"
   INFO:core.vectorstore_manager:[INGEST] Successfully ingested 10 documents.
   ```

3. **Verify Ingestion:**

   - **Check `ingested_docs.json`:**

     ```bash
     cat ingested_docs.json
     ```

     **Expected Content:**

     ```json
     [
       {
         "title": "Project Aurora Overview",
         "url": "https://your-confluence-instance.atlassian.net/wiki/spaces/TD/pages/123456789/Project+Aurora+Overview",
         "hash": "unique_hash_1",
         "content": "Detailed content of Project Aurora Overview..."
       },
       ...
     ]
     ```

   - **Check Vector Store Directory:**

     ```bash
     ls chroma_db
     ```

     **Expected Output:**

     ```
     325c5328-adc0-459d-92aa-ab234a91a6cf
     chroma.sqlite3
     chunks/
     metadatas/
     index/
     ```

### 8. Start the API Server

Launch the backend API server to handle frontend requests.

1. **Ensure You're in the Backend Directory and Virtual Environment is Active:**

   ```bash
   cd /path/to/nymcard_project/backend
   source venv/bin/activate
   ```

2. **Run the API Server:**

   ```bash
   python -m nymcard.main --mode api
   ```

   **Expected Output:**

   ```
    * Debug mode: off
   INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on all addresses (0.0.0.0)
    * Running on http://127.0.0.1:5000
    * Running on http://192.168.100.17:5000
   INFO:werkzeug:Press CTRL+C to quit
   ```

3. **Verify the Server is Running:**

   - Open a browser and navigate to [http://localhost:5000/health](http://localhost:5000/health) (assuming you've added a health check endpoint).

   - **Expected Response:**

     ```json
     {
       "status": "OK"
     }
     ```

### 9. CLI-Based Testing

Interact with the backend using the Command Line Interface (CLI) for testing purposes.

1. **Run CLI Mode:**

   ```bash
   python -m nymcard.main --mode cli
   ```

2. **Sample Interaction:**

   ```
   Type 'exit' to quit.

   Ask a question: What are recent incident logs for Project Aurora?
   Answer: Here are the recent incident logs for Project Aurora...

   Ask a question: What is our company's vacation policy?
   Answer: Our company's vacation policy includes...
   ```

## Frontend Setup

The frontend provides a user-friendly interface for interacting with the Confluence Knowledge Assistant.

### 1. Navigate to Frontend Directory

```bash
cd ../frontend
```

### 2. Install Dependencies

Ensure you have **Node.js** and **npm** installed. Then, install the required packages:

```bash
npm install
```

### 3. Run the Frontend

Start the React development server:

```bash
npm start
```

- The application should automatically open in your default browser at [http://localhost:3000](http://localhost:3000).
- If it doesn't, manually navigate to the URL.

### 4. Refer to Frontend README

For more detailed instructions, customization options, and advanced configurations, refer to the frontend's [README.md](./frontend/README.md).

## Troubleshooting

If you encounter issues during setup or while running the application, consider the following troubleshooting steps:

1. **Import Errors:**

   - Ensure that all `__init__.py` files are present in the backend directories.
   - Verify that you're running commands from the correct directory (`backend`).

2. **Environment Variables Not Loaded:**

   - Confirm that the `.env` file is correctly named and placed in `./backend/nymcard/`.
   - Ensure that all required variables are set and have valid values.

3. **Confluence Access Issues:**

   - Verify that your `CONFLUENCE_API_TOKEN` is active and has the necessary permissions.
   - Check your Confluence space key (`CONFLUENCE_SPACE_KEY`) for accuracy.

4. **Frontend Not Loading:**

   - Ensure that the backend API server is running.
   - Check the browser console for any frontend errors.
   - Verify that the frontend is correctly pointing to the backend API (check proxy settings in `frontend/package.json`).

5. **Dependencies Issues:**

   - If you face issues related to missing packages, ensure that you've installed all dependencies in both backend and frontend.

6. **Port Conflicts:**

   - If ports `5000` (backend) or `3000` (frontend) are in use, terminate the conflicting processes or change the application's port configurations.

## Additional Notes

- **Version Control:**
  
  - Ensure that sensitive files like `.env` are listed in `.gitignore` to prevent accidental commits.
  
- **Production Deployment:**
  
  - For deploying the application in a production environment, consider using production-ready servers like **Gunicorn** for the backend and build optimizations for the frontend.
  
- **Security:**
  
  - Always keep your API keys and tokens secure. Avoid hardcoding them into your codebase.
  
- **Scalability:**
  
  - As your project grows, consider integrating scalable vector stores or databases to handle increased data and traffic.
  
- **Feedback and Contributions:**
  
  - Feedback is welcome! If you encounter bugs or have feature requests, please open an issue or submit a pull request.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. **Fork the Project**
2. **Create your Feature Branch**

   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **Commit your Changes**

   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/AmazingFeature
   ```

5. **Open a Pull Request**

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Rohaan Khan - [rohaank67@gmail.com](mailto:rohaank67@gmail.com)

Project Link: [https://github.com/muhammadRohaankhan/nymcard_project](https://github.com/muhammadRohaankhan/nymcard_project)
