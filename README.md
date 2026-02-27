# Aula-de-Eng.-Software

Este repositório agora contém um **comparador de títulos** em Python para validar textos de plataformas diferentes (ex.: sistema interno x PDF), ignorando acentos, pontuação e diferenças de caixa.

## Arquivo principal

- `comparador_titulos.py`

## Como usar

### 1) Modo interativo

```bash
python3 comparador_titulos.py --interativo
```

Você informa os dois títulos e recebe o relatório.

### 2) Modo por argumentos (mais prático para automação)

```bash
python3 comparador_titulos.py \
  --sistema "Título vindo do sistema" \
  --pdf "Título vindo do PDF" \
  --nivel completo
```

Níveis disponíveis (`--nivel`):

- `simples`: apenas status final (igual/diferente)
- `primeira_diferenca`: mostra índice da primeira divergência
- `completo`: mostra divergências por palavra alinhadas com `difflib`

## Executar testes

```bash
python3 -m unittest discover -s tests -v
```

## Saída e código de retorno

- Retorna `0` quando os títulos são iguais após normalização.
- Retorna `1` quando os títulos são diferentes.

Isso facilita integração com pipelines de CI/CD.
