# RepoSage - AI Pull Request Review Agent

An intelligent code review system that analyzes pull requests from GitHub, GitLab, and Bitbucket using advanced AI to provide comprehensive feedback on code quality, security, performance, and best practices.

## Features

- **Multi-Platform Support**: Works with GitHub, GitLab, and Bitbucket repositories
- **Comprehensive Code Analysis**: Evaluates code structure, standards, bugs, security, performance, and maintainability
- **Quality Scoring System**: Provides A-F grades with detailed metrics for each category
- **Inline Comments**: Line-specific feedback with severity levels
- **Actionable Feedback**: Specific suggestions for code improvements
- **Modern UI**: Professional web interface with real-time analysis
- **Modular Architecture**: Clean Python structure with separation of concerns

## Technology Stack

- **Backend**: Flask (Python 3.11+)
- **AI Engine**: Google Gemini API
- **Git Integration**: GitHub API, GitLab API, Bitbucket API
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Deployment**: Docker support

## Prerequisites

Before running this project, ensure you have:

- Python 3.11 or higher
- At least one of the following:
  - GitHub Personal Access Token
  - GitLab Personal Access Token
  - Bitbucket App Password
- Google Gemini API Key
- pip package manager

## Obtaining API Tokens

### GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `public_repo` (Access public repositories)
4. Copy the generated token

### GitLab Token

