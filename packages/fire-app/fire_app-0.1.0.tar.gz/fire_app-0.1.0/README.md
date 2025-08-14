# Fire App 🔥

A modern, beautiful personal finance tracker built with PySide6. Track your net worth, assets, liabilities, and cash flow with an intuitive dashboard interface.

![Fire App Preview](https://via.placeholder.com/800x400/1a1a2e/ffffff?text=Fire+App+Dashboard+Preview)

## ✨ Features

- **📊 Comprehensive Dashboard**: Get a complete overview of your financial health
- **💰 Net Worth Tracking**: Monitor your net worth growth over time with interactive charts  
- **🏦 Asset Management**: Track cash, investments, crypto, properties, and vehicles
- **📈 Investment Portfolio**: Monitor your investment accounts and performance
- **💳 Liability Tracking**: Keep track of loans, credit cards, and other debts
- **💸 Cash Flow Analysis**: Visualize income vs expenses by category
- **🌙 Modern Dark Theme**: Beautiful, eye-friendly interface
- **⚡ Fast & Responsive**: Built with PySide6 for native performance

## 🚀 Installation

### From PyPI

```bash
pip install fire-app
```

### From Source

```bash
git clone https://github.com/ijimenez/fire-app.git
cd fire-app
pip install -e .
```

## 🖥️ Usage

### GUI Application

Launch the graphical interface:

```bash
fire-app
```

Or from Python:

```python
from fire_app import main
main()
```

### Command Line

```bash
fire-app-cli
```

## 📋 Requirements

- Python 3.8+
- PySide6 >= 6.5.0

## 🛠️ Development

### Setting up for Development

1. Clone the repository:
   ```bash
   git clone https://github.com/ijimenez/fire-app.git
   cd fire-app
   ```

2. Install in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run the application:
   ```bash
   python -m fire_app.main
   ```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
isort src/
```

### Linting

```bash
flake8 src/
```

## 🎨 Screenshots

### Main Dashboard
- **Net Worth Chart**: Track your financial progress over time
- **Asset Allocation**: Visual breakdown of your asset portfolio
- **Liability Overview**: Monitor debts and obligations

### Features Overview
- Real-time data updates
- Interactive charts and graphs
- Customizable categories
- Export capabilities
- Multi-currency support (coming soon)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Ismael Jimenez**

- GitHub: [@ijimenez](https://github.com/ijimenez)
- Email: ismael@example.com

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) for the amazing Qt framework
- Inspired by modern fintech applications
- Thanks to the open-source community

## 📊 Project Status

Fire App is currently in active development. We're working on:

- [ ] Data persistence and database integration
- [ ] Import/export functionality
- [ ] Multi-currency support  
- [ ] Mobile companion app
- [ ] API integrations with banks and brokers
- [ ] Advanced reporting and analytics
- [ ] Budgeting and goal setting features

## ⭐ Support

If you find Fire App useful, please consider giving it a star on GitHub! It helps others discover the project.

---

Made with ❤️ by Ismael Jimenez