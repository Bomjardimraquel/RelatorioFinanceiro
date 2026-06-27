# conftest.py — configuração global dos testes
import sys
from pathlib import Path

# Adiciona o backend ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent))