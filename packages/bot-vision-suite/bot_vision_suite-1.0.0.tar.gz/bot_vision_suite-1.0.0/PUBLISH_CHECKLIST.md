# 📋 Checklist para Publicação no PyPI

## ✅ Preparação (Concluído)
- [x] Build gerado com sucesso
- [x] Biblioteca testada localmente
- [x] Funcionalidade "move_to" adicionada
- [x] Documentação atualizada
- [x] README.md completo
- [x] Licença MIT incluída
- [x] pyproject.toml configurado

## 🔑 Antes de Publicar
- [ ] Criar conta no https://test.pypi.org/
- [ ] Criar conta no https://pypi.org/
- [ ] Gerar API Token (recomendado) em vez de usar senha

## 🧪 Teste no TestPyPI
```cmd
cd /d d:\suite2\Automation-Suite\bot_vision_suite
twine upload --repository testpypi dist/*
```

- [ ] Upload para TestPyPI bem-sucedido
- [ ] Testar instalação: `pip install -i https://test.pypi.org/simple/ bot-vision-suite`
- [ ] Testar importação: `import bot_vision`
- [ ] Verificar se todas as funções estão disponíveis

## 🚀 Publicação Oficial
```cmd
cd /d d:\suite2\Automation-Suite\bot_vision_suite
twine upload dist/*
```

- [ ] Upload para PyPI oficial bem-sucedido
- [ ] Testar instalação: `pip install bot-vision-suite`
- [ ] Verificar página do projeto: https://pypi.org/project/bot-vision-suite/

## 📈 Pós-Publicação
- [ ] Atualizar README com instruções de instalação via pip
- [ ] Criar tags no Git com a versão
- [ ] Documentar próximas versões

## 🔧 Para Futuras Atualizações
1. Atualizar versão no `pyproject.toml`
2. Rebuild: `python -m build`
3. Upload: `twine upload dist/*`

## 🆘 Comandos de Emergência
- Remover arquivos dist antigos: `rmdir /s dist`
- Rebuild completo: `python -m build --clean`
- Verificar conteúdo do pacote: `twine check dist/*`

## 📞 Links Úteis
- PyPI Test: https://test.pypi.org/
- PyPI Oficial: https://pypi.org/
- Documentação Twine: https://twine.readthedocs.io/
- Guia PyPI: https://packaging.python.org/
