# Q VEST - IBM Quantum Portfolio Prediction CLI

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-qvest-orange.svg)](https://pypi.org/project/qvest/)

**Q VEST** is a quantum-powered investment portfolio optimization CLI tool that leverages IBM Quantum computers to find optimal asset allocations using advanced quantum algorithms.

## 🚀 Features

- **Quantum-Enhanced Portfolio Optimization**: Uses IBM Quantum computers with QAOA-inspired algorithms
- **Real-Time Market Data**: Fetches live market data from Yahoo Finance
- **Secure API Key Management**: Stores IBM Quantum credentials securely in `~/.qvest/config.json`
- **Interactive CLI**: User-friendly command-line interface with step-by-step guidance
- **Multiple Sectors**: Pre-built portfolios for Tech, Healthcare, Finance, Energy, plus custom options
- **Risk Analysis**: Comprehensive risk metrics and quantum advantage reporting
- **Fallback Support**: Classical optimization backup when quantum resources are unavailable

## 📦 Installation

Install qvest globally using pip:

```bash
pip install qvest
```

## 🔑 Setup

### 1. Get IBM Quantum API Key

1. Visit [IBM Quantum](https://quantum-computing.ibm.com/)
2. Create a free account or sign in
3. Go to your [Account Settings](https://quantum-computing.ibm.com/account/)
4. Copy your API Token

### 2. Configure qvest

On first run, qvest will automatically prompt for your API key:

```bash
qvest
```

Or configure manually:

```bash
qvest config
```

## 🛠 Usage

### Run Portfolio Optimization

```bash
# Start portfolio optimization with interactive prompts
qvest
```

### Configuration Management

```bash
# Show configuration status
qvest config --status

# Update configuration
qvest config --update

# Clear all configuration
qvest config --clear
```

### Command Line Options

```bash
# Show version
qvest --version

# Show help
qvest --help
```

## 🎯 Interactive Workflow

When you run `qvest`, you'll be guided through:

1. **Sector Selection**: Choose from Tech, Healthcare, Finance, Energy, or Custom assets
2. **Risk Level**: Set your risk tolerance (1-10 scale)
3. **Investment Amount**: Enter your investment amount in USD
4. **Time Horizon**: Specify prediction horizon in years
5. **Algorithm Mode**: Choose Pure Quantum or Quantum+Classical optimization

Example session:
```
         ██████╗ ██╗   ██╗███████╗███████╗████████╗
        ██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
        ██║   ██║██║   ██║█████╗  ███████╗   ██║   
        ██║▄▄ ██║╚██╗ ██╔╝██╔══╝  ╚════██║   ██║   
        ╚██████╔╝ ╚████╔╝ ███████╗███████║   ██║   
         ╚══▀▀═╝   ╚═══╝  ╚══════╝╚══════╝   ╚═╝   

                 QVEST BY Minhal Rizvi

        Welcome to Q VEST - Your Quantum Investment Advisor

Please select a market sector:
1. Tech
2. Healthcare
3. Finance
4. Energy
5. Custom
Enter your choice (1-5): 1
Enter risk level (1-10): 7
Enter investment amount (USD): 10000
Enter prediction horizon (years): 5

Select execution mode:
1. Normal (Quantum + classical refinement)
2. Pure Quantum (bitstring allocation only)
Enter your choice (1-2) [2]: 2
```

## 📊 Output

qvest provides comprehensive results including:

- **Portfolio Allocation**: Percentage allocation for each asset
- **Expected Return**: Projected annual return
- **Risk Metrics**: Portfolio volatility and risk analysis
- **Quantum Advantage**: Performance comparison vs classical methods

Example output:
```
✅ Prediction result:
==================================================
🧮 Algorithm: Pure Quantum QAOA
💰 Expected Return: 12.34%
📊 Portfolio Allocation:
   • AAPL: 35.2%
   • MSFT: 28.7%
   • NVDA: 21.1%
   • GOOGL: 15.0%
⚡ Quantum Advantage: 2.3x speedup
==================================================
```

## 🔧 Configuration File

qvest stores configuration in `~/.qvest/config.json`:

```json
{
  "ibm_quantum_token": "your_api_token_here",
  "ibm_quantum_instance": "hub/group/project"
}
```

The file is automatically created with secure permissions (600) on Unix systems.

## 🌐 Supported Assets

### Predefined Sectors

- **Tech**: AAPL, MSFT, NVDA, AMZN, GOOGL
- **Healthcare**: JNJ, PFE, UNH, MRK, ABBV  
- **Finance**: JPM, BAC, GS, WFC, MS
- **Energy**: XOM, CVX, SHEL, TTE, COP

### Custom Assets

Enter any valid stock ticker symbols separated by commas.

## 🔬 Quantum Algorithms

qvest uses quantum optimization algorithms including:

- **QAOA (Quantum Approximate Optimization Algorithm)**: For portfolio optimization
- **Quantum Superposition**: For exploring multiple allocation states simultaneously
- **Quantum Entanglement**: For capturing asset correlations
- **Variational Quantum Eigensolver (VQE)**: For risk-return optimization

## ⚙️ Requirements

- Python 3.8+
- IBM Quantum API Key (free)
- Internet connection for market data

## 🛡 Security

- API keys are stored locally in `~/.qvest/config.json`
- File permissions are set to user-only access (600)
- No sensitive data is transmitted except to IBM Quantum services
- All API calls use secure HTTPS connections

## 🐛 Troubleshooting

### API Key Issues
```bash
# Check configuration status
qvest config --status

# Update API key
qvest config --update
```

### Connection Problems
- Ensure you have an active internet connection
- Verify your IBM Quantum API key is valid
- Check if IBM Quantum services are operational

### Market Data Issues
- qvest automatically falls back to simulated data if Yahoo Finance is unavailable
- Ensure asset tickers are valid (e.g., AAPL, not Apple)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/minhalrizvi/qvest/issues)
- **Documentation**: [README.md](https://github.com/minhalrizvi/qvest/README.md)
- **IBM Quantum**: [quantum-computing.ibm.com](https://quantum-computing.ibm.com/)

## ⚠️ Disclaimer

This tool is for educational and research purposes only. The results should not be considered as financial advice. Always consult with qualified financial advisors before making investment decisions.

---

**Made with ⚡ by Minhal Rizvi**
