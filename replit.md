# Overview

This is a Flask-based web service that provides CSV data comparison functionality. The application accepts CSV files containing user data, performs field-by-field comparisons between original and "forced" values, and generates difference reports. The service is designed to identify discrepancies in user profile data fields like email, phone, title, name, and mobile numbers.

**Current Status**: User has completely replaced the original Flask template with a specialized data analysis application that processes CSV files and creates Excel reports with field differences.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask (Python web framework)
- **Processing Engine**: Pandas for data manipulation and analysis
- **File Handling**: Base64 encoding/decoding for CSV data transmission
- **Output Format**: Excel files with styled formatting using openpyxl

## API Design
- RESTful endpoint structure
- JSON request/response format
- POST-based data submission for security and data size considerations

# Key Components

## Data Processing Pipeline
1. **CSV Input Handler**: Accepts base64-encoded CSV data through POST requests
2. **Data Validator**: Parses and validates CSV structure with date parsing for "lastused" column
3. **Data Filter**: Applies 60-day cutoff filter based on "lastused" timestamp
4. **Comparison Engine**: Performs field-by-field comparison between original and forced values
5. **Report Generator**: Creates formatted Excel output with difference highlighting

## Field Comparison Logic
- Compares five predefined field pairs:
  - email vs email-forced
  - phone vs phone-forced
  - title vs title-forced
  - name vs name-forced
  - mobile vs mobile-forced
- Identifies rows where original and forced values differ
- Maintains username and timestamp context for each difference

## Data Filtering Strategy
- **Time-based filtering**: Only processes records with "lastused" within 60 days
- **Null handling**: Excludes records with missing "lastused" values
- **Column selection**: Keeps only essential columns for comparison

# Data Flow

1. Client sends POST request to `/run-diff` with base64-encoded CSV
2. Server decodes and parses CSV into pandas DataFrame
3. System filters data based on 60-day "lastused" cutoff
4. Comparison engine iterates through field pairs to identify differences
5. Results are compiled into a structured differences DataFrame
6. Output is sorted by username for consistent reporting

# External Dependencies

## Python Libraries
- **Flask**: Web framework for HTTP request handling
- **Pandas**: Data manipulation and analysis
- **openpyxl**: Excel file generation and formatting
- **base64**: Data encoding/decoding utilities
- **datetime/timedelta**: Date and time operations

## Data Requirements
- Input CSV must contain "lastused" column with valid date formats
- Expected columns: username, email, phone, title, name, mobile (plus their "-forced" variants)

# Deployment Strategy

## Current State
- Single-file Flask application (main.py)
- No database persistence - stateless processing
- Memory-based data processing suitable for moderate file sizes
- No authentication or session management

## Scalability Considerations
- Stateless design allows for easy horizontal scaling
- Memory usage scales with CSV file size
- No persistent storage requirements
- Suitable for containerized deployment

## Security Notes
- No input sanitization beyond basic CSV parsing
- No authentication mechanism implemented
- Base64 encoding provides basic data transport security
- Consider adding request size limits and rate limiting for production use