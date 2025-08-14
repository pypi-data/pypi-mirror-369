# MT5 Trading Library

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![CI](https://github.com/paxelcool/MT5_trading_lib_project/actions/workflows/ci.yml/badge.svg)](https://github.com/paxelcool/MT5_trading_lib_project/actions/workflows/ci.yml)

Современная Python-библиотека для взаимодействия с MetaTrader5, предоставляющая высокоуровневый API с расширенными возможностями.

## 🚀 Особенности

- **Надежное соединение** с автоматическим переподключением и circuit breaker
- **Асинхронная поддержка** для высокопроизводительных сценариев
- **Умное кэширование** с TTL и стратегиями инвалидации
- **Безопасность** с шифрованием учетных данных
- **Мониторинг** и метрики производительности
- **Расширяемость** через middleware и event-driven архитектуру
- **Production-ready** с comprehensive тестированием

## 📦 Установка

```bash
pip install mt5-trading-lib
```

## 🔧 Быстрый старт

Асинхронный высокоуровневый клиент:

```python
import asyncio
from mt5_trading_lib import AsyncMt5Client, Config
from mt5_trading_lib.logging_config import setup_logging
import MetaTrader5 as mt5

async def main():
    setup_logging()
    cfg = Config.load_config()
    client = AsyncMt5Client(cfg)

    if await client.connect():
        account = await client.get_account_info()
        print(f"Balance: {account['balance']}")

        quotes = await client.get_real_time_quotes("EURUSD")
        print(f"EURUSD: {quotes['bid']}/{quotes['ask']}")

        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

Синхронные компоненты (низкоуровневое использование):

```python
from mt5_trading_lib import (
    Config, Mt5Connector, CacheManager, RetryManager, DataFetcher
)
from mt5_trading_lib.logging_config import setup_logging
import MetaTrader5 as mt5

setup_logging()
cfg = Config.load_config()

connector = Mt5Connector(cfg)
connector.connect()

cache = CacheManager(cfg)
retry = RetryManager(cfg)
data = DataFetcher(cfg, connector, cache, retry)

account = data.get_account_info()
print(account)

quotes = data.get_real_time_quotes("EURUSD")
print(quotes)

connector.disconnect()
```

## 📚 Документация

- API Reference: `docs/api_reference.rst`
- Архитектура: `doc/project_design_concept.md`
- План проекта: `doc/project_plan.md`

## 🛠️ Разработка

Этот проект находится в активной разработке. См. [план проекта](project_plan.md) для деталей.

### Требования для разработки

- Python 3.8+
- MetaTrader5 Terminal
- Windows 10/11

### Установка для разработки

```bash
git clone https://github.com/paxelcool/MT5_trading_lib_project.git
cd MT5_trading_lib_project
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev]"
```

## 🤝 Участие в проекте

Приветствуются contributions! См. [CONTRIBUTING.md](CONTRIBUTING.md) для деталей.

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. [LICENSE](LICENSE) файл для деталей.

## ⚠️ Предупреждение

Эта библиотека предназначена для образовательных и исследовательских целей. Торговля на финансовых рынках связана с высокими рисками. Всегда тестируйте стратегии на демо-счетах перед использованием реальных средств.

## 📞 Поддержка

- 📧 Email: mtrfrgm@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/mt5-trading-lib/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/mt5-trading-lib/discussions)
