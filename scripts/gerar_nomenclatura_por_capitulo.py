#!/usr/bin/env python3
"""Distribui o Índice de Símbolos pelos capítulos que cada símbolo usa.

Motivação (pedido do autor, 13/09/2026): uma nomenclatura única no início
obriga o leitor a paginar até lá toda vez que um símbolo o detém. Cada capítulo
passa a abrir com a tabela dos símbolos que ele de fato usa.

Fonte única da verdade: o `\\section*{Índice de Símbolos}` no back matter do
próprio volume — o mesmo princípio já adotado para a Edição Completa (gerar, em
vez de duplicar; ver "Aprendizados operacionais" no CONTEXTO.md). As tabelas por
capítulo ficam entre marcadores e são reescritas a cada execução, de modo que
editar o Índice de Símbolos e rodar este script mantém os dois em sincronia.

Regras de distribuição:
  - entrada cuja coluna "Capítulos" cita números vai para cada capítulo citado;
  - entrada "Todos" ou temática (ex.: "Termofluídica") NÃO é repetida capítulo a
    capítulo: vai para a tabela única de símbolos de uso geral, inserida uma vez
    na abertura do corpo. Repetir P, T e m-ponto em 29 capítulos seria ruído,
    não serviço ao leitor;
  - capítulo sem nenhum símbolo próprio não recebe tabela.

Uso:
    python3 scripts/gerar_nomenclatura_por_capitulo.py [--check]

`--check` não escreve nada: só relata o que mudaria (útil em verificação).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VOLUMES = ["Volume_I_Fundamentos.tex", "compressores.tex"]

INI = "% >>> NOMENCLATURA-CAP {n} — GERADO por scripts/gerar_nomenclatura_por_capitulo.py"
FIM = "% <<< NOMENCLATURA-CAP {n}"
INI_GERAL = "% >>> SIMBOLOS-GERAIS — GERADO por scripts/gerar_nomenclatura_por_capitulo.py"
FIM_GERAL = "% <<< SIMBOLOS-GERAIS"


def bloco_indice(texto: str) -> tuple[int, int]:
    """Posição (início, fim) do Índice de Símbolos no volume."""
    i = texto.index(r"\section*{Índice de Símbolos}")
    j = texto.index(r"% --- LISTAS DE FIGURAS E TABELAS", i)
    return i, j


def entradas(texto: str) -> list[tuple[str, str, str, str]]:
    """Extrai (símbolo, significado, unidade, capítulos) do Índice de Símbolos."""
    i, j = bloco_indice(texto)
    out = []
    for linha in texto[i:j].split("\n"):
        linha = linha.strip()
        if linha.count("&") != 3 or r"\\" not in linha or "textbf" in linha:
            continue
        linha = re.sub(r"\\\\.*$", "", linha).strip()
        sim, sig, uni, cap = (c.strip() for c in linha.split("&"))
        if sim and sig:
            out.append((sim, sig, uni, cap))
    return out


def capitulos_de(campo: str) -> list[int]:
    """Números de capítulo citados no campo 'Capítulos'; [] se for geral."""
    if campo.lower().startswith("todos"):
        return []
    return [int(n) for n in re.findall(r"\d+", campo)]


def tabela(linhas: list[tuple[str, str, str]], titulo: str) -> str:
    """Monta a tabela LaTeX de símbolos (booktabs, como o resto da coleção)."""
    # O símbolo vai EXATAMENTE como está na fonte: reempacotar em $...$ quebra
    # entradas que já trazem marcação fora do modo matemático (ex.: "$G$\dag").
    corpo = "\n".join(f"\t{s} & {sig} & {uni} \\\\" for s, sig, uni in linhas)
    return (
        f"\\paragraph{{{titulo}}}\\mbox{{}}\\\\[-0.5em]\n"
        "{\\small\n"
        "\\begin{longtable}{>{\\raggedright\\arraybackslash}p{2.6cm} "
        ">{\\raggedright\\arraybackslash}p{9.2cm} "
        ">{\\raggedright\\arraybackslash}p{2.6cm}}\n"
        "\t\\toprule\n"
        "\t\\textbf{Símbolo} & \\textbf{Significado} & \\textbf{Unidade} \\\\ \\midrule\n"
        "\t\\endhead\n"
        f"{corpo}\n"
        "\t\\bottomrule\n"
        "\\end{longtable}\n"
        "}\n"
    )


def limpa_gerados(texto: str) -> str:
    """Remove blocos gerados por execuções anteriores (idempotência)."""
    texto = re.sub(
        re.escape(INI.split("{n}")[0]) + r".*?"
        + re.escape(FIM.split("{n}")[0]) + r"\d+\n",
        "", texto, flags=re.S,
    )
    return re.sub(
        re.escape(INI_GERAL) + r".*?" + re.escape(FIM_GERAL) + r"\n", "", texto, flags=re.S
    )


def processa(arquivo: Path, check: bool) -> None:
    texto = arquivo.read_text(encoding="utf-8")
    texto = limpa_gerados(texto)
    itens = entradas(texto)

    por_cap: dict[int, list[tuple[str, str, str]]] = {}
    gerais: list[tuple[str, str, str]] = []
    for sim, sig, uni, cap in itens:
        caps = capitulos_de(cap)
        if not caps:
            gerais.append((sim, sig, uni))
        for n in caps:
            por_cap.setdefault(n, []).append((sim, sig, uni))

    # tabela de símbolos gerais, uma vez, na abertura do corpo
    if gerais:
        alvo = re.search(r"^\\clearpage\n\\section\{", texto, flags=re.M)
        bloco = (
            f"{INI_GERAL}\n"
            + tabela(gerais, "Símbolos de uso geral, válidos em todo o volume")
            + f"{FIM_GERAL}\n"
        )
        texto = texto[: alvo.start()] + bloco + texto[alvo.start():]

    # tabela por capítulo, logo após o \section{...} de cada um
    inseridas = 0
    for m in list(re.finditer(r"\\section\{([^}]*)\}(\s*\\label\{[^}]*\})?", texto))[::-1]:
        n = texto[: m.start()].count("\\section{") + 1
        linhas = por_cap.get(n)
        if not linhas:
            continue
        fim = m.end()
        mk = re.match(r"\s*\\markboth\{[^}]*\}\{\}", texto[fim:])
        if mk:
            fim += mk.end()
        bloco = (
            "\n\n" + INI.format(n=n) + "\n"
            + tabela(linhas, "Símbolos deste capítulo")
            + FIM.format(n=n) + "\n"
        )
        texto = texto[:fim] + bloco + texto[fim:]
        inseridas += 1

    print(f"  {arquivo.name}: {len(itens)} entradas | {len(gerais)} gerais | "
          f"{inseridas} capítulos com tabela própria")
    if not check:
        arquivo.write_text(texto, encoding="utf-8")


def main() -> int:
    check = "--check" in sys.argv
    for nome in VOLUMES:
        processa(RAIZ / nome, check)
    if check:
        print("\n--check: nada foi escrito.")
    else:
        print("\nRecompile os volumes (pdflatex 3x) e a Edição Completa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
