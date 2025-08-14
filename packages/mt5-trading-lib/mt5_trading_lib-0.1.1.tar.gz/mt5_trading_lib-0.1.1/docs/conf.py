import os
import sys

# -- Path setup --------------------------------------------------------------

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "mt5_trading_lib"
author = "Павел Садовенко"
release = "0.1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = []

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Избегаем ошибок импорта тяжёлых внешних зависимостей при сборке доков
autodoc_mock_imports = [
    "MetaTrader5",
    "redis",
    "pybreaker",
    "prometheus_client",
    "structlog",
    "asyncio_mqtt",
    "aioredis",
]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
