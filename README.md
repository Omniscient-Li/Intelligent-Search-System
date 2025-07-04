# Intelligent Search System

An intelligent product retrieval system that provides real-time, expert advisor-style recommendations for Richelieu hardware products—no local data or deployment required.

## 🎯 Features

- **Real-Time Online Search**: Instantly retrieves product data from Richelieu via Browser-use, no local data required.
- **Expert AI Recommendations**: Professional, scenario-based suggestions using Azure OpenAI.
- **Product Field Completion**: All product results are automatically completed with required fields; missing data is filled with defaults for consistent, structured output (ideal for UI/frontend integration).
- **Professional Recommendation System**: Scenario-based, expert template recommendations with detailed, friendly, and professional advice.
- **User-Friendly CLI**: Simple, interactive command-line interface.
- **No Local Data Needed**: No CSV, no embeddings, no local index—just configure and run.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** (recommended)
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

### Usage

#### Interactive Mode (Default)
```bash
python main.py
```

#### Single Search Query
```bash
python main.py --search "kitchen drawer handle"
```

#### Help
```bash
python main.py --help
```

## 🔧 Commands

When in interactive mode, you can use these commands:

- `exit` - Exit the system
- `mode` - Show current search mode (should be Online-Only)
- `status` - Show system status
- `test` - Run test search

## 📊 Search Mode

### Online-Only Mode (Default)
- **All product data and recommendations are fetched in real time from Richelieu via Browser-use.**
- **No local CSV, embeddings, or index required.**
- **Fast, up-to-date, and zero-maintenance.**

## 🤖 AI Recommendations

The system provides expert advisor-style recommendations that include:

- **Product Analysis**: Detailed specifications and features
- **Installation Guidance**: Requirements and best practices
- **Material Selection**: Professional insights on materials
- **Usage Advice**: Maintenance and care recommendations
- **Personalized Suggestions**: Tailored to user needs
- **Image Preview & Purchase Link**: If available, recommendations include product images (Markdown format) and direct purchase links for easy access
- **Scenario-based & Professional**: Recommendations use a structured, expert template, considering user scenarios, style compatibility, and practical advice
- **Consistent Output**: All recommendations are structured, sectioned, and easy to read for both users and UI integration

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
  "warranty": "Warranty information",
  "source": "Data source (browser-use)",
  "search_query": "Original user query",
  "search_time": "Time taken for search (seconds)"
}
```
All product results are guaranteed to include all fields above; missing or unavailable data is filled with a default value for consistency.

## 🛠️ Configuration

### Environment Variables
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your deployment name
- `AZURE_OPENAI_API_VERSION`: API version

## 📝 Logging

The system provides comprehensive logging:
- **Console Output**: Real-time status and progress
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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<<<<<<< HEAD
**Intelligent Search System** — Making product discovery intelligent, real-time, and friendly! 🚀 
=======
**Intelligent Search System** — Making product discovery intelligent, real-time, and friendly! 🚀 
>>>>>>> ece3943 (feat: unify output to only print results.md content, remove all structured parsing and debug output (align with semantic_search_v2.py))

---

**Intelligent Search System** — Making product discovery intelligent, real-time, and friendly! 🚀 
