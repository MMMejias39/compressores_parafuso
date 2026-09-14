#!/usr/bin/env python3
"""Gera a Edição Completa da Enciclopédia de Máquinas Rotodinâmicas.

Monta `Enciclopedia_Completa.tex` a partir dos três volumes canônicos, sem
copiar conteúdo à mão. A decisão de gerar em vez de manter um quarto arquivo
editável é deliberada: o projeto já perdeu tempo com duplicatas que divergiram
(`teorias`/`theorias`, cópias datadas — ver "Aprendizados operacionais" no
CONTEXTO.md). Aqui, a fonte da verdade continua sendo o volume avulso; a edição
completa é derivada e descartável.

O que o gerador faz, por volume:
  - descarta a capa própria (`titlepage`), substituída pela página de Parte;
  - descarta sumário e listas de figuras/tabelas locais (há versões globais);
  - preserva prefácio, dedicatória, nomenclatura e todo o corpo;
  - zera o contador de seção, de modo que a numeração de capítulos, equações,
    figuras e tabelas fique IDÊNTICA à da edição avulsa (`\\numberwithin` faz o
    resto). Isso é o ponto crítico: o código dos simuladores cita "Eq. 5.5" do
    Volume II, e essa citação precisa continuar apontando para a mesma equação;
  - extrai os `\\bibitem` para uma bibliografia única, deduplicada por chave.

Uso:
    python3 scripts/gerar_edicao_completa.py
    latexmk -pdf Enciclopedia_Completa.tex     # ou pdflatex 3x
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "Enciclopedia_Completa.tex"
CAPA = RAIZ / "capa_edicao_completa.tex"

# (arquivo, rótulo da Parte, título da Parte, subtítulo)
VOLUMES = [
    (
        "Volume_0_Notacoes_e_Calculo.tex",
        "VOLUME 0",
        "Notações e Cálculo Básico",
        "Os pré-requisitos matemáticos da coleção, reunidos num percurso curto.",
    ),
    (
        "Volume_I_Fundamentos.tex",
        "VOLUME I",
        "Fundamentos de Mecânica do Contínuo,\\\\Termofluidos e Sistemas de Medição",
        "As bases teóricas das máquinas rotodinâmicas.",
    ),
    (
        "compressores.tex",
        "VOLUME II",
        "Gêmeo Digital de Sistemas\\\\de Compressão Offshore",
        "Diretrizes técnicas, modelagem e implementação.",
    ),
]

AUTOR = "Marcelo Moreira Mejias"


# --------------------------------------------------------------------------
# Extração
# --------------------------------------------------------------------------

def separa_preambulo_e_corpo(texto: str) -> tuple[str, str]:
    """Divide o .tex em preâmbulo e corpo (entre begin/end document)."""
    i = texto.index(r"\begin{document}")
    j = texto.rindex(r"\end{document}")
    return texto[:i], texto[i + len(r"\begin{document}"): j]


def remove_bloco(texto: str, abre: str, fecha: str) -> tuple[str, str]:
    """Remove o primeiro bloco abre..fecha; devolve (texto_sem, bloco)."""
    i = texto.find(abre)
    if i == -1:
        return texto, ""
    j = texto.index(fecha, i) + len(fecha)
    return texto[:i] + texto[j:], texto[i:j]


def limpa_corpo(corpo: str, rotulo: str) -> tuple[str, list[tuple[str, str]]]:
    """Tira capa, sumário e bibliografia locais; devolve corpo e bibitens."""
    corpo, _ = remove_bloco(corpo, r"\begin{titlepage}", r"\end{titlepage}")

    corpo, bib = remove_bloco(
        corpo, r"\begin{thebibliography}", r"\end{thebibliography}"
    )
    itens: list[tuple[str, str]] = []
    if bib:
        # Cada \bibitem{chave} vai até o próximo \bibitem ou até o fim do bloco.
        miolo = bib[bib.index("}", bib.index(r"\begin{thebibliography}")) + 1:]
        miolo = miolo.replace(r"\end{thebibliography}", "")
        for pedaco in re.split(r"(?=\\bibitem\{)", miolo):
            m = re.match(r"\\bibitem\{([^}]*)\}", pedaco.strip())
            if m:
                itens.append((m.group(1), pedaco.strip()))

    # Sumário e listas locais: a edição completa tem os seus, globais.
    corpo = re.sub(r"^[ \t]*\\tableofcontents[ \t]*\n", "", corpo, flags=re.M)
    for lista in ("listoffigures", "listoftables"):
        corpo = re.sub(
            r"^[ \t]*\\phantomsection[ \t]*\n"
            r"[ \t]*\\addcontentsline\{toc\}\{section\}\{[^}]*\}[ \t]*\n"
            r"[ \t]*\\" + lista + r"[ \t]*\n",
            "",
            corpo,
            flags=re.M,
        )
        corpo = re.sub(r"^[ \t]*\\" + lista + r"[ \t]*\n", "", corpo, flags=re.M)

    # Entradas de sumário que se repetiriam nos três volumes ganham o rótulo do
    # volume — sem isso o sumário global teria três "Prefácio" indistinguíveis.
    for entrada in ("Prefácio", "Nomenclatura", "Glossário de Anglicismos"):
        corpo = corpo.replace(
            r"\addcontentsline{toc}{section}{" + entrada + "}",
            r"\addcontentsline{toc}{section}{" + f"{entrada} — {rotulo}" + "}",
        )

    # As Partes internas do Volume II entram no sumário como "I", "II", "III" —
    # no volume avulso isso é claro, mas na edição completa colide com as
    # Partes-volume ("VOLUME II"). Rotula explicitamente, só no arquivo gerado.
    corpo = re.sub(
        r"\\addcontentsline\{toc\}\{part\}\{([IVX]+)\\hspace\{1em\}([^}]*)\}",
        r"\\addcontentsline{toc}{part}{Parte \1 --- \2}",
        corpo,
    )

    return corpo.strip("\n"), itens


# Ordem obrigatória no topo do preâmbulo: cmap corrige o mapeamento Unicode
# das ligaduras e PRECISA vir antes de fontenc (regra permanente do projeto —
# ver "Correção de extração de texto" no CONTEXTO.md).
ORDEM_INICIAL = ["cmap", "fontenc", "inputenc", "babel", "microtype"]


def coleta_pacotes(preambulos: list[str]) -> list[str]:
    """União dos \\usepackage dos volumes, sem duplicar e na ordem correta.

    Derivar da fonte em vez de manter uma lista à mão: um volume que passe a
    usar um pacote novo não quebra mais a edição completa (foi o que aconteceu
    com tabularx e bm na primeira geração).
    """
    vistos: dict[str, str] = {}
    for pre in preambulos:
        for linha in re.findall(r"\\usepackage(?:\[[^\]]*\])?\{[^}]*\}", pre):
            nomes = re.search(r"\{([^}]*)\}", linha).group(1)
            chave = nomes.split(",")[0].strip()
            if chave not in vistos:
                vistos[chave] = linha

    ordenados = [vistos.pop(n) for n in ORDEM_INICIAL if n in vistos]
    # hyperref por último: precisa enxergar os demais pacotes já carregados
    hyper = vistos.pop("hyperref", None)
    ordenados += [vistos[k] for k in sorted(vistos)]
    if hyper:
        ordenados.append(hyper)
    return ordenados


def pagina_de_parte(rotulo: str, titulo: str, subtitulo: str) -> str:
    """Página de abertura de volume.

    Usa a montagem manual documentada no CONTEXTO.md: `\\part{}` renderiza
    desalinhado à esquerda nesta classe, e nem envolvê-lo em `center` resolve.
    """
    return rf"""
