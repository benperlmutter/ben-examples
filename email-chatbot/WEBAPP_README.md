# Email Chatbot Web Application

A comprehensive web interface that combines all four "aug" scripts into a unified dashboard for managing email processing and response generation.

## Features

### 🎯 **Core Functionality**
1. **Update System** - Check for new emails and generate embeddings
2. **View Unanswered Emails** - Browse guest emails that need responses
3. **Generate Responses** - Create AI-powered responses using RAG

### 📊 **Dashboard Features**
- Real-time system statistics
- Email collection metrics
- Embedding coverage tracking
- Recent activity monitoring
- System status indicators

### 🔧 **Interactive Tools**
- One-click email updates
- Filterable email lists
- Response generation with similarity scores
- Auto-refresh capabilities
- Toast notifications for user feedback

## Screenshots

### Dashboard
- System statistics and status
- Action buttons for common tasks
- Real-time metrics and progress tracking

### Unanswered Emails
- List of guest emails needing responses
- Full message preview with expand/collapse
- One-click response generation
- Similarity score display

## Installation

### 1. Prerequisites
```bash
# Ensure you have Python 3.8+ installed
python --version

# Install required packages
pip install -r requirements.txt
```

### 2. Credentials Setup
Ensure these credential files exist:
- `../../../atlas-creds/atlas-creds.json` - MongoDB Atlas
- `../../../azure-gpt-creds/azure-gpt-creds.json` - Azure OpenAI
- `../../../email-chatbot-creds/credentials.json` - Gmail API
- `../../../email-chatbot-creds/token.json` - Gmail OAuth (auto-generated)

### 3. Database Setup
Ensure your MongoDB database has:
- Database: `email_chatbot`
- Collections: `original_emails`, `email_embeddings`
- Vector search index on `message_embeddings` field

## Usage

### Starting the Application
```bash
# Navigate to the email-chatbot directory
cd email-chatbot

# Start the Flask application
python webapp.py
```

The application will be available at: `http://localhost:5000`

### Web Interface

#### Dashboard (`/`)
- **System Statistics**: View email counts, embedding coverage, recent activity
- **Update System**: Check for new emails and generate embeddings
- **Quick Actions**: Access all major functions from one place
- **Auto-refresh**: Statistics update every 30 seconds

#### Unanswered Emails (`/unanswered`)
- **Email List**: View all guest emails needing responses
- **Filtering**: Adjust time range and email limits
- **Message Preview**: Expand/collapse full message content
- **Generate Response**: Create AI responses with one click
- **Similarity Scores**: See how similar conversations influenced the response

### API Endpoints

#### GET `/api/stats`
Returns system statistics in JSON format.

#### POST `/api/update`
Triggers email update and embedding generation.

#### GET `/api/unanswered?days_back=30&limit=20`
Returns list of unanswered emails.

#### POST `/api/generate_response`
Generates response for specific email.
```json
{
  "thread_id": "thread_123",
  "message_id": "msg_456"
}
```

## Configuration

### Application Settings
Edit `webapp.py` to modify:
- Flask host/port settings
- Default filter values
- Auto-refresh intervals
- Batch processing sizes

### UI Customization
Edit templates in `templates/` directory:
- `base.html` - Common layout and navigation
- `index.html` - Dashboard page
- `unanswered.html` - Email list page

### Styling
The application uses Bootstrap 5 with custom CSS for:
- Responsive design
- Card-based layouts
- Interactive elements
- Loading states

## Architecture

### Backend Components
```
webapp.py
├── EmailChatbotService
│   ├── EmailUpdater (aug_update_emails.py)
│   ├── IncrementalEmailEmbeddingGenerator (aug_generate_embeddings.py)
│   └── EmailResponseGenerator (aug_generate_responses.py)
└── Flask Routes
    ├── Dashboard routes
    ├── Email management routes
    └── API endpoints
```

### Frontend Components
```
templates/
├── base.html (Navigation, common JS/CSS)
├── index.html (Dashboard with statistics)
└── unanswered.html (Email list and response generation)
```

### Data Flow
1. **User clicks "Update System"**
2. **Backend calls EmailUpdater.check_for_new_emails()**
3. **Backend calls EmbeddingGenerator.process_new_embeddings()**
4. **Frontend displays results and updates statistics**

## Security Considerations

### Credential Management
- Store credentials outside the web directory
- Use environment variables in production
- Regularly rotate API keys
- Implement proper access controls

### Web Security
- Change the Flask secret key in production
- Use HTTPS in production
- Implement authentication if needed
- Validate all user inputs

### API Security
- Rate limiting for API endpoints
- Input validation and sanitization
- Error handling without information disclosure

## Deployment

### Development
```bash
python webapp.py
# Runs on http://localhost:5000 with debug mode
```

### Production
```bash
# Use a production WSGI server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webapp:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "webapp:app"]
```

## Monitoring

### Application Logs
- Flask logs all requests and errors
- Custom logging for email processing
- Error tracking with stack traces

### Performance Metrics
- Response generation times
- Database query performance
- Memory usage during processing

### Health Checks
- Database connectivity
- API service availability
- Embedding model status

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path and module locations

2. **Database Connection**
   - Verify MongoDB Atlas credentials
   - Check network connectivity
   - Ensure collections exist

3. **API Errors**
   - Validate Azure OpenAI credentials
   - Check API quotas and limits
   - Verify model deployment names

4. **Gmail API Issues**
   - Refresh OAuth tokens
   - Check API permissions
   - Verify credentials.json format

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Browser Console
Check browser console for JavaScript errors and network issues.

## Future Enhancements

### Planned Features
- **User Authentication**: Login system for multiple users
- **Email Sending**: Direct integration to send responses
- **Response Templates**: Predefined response templates
- **Analytics Dashboard**: Advanced metrics and reporting
- **Webhook Integration**: Real-time email notifications
- **Mobile Responsive**: Enhanced mobile experience

### Integration Opportunities
- **CRM Integration**: Connect with customer management systems
- **Calendar Integration**: Automatic event scheduling
- **Notification Systems**: Slack/Teams alerts
- **Workflow Automation**: Zapier/Power Automate integration

## Support

### Documentation
- See `AUG_SYSTEM_OVERVIEW.md` for system architecture
- See `RESPONSE_GENERATION_GUIDE.md` for RAG details
- See individual script documentation for component details

### Getting Help
1. Check the logs for error messages
2. Verify all credentials and connections
3. Test individual components separately
4. Review the troubleshooting section

The web application provides a user-friendly interface to the powerful email processing and response generation capabilities of the "aug" system, making it easy to manage email communications at scale.
