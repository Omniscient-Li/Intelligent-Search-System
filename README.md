# Intelligent Search System 

An intelligent product retrieval system that combines online search with local semantic search, providing expert advisor-style recommendations for Richelieu hardware products.

## 🎯 Features

- **Hybrid Search**: Combines Browser-use online search with local FAISS semantic search
- **AI Recommendations**: Expert advisor-style recommendations using Azure OpenAI
- **Friendly Interface**: User-friendly CLI with interactive commands
- **Modular Architecture**: Clean, maintainable code structure
- **Robust Fallback**: Local backup when online search fails

## 🏗️ Architecture

```
Intelligent Search System/
├── src/
│   ├── core/                 # Core functionality
│   │   ├── search_engine.py  # Main search orchestrator
│   │   ├── browser_search.py # Browser-use online search
│   │   ├── local_search.py   # Local semantic search
│   │   └── recommendation.py # AI recommendation system
│   ├── utils/                # Utilities
│   │   ├── config.py         # Configuration management
│   │   ├── logger.py         # Logging system
│   │   └── helpers.py        # Helper functions
│   └── ui/                   # User interface
│       └── cli.py           # Command line interface
├── data/                     # Data storage
│   ├── embeddings/          # FAISS embeddings cache
│   └── indexes/             # FAISS index cache
├── config/                   # Configuration files
├── tests/                    # Test files
├── docs/                     # Documentation
├── logs/                     # Log files
├── main.py                   # Main entry point
└── requirements.txt          # Dependencies
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Azure OpenAI API** credentials
3. **Browser-use** for online search

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Intelligent Search System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Copy the example environment file and configure it:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your actual values:
   ```env
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

4. **Prepare data files**
   - Place your CSV product data in the specified path
   - The system will automatically generate embeddings and indexes

### Usage

#### Interactive Mode (Default)
```bash
python main.py
# or
python main.py --interactive
```

#### Single Search Query
```bash
python main.py --search "kitchen drawer handle"
```

#### System Test
```bash
python main.py --test
```

#### Help
```bash
python main.py --help
```

## 🔧 Commands

When in interactive mode, you can use these commands:

- `exit` - Exit the system
- `backup on/off` - Enable/disable local backup search
- `mode` - Show current search mode
- `status` - Show system status
- `test` - Run test search

## 📊 Search Modes

### Hybrid Mode (Default)
- **Online Search**: Real-time data from Richelieu using Browser-use
- **Local Backup**: FAISS semantic search when online fails
- **Best Performance**: Combines speed and reliability

### Online-Only Mode
- **Browser-use Only**: Real-time data from Richelieu
- **No Local Backup**: Faster but less reliable

### Local-Only Mode
- **Local Data Only**: FAISS semantic search
- **Fast Response**: No network dependency

## 🤖 AI Recommendations

The system provides expert advisor-style recommendations that include:

- **Product Analysis**: Detailed specifications and features
- **Installation Guidance**: Requirements and best practices
- **Material Selection**: Professional insights on materials
- **Usage Advice**: Maintenance and care recommendations
- **Personalized Suggestions**: Tailored to user needs

## 🔍 Search Features

### Online Search (Browser-use)
- Real-time product data from Richelieu
- Detailed product information extraction
- Automatic login and navigation
- JSON data parsing and validation

### Local Search (FAISS)
- Semantic search using sentence transformers
- Fast similarity matching
- Cached embeddings and indexes
- Fallback when online search fails

## 📁 Data Structure

### Product Data Format
```json
{
  "name": "Product Name",
  "price": "Price with currency",
  "image_url": "Product image URL",
  "product_url": "Product page URL",
  "description": "Detailed description",
  "sku": "Product SKU",
  "dimensions": "Dimensions information",
  "material": "Material information",
  "finish": "Finish options",
  "installation": "Installation requirements",
  "weight": "Weight information",
  "package_contents": "Package contents",
  "technical_specs": "Technical specifications",
  "certifications": "Certifications",
  "warranty": "Warranty information"
}
```

## 🛠️ Configuration

### Environment Variables
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your deployment name
- `AZURE_OPENAI_API_VERSION`: API version

### Search Configuration
- `max_products`: Maximum products to return (default: 5)
- `enable_backup`: Enable local backup search (default: true)
- `model_name`: Sentence transformer model (default: all-MPNET-base-v2)

## 📝 Logging

The system provides comprehensive logging:

- **Console Output**: Real-time status and progress
- **File Logs**: Detailed logs in `logs/` directory
- **Search Tracking**: Query, results, and timing information
- **Error Handling**: Detailed error messages and stack traces

## 🧪 Testing

Run the system test to verify all components:

```bash
python main.py --test
```

This will:
- Initialize all components
- Perform a test search
- Generate a test recommendation
- Verify system functionality

## 🔧 Development

### Project Structure
- **Modular Design**: Each component is self-contained
- **Clean Interfaces**: Clear API boundaries
- **Error Handling**: Comprehensive exception handling
- **Type Hints**: Full type annotation support

### Adding New Features
1. Create new modules in appropriate directories
2. Follow existing patterns and conventions
3. Add tests for new functionality
4. Update documentation

### Debugging
- Check logs in `logs/` directory
- Use `--test` mode for component verification
- Enable debug logging for detailed information

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the logs for error details
- Review the configuration settings
- Test individual components
- Create an issue with detailed information

## 🔄 Version History

### v2.0
- Complete modular restructuring
- Enhanced AI recommendations
- Improved error handling
- Better user interface
- Comprehensive documentation

### v1.0
- Initial implementation
- Basic search functionality
- Simple recommendations

---

**Intelligent Search System** - Making product discovery intelligent and friendly! 🚀 