\clearpage
\thispagestyle{{empty}}
\phantomsection
\addcontentsline{{toc}}{{part}}{{{rotulo} — {titulo.replace(chr(92) * 2, ' ')}}}
\vspace*{{\fill}}
\begin{{center}}
	{{\color{{capaBlue}}\sffamily\bfseries\Large\textls[200]{{{rotulo}}}}}\\[3mm]
	{{\color{{capaOuro}}\rule{{42mm}}{{2.2pt}}}}\\[9mm]
	{{\huge\bfseries {titulo}}}\\[7mm]
	\begin{{minipage}}{{0.68\textwidth}}
		\centering\itshape\small {subtitulo}
	\end{{minipage}}
\end{{center}}
\vspace*{{\fill}}
\clearpage
"""


# --------------------------------------------------------------------------
# Montagem
# --------------------------------------------------------------------------

def main() -> int:
    if not CAPA.exists():
        print(f"ERRO: capa não encontrada em {CAPA}", file=sys.stderr)
        return 1

    corpos: list[str] = []
    bibitens: dict[str, str] = {}
    ordem_bib: list[str] = []
    hifenizacao: set[str] = set()
    preambulos: list[str] = []

    for arquivo, rotulo, titulo, subtitulo in VOLUMES:
        caminho = RAIZ / arquivo
        if not caminho.exists():
            print(f"ERRO: volume não encontrado: {caminho}", file=sys.stderr)
            return 1
        texto = caminho.read_text(encoding="utf-8")
        preambulo, corpo = separa_preambulo_e_corpo(texto)
        preambulos.append(preambulo)

        m = re.search(r"\\hyphenation\{(.*?)\}", preambulo, re.S)
        if m:
            hifenizacao.update(m.group(1).split())

        corpo, itens = limpa_corpo(corpo, rotulo)
        for chave, item in itens:
            if chave not in bibitens:          # 1ª ocorrência vence
                bibitens[chave] = item
                ordem_bib.append(chave)

        corpos.append(
            pagina_de_parte(rotulo, titulo, subtitulo)
            # Zera a seção: mantém a numeração idêntica à do volume avulso.
            + "\n\\setcounter{section}{0}\n"
            + corpo
        )
        print(f"  {arquivo}: {len(corpo.splitlines())} linhas, "
              f"{len(itens)} referências")

    hif = "\n  ".join(sorted(hifenizacao))
    bib = "\n\n".join(bibitens[c] for c in ordem_bib)

    cabecalho = (CABECALHO
                 .replace("@@AUTOR@@", AUTOR)
                 .replace("@@HIFENIZACAO@@", hif)
                 .replace("@@CAPA@@", CAPA.name)
                 .replace("@@PACOTES@@", "\n".join(coleta_pacotes(preambulos))))
    rodape = RODAPE.replace("@@BIBLIOGRAFIA@@", bib)
    saida = cabecalho + "\n\n".join(corpos) + rodape

    SAIDA.write_text(saida, encoding="utf-8")
    print(f"\nGerado: {SAIDA.name} "
          f"({len(saida.splitlines())} linhas, {len(bibitens)} referências únicas)")
    print("Compile com: latexmk -pdf Enciclopedia_Completa.tex")
    return 0


CABECALHO = r"""% =============================================================================
% ENCICLOPÉDIA DE MÁQUINAS ROTODINÂMICAS — EDIÇÃO COMPLETA (volume único)
% -----------------------------------------------------------------------------
% ARQUIVO GERADO — não edite à mão.
% Fonte: Volume_0_Notacoes_e_Calculo.tex, Volume_I_Fundamentos.tex e
%        compressores.tex (os três continuam sendo os documentos canônicos).
% Gerador: scripts/gerar_edicao_completa.py
% Capa:    capa_edicao_completa.tex (essa sim, editável à mão)
%
% A numeração de capítulos, equações, figuras e tabelas de cada volume é
% preservada exatamente como na edição avulsa — o contador de seção é zerado na
% abertura de cada volume.
% =============================================================================
\documentclass[12pt,a4paper]{article}

