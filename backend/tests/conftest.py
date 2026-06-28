# conftest.py — configuração global dos testes
import os
import sys
from pathlib import Path

# Adiciona o backend ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Variáveis de ambiente necessárias para os testes
os.environ.setdefault("SECRET_KEY", "chave-secreta-para-testes-nao-usar-em-producao")
os.environ.setdefault("ALGORITHM", "HS256")