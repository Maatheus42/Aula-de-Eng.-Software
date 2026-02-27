"""Aplicativo de comparação de títulos.

- Normaliza textos (remove acentos, pontuação e diferença de caixa)
- Compara títulos em níveis diferentes de detalhamento
- Pode ser usado de forma interativa ou via linha de comando
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, List


# ----------------------------
# Utilidades de apresentação
# ----------------------------
def obter_largura_terminal() -> int:
    """Obtém largura do terminal com fallback seguro."""
    try:
        return max(80, os.get_terminal_size().columns)
    except OSError:
        return 80


def centralizar_texto(texto: str, largura: int | None = None) -> str:
    if largura is None:
        largura = obter_largura_terminal()
    return texto.center(largura)


def linha_separadora(caractere: str = "=", largura: int | None = None) -> str:
    if largura is None:
        largura = obter_largura_terminal()
    return caractere * largura


# ----------------------------
# Normalização
# ----------------------------
def remover_acentos(texto: str) -> str:
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8")


def normalizar_texto_para_comparacao(texto: str) -> str:
    """Normaliza para comparação compacta (sem espaços e símbolos)."""
    texto = remover_acentos(texto.lower())
    return re.sub(r"[^a-z0-9]", "", texto)


def normalizar_texto_para_exibicao(texto: str) -> str:
    """Normaliza para leitura (mantém separação entre palavras)."""
    texto = remover_acentos(texto.lower())
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# ----------------------------
# Modelo de resultado
# ----------------------------
@dataclass
class Diferenca:
    tipo: str
    sistema: List[str]
    pdf: List[str]
    pos_sistema: tuple[int, int]
    pos_pdf: tuple[int, int]


@dataclass
class ResultadoComparacao:
    sao_iguais: bool
    sistema_compactado: str
    pdf_compactado: str
    primeira_diferenca_indice: int | None
    diferencas: List[Diferenca]


# ----------------------------
# Núcleo de comparação
# ----------------------------
def _indice_primeira_diferenca(a: str, b: str) -> int | None:
    limite = min(len(a), len(b))
    for i in range(limite):
        if a[i] != b[i]:
            return i
    if len(a) != len(b):
        return limite
    return None


def _diferencas_por_palavra(texto_sistema: str, texto_pdf: str) -> List[Diferenca]:
    palavras_sistema = normalizar_texto_para_exibicao(texto_sistema).split()
    palavras_pdf = normalizar_texto_para_exibicao(texto_pdf).split()

    matcher = difflib.SequenceMatcher(None, palavras_sistema, palavras_pdf)
    diferencas: List[Diferenca] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        diferencas.append(
            Diferenca(
                tipo=tag,
                sistema=palavras_sistema[i1:i2],
                pdf=palavras_pdf[j1:j2],
                pos_sistema=(i1 + 1, i2),
                pos_pdf=(j1 + 1, j2),
            )
        )
    return diferencas


def comparar_titulos(titulo_sistema: str, titulo_pdf: str) -> ResultadoComparacao:
    sistema_compactado = normalizar_texto_para_comparacao(titulo_sistema)
    pdf_compactado = normalizar_texto_para_comparacao(titulo_pdf)
    iguais = sistema_compactado == pdf_compactado

    return ResultadoComparacao(
        sao_iguais=iguais,
        sistema_compactado=sistema_compactado,
        pdf_compactado=pdf_compactado,
        primeira_diferenca_indice=_indice_primeira_diferenca(sistema_compactado, pdf_compactado),
        diferencas=[] if iguais else _diferencas_por_palavra(titulo_sistema, titulo_pdf),
    )


# ----------------------------
# Renderização de saída
# ----------------------------
def _formatar_diferenca(dif: Diferenca) -> str:
    if dif.tipo == "replace":
        return (
            "🚨 Substituição\n"
            f"  Sistema (posições {dif.pos_sistema[0]}-{dif.pos_sistema[1]}): {dif.sistema}\n"
            f"  PDF     (posições {dif.pos_pdf[0]}-{dif.pos_pdf[1]}): {dif.pdf}"
        )
    if dif.tipo == "delete":
        return (
            "🚨 Removido no PDF\n"
            f"  Sistema (posições {dif.pos_sistema[0]}-{dif.pos_sistema[1]}): {dif.sistema}"
        )
    if dif.tipo == "insert":
        return (
            "🚨 Adicionado no PDF\n"
            f"  PDF (posições {dif.pos_pdf[0]}-{dif.pos_pdf[1]}): {dif.pdf}"
        )
    return f"ℹ️ Diferença ({dif.tipo}) - sistema={dif.sistema}, pdf={dif.pdf}"


def gerar_relatorio(resultado: ResultadoComparacao, nivel: str) -> str:
    largura = obter_largura_terminal()
    linhas: List[str] = []

    linhas.append(linha_separadora("=", largura))
    linhas.append(centralizar_texto("RESULTADO DA COMPARAÇÃO", largura))
    linhas.append(linha_separadora("=", largura))

    if nivel in {"completo", "primeira_diferenca"}:
        linhas.append(f"Sistema (compactado): {resultado.sistema_compactado}")
        linhas.append(f"PDF     (compactado): {resultado.pdf_compactado}")
        linhas.append(linha_separadora("-", largura))

    if resultado.sao_iguais:
        linhas.append("✅ STATUS: TÍTULOS IGUAIS")
        return "\n".join(linhas)

    linhas.append("❌ STATUS: TÍTULOS DIFERENTES")

    if nivel == "simples":
        return "\n".join(linhas)

    if nivel == "primeira_diferenca":
        idx = resultado.primeira_diferenca_indice
        if idx is None:
            linhas.append("Nenhuma diferença detectada.")
        else:
            linhas.append(f"Primeira diferença no índice compactado: {idx}")
        return "\n".join(linhas)

    if nivel == "completo":
        if not resultado.diferencas:
            linhas.append("Diferenças não puderam ser alinhadas por palavra.")
        else:
            for i, dif in enumerate(resultado.diferencas, start=1):
                linhas.append(f"\n[{i}] {_formatar_diferenca(dif)}")

    return "\n".join(linhas)


# ----------------------------
# CLI
# ----------------------------
def _input_nao_vazio(prompt: str) -> str:
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        print("Entrada vazia. Tente novamente.")


def executar_modo_interativo(nivel: str) -> int:
    largura = obter_largura_terminal()
    print(linha_separadora("=", largura))
    print(centralizar_texto("COMPARADOR DE TÍTULOS", largura))
    print(linha_separadora("=", largura))

    titulo_sistema = _input_nao_vazio("Título do Sistema: ")
    titulo_pdf = _input_nao_vazio("Título do PDF: ")

    resultado = comparar_titulos(titulo_sistema, titulo_pdf)
    print(gerar_relatorio(resultado, nivel))
    return 0 if resultado.sao_iguais else 1


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compara títulos com normalização inteligente.")
    parser.add_argument("--sistema", help="Título vindo do sistema.")
    parser.add_argument("--pdf", help="Título vindo do PDF.")
    parser.add_argument(
        "--nivel",
        choices=["simples", "primeira_diferenca", "completo"],
        default="completo",
        help="Nível de detalhamento da saída.",
    )
    parser.add_argument(
        "--interativo",
        action="store_true",
        help="Força execução interativa, mesmo com argumentos disponíveis.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.interativo or not (args.sistema and args.pdf):
        return executar_modo_interativo(args.nivel)

    resultado = comparar_titulos(args.sistema, args.pdf)
    print(gerar_relatorio(resultado, args.nivel))
    return 0 if resultado.sao_iguais else 1


if __name__ == "__main__":
    raise SystemExit(main())