@@PACOTES@@
\usepackage{xcolor}   % cores da capa (tikz já carrega, explícito por clareza)
\usetikzlibrary{patterns}
\pgfplotsset{compat=1.18}

\numberwithin{equation}{section}
\numberwithin{table}{section}
\numberwithin{figure}{section}

\geometry{margin=2.5cm, headheight=15pt}
\addtolength{\topmargin}{-0.5pt}
\emergencystretch=1em

\hyphenation{
  @@HIFENIZACAO@@
}

\hypersetup{
	colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black,
	pdftitle={Enciclopédia de Máquinas Rotodinâmicas — Edição Completa},
	pdfauthor={@@AUTOR@@},
	pdfsubject={Volumes 0, I e II reunidos em volume único},
	pdfkeywords={máquinas rotodinâmicas, compressor de parafuso, offshore,
	             gêmeo digital, mecânica do contínuo, termofluidos, cálculo}
}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\sectionmark}[1]{\markboth{#1}{}}
\fancyhead[L]{\nouppercase{\leftmark}}
\fancyhead[R]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\newcommand{\chapterword}{Capítulo}
\titleformat{\section}
	{\normalfont\Large\bfseries\raggedright}
	{\chapterword~\thesection}{1em}{}
	[\vspace{-0.5em}\rule{\textwidth}{0.4pt}]

\newcommand{\colecaotitulo}{Enciclopédia de Máquinas Rotodinâmicas}
\newcommand{\autorlivro}{@@AUTOR@@}
\newcommand{\revdatacompleta}{\today}

\begin{document}

\input{@@CAPA@@}

% --- SUMÁRIO GERAL ---
\clearpage
\pagenumbering{roman}
\tableofcontents

\clearpage
\phantomsection
\addcontentsline{toc}{section}{Lista de Figuras}
\listoffigures

\clearpage
\phantomsection
\addcontentsline{toc}{section}{Lista de Tabelas}
\listoftables

\clearpage
\pagenumbering{arabic}

"""

RODAPE = r"""

% =============================================================================
% BIBLIOGRAFIA UNIFICADA — referências dos três volumes, deduplicadas por chave
% =============================================================================
\clearpage
\phantomsection
\addcontentsline{toc}{section}{Referências}
\begin{thebibliography}{99}

@@BIBLIOGRAFIA@@

\end{thebibliography}

\end{document}
"""


if __name__ == "__main__":
    raise SystemExit(main())
