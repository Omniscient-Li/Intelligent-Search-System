# Intelligent Product System

## Two-Stage Intelligent Product Retrieval System

A sophisticated two-stage intelligent product retrieval system based on Azure OpenAI and Browser-use, specifically designed for Richelieu hardware products search and recommendation.

## 🏗️ System Architecture

### Stage One: Product Search and Recommendation
**File**: `src/core/dialogue_manager.py`
- Multi-turn dialogue management
- Intelligent keyword extraction and clarification
- Product search using Browser-use (no login required)
- Recommendation of 5 different products with various models/styles/materials (no URLs, names and brief descriptions only)
- Personalized recommendation reasons for each product
- Smart deduplication ensuring diversity

### Stage Two: Product Detailed Information Retrieval
**File**: `src/core/semantic_search.py`
- Retrieve detailed information by product name (no URL needed)
- Automatic login to Richelieu website
- Extract complete product specifications and pricing information

## ✨ System Highlights

- **Two-Stage Separation**: Stage One provides no-login multi-turn dialogue recommendations, Stage Two provides logged-in detailed information retrieval, preventing input contamination
- **Diverse Recommendations**: Stage One always recommends 5 different products with various models/styles/materials, avoiding repetition
- **Personalized Recommendation Reasons**: Each product has personalized recommendation reasons based on user needs and product characteristics
- **No-URL Recommendations**: Stage One doesn't output product URLs for better user experience
- **Smart Deduplication**: Automatically filters duplicate or similar products, ensuring recommendation diversity
- **English/Chinese Input Support**: Automatic translation and keyword extraction
- **Batch Search**: Support for batch processing multiple queries from files
- **Complete Logging**: Colored console output and file logging
- **Structured Configuration**: Modular configuration management

## 📋 Requirements

- Python 3.8+
- Azure OpenAI account
- Internet connection

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp env.example .env
```
Edit the `.env` file with your Azure OpenAI configuration:
```env
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

### 3. Run the System
```bash
# Interactive mode (recommended)
python main.py

# Or specify mode
python main.py --two-stage
```

## 📖 Usage

### Run Complete Two-Stage System
```bash
python main.py --two-stage
```

### Run Stage One (Recommendation System)
```bash
python main.py --search "door handle modern style stainless steel"
```

### Run Stage Two (Detailed Information Retrieval)
```bash
python main.py --details "Modern Steel Pull - 305"
```

### Batch Search
```bash
# Create query file queries.txt
echo "door handle modern style" > queries.txt
echo "kitchen pull stainless steel" >> queries.txt

# Run batch search
python main.py --batch queries.txt
```

### Run System Test
```bash
python main.py --test
```

## 🎯 Command Line Options

- `-h, --help` - Show help information
- `-t, --test` - Run system test
- `-s, --search QUERY` - Perform single search query (Stage One)
- `-d, --details NAME` - Get product details (Stage Two)
- `-2, --two-stage` - Run complete two-stage system
- `-b, --batch FILE` - Batch search (read queries from file)
- `-i, --interactive` - Run interactive CLI (default)

## 📁 Project Structure

```
Intelligent_Product_System_v3/
├── main.py                    # Main entry file
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
├── env.example               # Environment variables example
├── config/
│   └── config.py             # Configuration management
├── src/
│   ├── core/
│   │   ├── dialogue_manager.py    # Stage One: Dialogue management
│   │   ├── semantic_search.py     # Stage Two: Semantic search
│   │   └── two_stage_system.py    # Two-stage system integration
│   ├── utils/
│   │   ├── keyword_extractor.py   # Keyword extraction
│   │   ├── logger.py              # Logging management
│   │   └── helpers.py             # Utility functions
│   ├── ui/                        # User interface modules
│   └── agents/                    # Intelligent agent modules
├── data/                          # Data files
├── logs/                          # Log files
├── tests/                         # Test files
└── docs/                          # Documentation
```

## 📝 Usage Examples

