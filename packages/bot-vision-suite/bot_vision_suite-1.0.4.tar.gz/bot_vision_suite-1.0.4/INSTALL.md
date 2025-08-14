# Instalação do Bot Vision Suite

## Instalação Básica

Para instalar apenas as dependências core necessárias:

```bash
pip install bot-vision-suite
```

## Instalação com Dependências Opcionais

### Para desenvolvimento:
```bash
pip install bot-vision-suite[dev]
```

### Para automação avançada (inclui keyboard e mouse utilities):
```bash
pip install bot-vision-suite[automation]
```

### Para integração com IA:
```bash
pip install bot-vision-suite[ai]
```

### Para automação web:
```bash
pip install bot-vision-suite[web]
```

### Instalação completa:
```bash
pip install bot-vision-suite[dev,automation,ai,web]
```

## Instalação a partir do código fonte

```bash
git clone <repository-url>
cd bot-vision-suite
pip install -e .
```

## Dependências Principais

O package utiliza as seguintes versões EXATAS das bibliotecas principais:

- **PyAutoGUI==0.9.54** - Automação de mouse e teclado
- **numpy==1.26.4** - Computação numérica
- **opencv-python==4.9.0.80** - Processamento de imagem
- **pytesseract** - OCR (Reconhecimento Óptico de Caracteres)
- **pyperclip>=1.8.2** - Manipulação da área de transferência
- **Pillow>=10.0.0** - Processamento de imagem

## Configuração do Tesseract

Certifique-se de ter o Tesseract OCR instalado:

### Windows:
1. Baixe e instale o Tesseract de: https://github.com/UB-Mannheim/tesseract/wiki
2. Adicione o caminho do executável ao PATH ou configure no código

### Linux:
```bash
sudo apt-get install tesseract-ocr
```

### macOS:
```bash
brew install tesseract
```

## Verificação da Instalação

```python
from bot_vision import BotVision

# Teste básico
bot = BotVision()
print("Bot Vision Suite instalado com sucesso!")

# Teste OCR
from bot_vision import find_text
print("Funcionalidades OCR disponíveis")

# Teste de automação
from bot_vision import click_text
print("Funcionalidades de automação disponíveis")
```
