# Intelligent Web Crawler with OpenAI Integration

An intelligent web crawler that combines automated web scraping with OpenAI's language models for enhanced data extraction and understanding.

## Features

- Automated web crawling with intelligent navigation
- OpenAI GPT integration for content analysis
- Smart content extraction and classification
- Automated decision making for crawl paths
- URL management and filtering
- Rate limiting and respectful crawling

## Installation

\\\ash
# Clone the repository
git clone https://github.com/twelve2five/intelligent_crawler.git

# Navigate to the project directory
cd intelligent_crawler

# Install required dependencies
pip install -r requirements.txt

# Set up your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'  # For Unix/Linux
# OR
set OPENAI_API_KEY=your-api-key-here  # For Windows
\\\

## How It Works

### 1. Initialization and Configuration

The crawler combines traditional web scraping with OpenAI's language models for intelligent navigation:

\\\python
from intelligent_crawler import AICrawler
from openai import OpenAI

crawler = AICrawler(
    openai_api_key='your-api-key',
    model='gpt-3.5-turbo',  # or 'gpt-4'
    max_depth=3
)
\\\

### 2. Intelligent Crawling Process

1. **URL Analysis**
   - The crawler first analyzes the target URL structure
   - GPT helps identify important URL patterns and sections

\\\python
# Configure URL analysis
crawler.set_url_analysis(
    priority_patterns=['blog', 'article', 'product'],
    exclude_patterns=['login', 'cart']
)
\\\

2. **Content Extraction**
   - Uses GPT to identify relevant content
   - Automatically extracts structured data

\\\python
# Define extraction parameters
crawler.set_content_extraction({
    'title': 'auto',  # GPT will identify titles
    'main_content': 'auto',
    'metadata': 'auto'
})
\\\

3. **Intelligent Navigation**
   - GPT analyzes page content to decide next crawl targets
   - Prioritizes relevant content based on context

### 3. OpenAI Integration

The crawler uses OpenAI's API in several ways:

1. **Content Understanding**
\\\python
# Example of content analysis
analysis = crawler.analyze_content(
    text=page_content,
    analysis_type='relevance',
    threshold=0.7
)
\\\

2. **Decision Making**
\\\python
# Let GPT decide crawl priority
next_urls = crawler.get_priority_urls(
    current_page=page,
    context=project_context
)
\\\

3. **Data Extraction**
\\\python
# Extract structured data with GPT
structured_data = crawler.extract_with_gpt(
    content=page_content,
    schema={
        'title': 'string',
        'author': 'string',
        'key_points': 'list'
    }
)
\\\

### 4. Rate Limiting and API Usage

The crawler includes smart rate limiting for both web requests and OpenAI API calls:

\\\python
crawler = AICrawler(
    openai_api_key='your-api-key',
    requests_per_second=2,
    openai_requests_per_minute=60,
    cost_limit=5.0  # Maximum USD to spend on API calls
)
\\\

## Usage Examples

### Basic Crawling with AI
\\\python
from intelligent_crawler import AICrawler

# Initialize crawler
crawler = AICrawler(openai_api_key='your-api-key')

# Start crawling with specific focus
results = crawler.crawl(
    start_url='https://example.com',
    focus_topic='AI technology',
    depth=3
)

# Save results
crawler.save_results('output.json')
\\\

### Advanced AI-Powered Extraction
\\\python
# Configure advanced AI extraction
crawler.set_ai_extraction({
    'sentiment_analysis': True,
    'key_topics': True,
    'summary_length': 'medium',
    'language_detection': True
})

# Start crawling with advanced features
results = crawler.crawl_with_analysis('https://example.com')
\\\

## Cost Management

The crawler includes built-in cost management for OpenAI API usage:

- Token counting and estimation
- Cost limits and warnings
- Usage reports and analytics

\\\python
# Get usage report
usage_report = crawler.get_usage_report()
print(f"Total API cost: ")
\\\

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