### Stage One Example
```
User: I need modern style kitchen cabinet pulls, stainless steel material
System: What style do you prefer? Modern minimalist, European classical, or other styles?
User: Modern minimalist
System: Here are our recommendations:

1. Modern Stainless Steel Edge Pull - 576
   Recommendation Reason: We recommend the Modern Stainless Steel Edge Pull - 576. This pull features high-quality stainless steel construction, durable and rust-resistant, making it perfect for modern home door applications. Its minimalist modern design with smooth lines integrates beautifully into various modern home environments, enhancing overall space aesthetics. Additionally, the edge pull design is practical and comfortable to use, making it an ideal choice for users who value both quality and aesthetics.

2. Modern Steel Knob - 305
   Recommendation Reason: We recommend the Modern Steel Knob - 305. This knob features high-quality stainless steel construction, durable and corrosion-resistant, easy to clean, making it perfect for modern home door applications. Its minimalist modern design harmonizes with various home styles, enhancing overall space aesthetics. Considering your requirements, this product offers both practicality and beauty.

... (5 products total)
```

### Stage Two Example
```
Please enter product name for detailed information: Modern Steel Pull - 205
Retrieving product detailed information...

【Product Detailed Information】
name: Modern Steel Pull - 205
price: $12.99 CAD
description: High-quality stainless steel material, modern minimalist design...
dimensions: 128mm x 16mm
material: Stainless Steel
...
```

## ⚙️ Configuration

### Environment Variables Configuration
The system supports detailed configuration through environment variables:

- **Azure OpenAI**: API keys, endpoints, deployment names, etc.
- **Browser Settings**: Headless mode, timeout, user agent, etc.
- **Search Settings**: Maximum products, deduplication threshold, search timeout, etc.
- **Logging Settings**: Log level, format, file path, etc.
- **Performance Settings**: Thread count, parallelization, etc.

### Configuration Files
All configurations are managed through `config/config.py`, supporting:
- Type-safe configuration classes
- Automatic environment variable loading
- Default value settings
- Configuration validation

## 🔧 Development Guide

### Adding New Features
1. Add functionality in the appropriate module
2. Update configuration files (if needed)
3. Add test cases
4. Update documentation

### Logging
The system provides complete logging functionality:
- Colored console output
- File logging
- Structured log format
- Different log levels

### Error Handling
- Unified exception handling mechanism
- Detailed error logging
- User-friendly error messages

## 🧪 Testing

### Run Tests
```bash
python main.py --test
```

### Unit Tests
```bash
pytest tests/
```

## 📊 Performance Optimization

- **Async Processing**: All network requests and I/O operations are asynchronous
- **Concurrency Control**: Support for concurrent batch query processing
- **Caching Mechanism**: Intelligent caching to reduce duplicate requests
- **Resource Management**: Automatic resource cleanup and memory management

## 🚨 Important Notes

1. Ensure stable internet connection
2. Ensure Azure OpenAI configuration is correct
3. Stage One completion doesn't automatically proceed to Stage Two
4. Stage Two only requires product name input
5. For batch searches, consider adding appropriate delays between queries

## 🐛 Troubleshooting

- **Module Import Errors**: Check dependency installation
- **Environment Variable Errors**: Check `.env` file configuration
- **Network Connection Issues**: Ensure stable internet connection
- **Browser-use Issues**: Ensure latest version is installed
- **Logging Issues**: Check log file permissions and paths

## 📈 Version History

- **v3.0** - Two-Stage Intelligent Product Retrieval System
  - Added multi-turn dialogue management
  - Added personalized recommendation reason generation
  - Added smart deduplication functionality
  - Added batch search functionality
  - Added complete logging system
  - Added structured configuration management
  - Optimized user experience

- **v2.0** - Intelligent Search System
  - Online search functionality
  - Local semantic search
  - AI recommendation system

- **v1.0** - Basic search functionality

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

**Intelligent Product System** - Making product search smarter, recommendations more precise! 