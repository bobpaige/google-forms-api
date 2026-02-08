# Google Forms API Manager

Creates and updates Google Forms from a YAML configuration file with idempotent behavior.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Enable Google Forms API:
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable Google Forms API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials as `credentials.json` in this directory

## Usage

```bash
python forms_manager.py --input-file chapter-1.yml
```

The program will:
- Read the specified YAML file
- Create new forms or update existing ones based on changes
- Store form IDs and hashes in `<basename>_state.json`
- Store authentication token in `<basename>.pickle`
- Only update forms when configuration changes

For example, with `--input-file questions-1.yml`:
- State file: `questions-1_state.json`
- Token file: `questions-1.pickle`

## Files

- YAML configuration file (e.g., `questions.yml`) - Input configuration
- `<basename>_state.json` - Tracks form IDs and hashes (auto-generated)
- `credentials.json` - Google OAuth credentials (you must provide)
- `<basename>.pickle` - Cached authentication token (auto-generated)

### Creating Google Forms API OAuth Credentials

1. **Go to the [Google Cloud Console](https://console.cloud.google.com/)** and select your project, or create a new one if needed.
2. **Enable the Google Forms API** and any other required APIs (like the Google Drive API, if needed to manage associated spreadsheets) for your project in the API Library.
3. **Configure the OAuth consent screen** by specifying an application name and other details.
4. **Go to the Credentials page** and click + **Create Credentials** > **OAuth client ID**.
5. **Select the appropriate Application type** for your project (e.g., "Desktop app" for a local application or "Web application" for a web service).
6. **Provide a name** for your credentials and configure any necessary redirect URIs if you chose "Web application".
7. **Click Create.** A dialog box will appear showing your Client ID and, if applicable, your Client Secret.
8. **Download the JSON file** by clicking the download button (or "DOWNLOAD JSON" button) associated with your newly created credentials.
9. **Save the downloaded file** as `credentials.json` (or a similar name) in your application's working directory, as this file contains the necessary information for your application to authenticate with Google's OAuth 2.0 servers. 

### Important Considerations
- **Security**: The downloaded JSON file contains sensitive information (like client secrets). It must be stored securely and not shared publicly.
- **File Type**: There are different types of credentials (web application, desktop app, service account). Ensure you select the correct type for your application's needs.
- **Scopes**: When implementing the OAuth flow in your code, you will need to specify the correct OAuth 2.0 scopes for the Google Forms API to define the permissions your application requests from the user.
- **Client Libraries**: Google recommends using Google API client libraries as they handle the complexities of the OAuth 2.0 protocol for you. 