1. Go to https://gitlab.com/-/profile/personal_access_tokens
2. Create a new token with scopes:
   - `api` (Access the authenticated user's API)
   - `read_api` (Read-only API access)
   - `read_repository` (Read access to repositories)
3. Copy the generated token

### Bitbucket App Password

1. Go to https://bitbucket.org/account/settings/app-passwords/
2. Click "Create app password"
3. Select permissions:
   - `Repositories: Read`
   - `Pull requests: Read`
4. Copy the generated password

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/RepoSage.git
cd RepoSage
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Git Service Tokens (At least one required)
GITHUB_TOKEN=your_github_personal_access_token
GITLAB_TOKEN=your_gitlab_personal_access_token
BITBUCKET_TOKEN=your_bitbucket_app_password

# AI Configuration (Required)
GEMINI_API_KEY=your_gemini_api_key

# Legacy Configuration (Optional - for CLI tool)
REPO_OWNER=default_owner
REPO_NAME=default_repo
PR_NUMBER=1

# Application Settings
DEBUG=False
PORT=5000
HOST=0.0.0.0

# Performance Settings
MAX_TOKENS=8000
MAX_DIFF_SIZE=50000
REQUEST_TIMEOUT=30

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_MINUTES=1

# Logging
LOG_LEVEL=INFO
```

**Note**: You only need to configure tokens for the platforms you plan to use. At least one git service token is required.

### 5. Run the Application

```bash
python app.py
```

Access the application at `http://localhost:5000`

## Usage

### Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Enter a pull/merge request URL in one of these formats:
   - **GitHub**: `https://github.com/owner/repo/pull/123`
   - **GitLab**: `https://gitlab.com/owner/repo/-/merge_requests/123`
   - **Bitbucket**: `https://bitbucket.org/owner/repo/pull-requests/123`
3. Click "Analyze Pull Request"
4. View the comprehensive analysis with scores and recommendations

### Command Line Interface

For GitHub repositories, edit the `.env` file with your repository details and run:

```bash
python main.py
```

This will analyze the PR specified in the `.env` file and post the review as a comment.

## Supported URL Formats

### GitHub
```
https://github.com/owner/repository/pull/123
https://www.github.com/owner/repository/pull/456
```

### GitLab
```
https://gitlab.com/owner/repository/-/merge_requests/123
https://gitlab.example.com/owner/repository/-/merge_requests/456
```

### Bitbucket
```
https://bitbucket.org/owner/repository/pull-requests/123
```

## API Endpoints

### Health Check
```http
GET /health
```

Returns system status and version information.

### Analyze Pull Request
```http
POST /analyze
Content-Type: application/json

{
  "pull_request_url": "https://github.com/owner/repo/pull/123"
}
```

**Supported URLs**:
- GitHub: `https://github.com/owner/repo/pull/123`
- GitLab: `https://gitlab.com/owner/repo/-/merge_requests/123`
- Bitbucket: `https://bitbucket.org/owner/repo/pull-requests/123`

Returns comprehensive analysis with feedback and metadata.

## Project Structure

```
RepoSage/
├── app.py                  # Flask application and API endpoints
├── config.py               # Configuration management
├── git_services.py         # GitHub API integration
├── analysis_engine.py      # AI-powered code analysis
├── main.py                 # CLI tool for analysis
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface
├── .env                   # Environment variables (create this)
└── README.md              # Project documentation
```

## Configuration Options

### Git Service Tokens

#### GitHub Token

Generate at: https://github.com/settings/tokens

Required scopes:
- `repo` (Full control of private repositories)
- `public_repo` (Access public repositories)

#### GitLab Token

Generate at: https://gitlab.com/-/profile/personal_access_tokens

Required scopes:
- `api` (Access the authenticated user's API)
- `read_api` (Read-only API access)
- `read_repository` (Read access to repositories)

#### Bitbucket App Password

Generate at: https://bitbucket.org/account/settings/app-passwords/

Required permissions:
- `Repositories: Read`
- `Pull requests: Read`

### Gemini API Key

Get your API key at: https://makersuite.google.com/app/apikey

### Rate Limiting

Default: 10 requests per minute per IP address. Adjust in `.env`:

```env
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_MINUTES=1
```

## Analysis Categories

The system evaluates code across six dimensions:

1. **Code Structure** (0-10): Architecture, design patterns, modularity
2. **Standards Compliance** (0-10): Coding conventions, naming, documentation
3. **Bug Detection** (0-10): Logic errors, edge cases, potential crashes
4. **Security Analysis** (0-10): Vulnerabilities, authentication, validation
5. **Performance** (0-10): Efficiency, scalability, resource usage
6. **Maintainability** (0-10): Readability, complexity, testability

Overall Score: 0-100 with letter grade (A-F)

## Docker Deployment

### Build Image

```bash
docker build -t reposage:latest .
```

### Run Container

```bash
docker run -d \
  --name reposage \
  -p 5000:5000 \
  --env-file .env \
  reposage:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  reposage:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    restart: unless-stopped
```

Run with: `docker-compose up -d`

## Testing

Run tests to verify functionality:

```bash
python -m pytest test_app.py -v
```

## Troubleshooting

### Common Issues

**Issue**: `ValueError: At least one git service token is required`
- **Solution**: Ensure `.env` file exists with at least one of: `GITHUB_TOKEN`, `GITLAB_TOKEN`, or `BITBUCKET_TOKEN`

**Issue**: `Failed to fetch pull request diff`
- **Solution**: Verify the PR/MR URL is correct and the repository is accessible with your token
- **GitHub**: Check token has `repo` scope
- **GitLab**: Check token has `read_api` and `read_repository` scopes
- **Bitbucket**: Check app password has `Repositories: Read` permission

**Issue**: `Unsupported git server or invalid URL format`
- **Solution**: Verify URL format matches one of the supported patterns:
  - GitHub: `https://github.com/owner/repo/pull/123`
  - GitLab: `https://gitlab.com/owner/repo/-/merge_requests/123`
  - Bitbucket: `https://bitbucket.org/owner/repo/pull-requests/123`

**Issue**: `API quota exceeded`
- **Solution**: Wait for quota reset or upgrade your Gemini API plan

**Issue**: Rate limit exceeded
- **Solution**: Wait 1 minute or adjust rate limiting settings

**Issue**: `Authentication failed` for specific platform
- **Solution**: 
  - Verify token is valid and not expired
  - Check token permissions/scopes
  - Regenerate token if necessary

## Security Considerations

- Never commit `.env` file to version control
- Add `.env` to `.gitignore`
- Use environment variables for all sensitive data
- Regularly rotate API tokens
- Enable rate limiting in production
- Use HTTPS in production deployments
- Store tokens securely (use secret managers in production)
- Limit token scopes to minimum required permissions

### Token Security Best Practices

**GitHub**:
- Use fine-grained tokens when possible
- Set expiration dates
- Limit to specific repositories

**GitLab**:
- Set token expiration dates
- Use read-only scopes when write access not needed
- Rotate tokens every 90 days

**Bitbucket**:
- Create separate app passwords for different applications
- Use minimum required permissions
- Revoke unused app passwords

## Performance Optimization

- Maximum diff size: 50KB (configurable)
- Request timeout: 30 seconds
- Automatic retry on API failures
- Response caching for repeated requests

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Google Gemini AI for intelligent code analysis
- GitHub API for repository integration
- GitLab API for merge request support
- Bitbucket API for pull request integration
- Flask community for the web framework
- Tailwind CSS for the UI components

## Platform-Specific Notes

### GitHub
- Supports public and private repositories
- Can post review comments directly on PRs
- Rate limit: 5000 requests/hour (authenticated)

### GitLab
- Supports GitLab.com and self-hosted instances
- Custom domain support for self-hosted GitLab
- Rate limit varies by instance configuration

### Bitbucket
- Supports Bitbucket Cloud repositories
- App passwords required (not account passwords)
- Rate limit: 1000 requests/hour per user

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## Changelog

### Version 2.0.0
- Added multi-platform support (GitHub, GitLab, Bitbucket)
- Comprehensive scoring system with A-F grades
- Implemented inline comment feature with severity levels
- Enhanced UI with modern design and platform indicators
- Added rate limiting and security features
- Improved error handling and logging
- Platform auto-detection from URL

### Version 1.0.0
- Initial release
- GitHub integration only
- Basic PR analysis functionality
- Web interface

---

**Built with ❤️ for better code reviews**
