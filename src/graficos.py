"""Chart helpers for the exploratory analysis (Etapa 3), built on matplotlib.

Visual identity shared with the portfolio:
    background #f8f7fa, text #26252b
    main #58628a (dark #414a6c), sage #6f8a6b, ochre #c08a3e (highlight only)
    IBM Plex Serif for titles, IBM Plex Sans for text, IBM Plex Mono for numbers

The functions never write titles, captions or interpretation on their own:
every text shown on a figure comes from a parameter.

Usage:
    from src import graficos as gr
    gr.aplicar_tema()
    fig, ax = gr.serie_temporal(df, "ano", "media_nota_mt", "rede",
                                titulo="...", marcar_quebra=True)
    gr.salvar(fig, "nome_do_grafico")

The chart palette is an extension of the brand palette, adjusted for
contrast and color vision deficiency: same hues where possible, with
chroma and lightness changed so the colors stay distinguishable on a
chart. The exact brand colors remain available in CORES for non-data
elements.

Color choices (checked with an OKLab/CVD validator against the #f8f7fa
background, simulating protanopia and deuteranopia, all pairs compared):
    - CORES_REDE: the brand hues of "principal" and "salvia" with chroma
      raised to 0.105 (the exact brand colors read as gray in a chart and
      sit too close to each other), plus a wine third hue far from the
      ochre. Worst pair: CVD dE 10.4, normal-vision dE 15.5, all >= 3:1.
    - cores_sequenciais(n): one indigo hue (brand hue 273 deg), OKLCH
      lightness 0.74 -> 0.29. Monotone, light end >= 2:1 on the background,
      adjacent lightness steps >= 0.06 for n <= 8.
    - CORES["nao_sei"]: neutral gray (#86858d, 3.4:1) for categories
      outside the ordered levels (FORA_DA_SEQUENCIA, e.g. "nao_sei").
      They never take a ramp step, always come after the ordered levels,
      sit apart from them in bar charts (extra gap) and use a dashed line
      in densities and time series, so they are not read as one more level.
"""

from __future__ import annotations

import math
import re
import warnings
from collections.abc import Mapping, Sequence
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.ticker import Formatter, FuncFormatter, MaxNLocator

ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "reports" / "figures"

# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------

CORES = {
    "fundo": "#f8f7fa",
    "texto": "#26252b",
    "texto_secundario": "#5f5e68",  # 6.1:1 on fundo
    "grade": "#e4e2e8",
    "eixo": "#b9b7c0",
    "principal": "#58628a",
    "principal_escuro": "#414a6c",
    "salvia": "#6f8a6b",
    "ocre": "#c08a3e",
    "neutro": "#a3a1ab",  # non-highlighted series when a highlight is used
    "nao_sei": "#86858d",  # categories outside the ordered levels, 3.4:1
}

# Categories that are not a level of an ordered scale (e.g. "don't know"
# in schooling). They get CORES["nao_sei"] and are kept apart from the levels.
FORA_DA_SEQUENCIA = ("nao_sei",)

# Extra space (in bar slots) between ordered levels and FORA_DA_SEQUENCIA.
_ESPACO_FORA = 0.5

DESTAQUE = CORES["ocre"]

# Fixed order: federal, estadual_municipal, privada. Color follows the
# entity, so a chart with only two networks keeps these same colors.
CORES_REDE = {
    "federal": "#505e9f",
    "estadual_municipal": "#5b9054",
    "privada": "#984260",
}

# Generic categorical order for groups that are not networks.
CATEGORICA = list(CORES_REDE.values())

FONTE_TITULO = "IBM Plex Serif"
FONTE_TEXTO = "IBM Plex Sans"
FONTE_NUMERO = "IBM Plex Mono"

# Sequential ramp parameters (OKLCH).
_SEQ_L = (0.74, 0.29)
_SEQ_HUE = 273.0
_SEQ_MAX_PASSOS = 8

# Break in the questionnaire/series between these two years (see D002, D006).
QUEBRA_PADRAO = (2023, 2024)

_PLEX_FILE = re.compile(r"^IBMPlex(Sans|Serif|Mono)-[A-Za-z]+\.(ttf|otf)$")


# ---------------------------------------------------------------------------
# Number formatting (pt-BR: 1.234,5)
# ---------------------------------------------------------------------------


def formatar_numero(valor: float, casas: int = 0) -> str:
    """Format a number with pt-BR separators (thousands '.', decimal ',')."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return ""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


class _FormatadorPtBr(Formatter):
    """Tick formatter with pt-BR separators.

    With casas=None the number of decimals follows the tick spacing, so
    ticks 0.002, 0.004 or 0.475, 0.500 are never rounded into duplicates.
    """

    def __init__(self, casas: int | None = None):
        self.casas = casas

    def _casas_auto(self) -> int:
        locs = np.asarray(self.locs, dtype=float)
        if locs.size < 2:
            return 0
        passo = np.min(np.abs(np.diff(locs)))
        if passo <= 0:
            return 0
        casas = max(0, -math.floor(math.log10(passo) + 1e-9))
        # Extra decimal for steps like 0.25 or 0.025.
        if not math.isclose(round(passo, casas), passo, rel_tol=1e-6):
            casas += 1
        return casas

    def __call__(self, x, pos=None):
        casas = self.casas if self.casas is not None else self._casas_auto()
        return formatar_numero(x, casas)


def _formatador_eixo(casas: int | None = None) -> Formatter:
    return _FormatadorPtBr(casas)


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------


def _oklch_para_hex(L: float, C: float, h: float) -> str:
    a = C * math.cos(math.radians(h))
    b = C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_**3, m_**3, s_**3
    rgb = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076152176 * s,
    )

    def _to_srgb(c: float) -> int:
        c = min(1.0, max(0.0, c))
        c = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
        return round(c * 255)

    return "#" + "".join(f"{_to_srgb(c):02x}" for c in rgb)


def cores_sequenciais(n: int) -> list[str]:
    """Return n colors of the sequential ramp, light (first) to dark (last).

    Use for ordered bands (income, schooling). Above 8 steps adjacent colors
    get too close to tell apart; a warning is issued.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if n > _SEQ_MAX_PASSOS:
        warnings.warn(
            f"{n} sequential steps: adjacent colors fall below the minimum "
            f"lightness gap (validated up to {_SEQ_MAX_PASSOS}). Consider "
            "grouping the bands.",
            stacklevel=2,
        )
    if n == 1:
        return [CORES["principal"]]
    l0, l1 = _SEQ_L
    cores = []
    for i in range(n):
        t = i / (n - 1)
        L = l0 - (l0 - l1) * t
        C = 0.06 + 0.03 * math.sin(math.pi * t)
        cores.append(_oklch_para_hex(L, C, _SEQ_HUE))
    return cores


def _cores_grupos(
    grupos: Sequence,
    cores: Mapping | Sequence | None,
    sequencial: bool,
    destaque=None,
) -> dict:
    """Resolve one color per group, keeping color tied to the entity."""
    grupos = list(grupos)
    if destaque is not None:
        return {g: (DESTAQUE if g == destaque else CORES["neutro"]) for g in grupos}
    if isinstance(cores, Mapping):
        faltando = [g for g in grupos if g not in cores]
        if faltando:
            raise ValueError(f"no color given for groups: {faltando}")
        return {g: cores[g] for g in grupos}
    if cores is not None:
        cores = list(cores)
        if len(cores) < len(grupos):
            raise ValueError("fewer colors than groups")
        return dict(zip(grupos, cores))
    fora = {g: CORES["nao_sei"] for g in grupos if _fora(g)}
    niveis = [g for g in grupos if not _fora(g)]
    if sequencial:
        return {**dict(zip(niveis, cores_sequenciais(len(niveis)))), **fora} if niveis else fora
    if all(g in CORES_REDE for g in niveis):
        return {**{g: CORES_REDE[g] for g in niveis}, **fora}
    if len(niveis) > len(CATEGORICA):
        raise ValueError(
            f"{len(niveis)} groups but only {len(CATEGORICA)} categorical colors "
            "are validated; pass `cores`, use sequencial=True for ordered bands, "
            "or reduce the number of groups."
        )
    return {**dict(zip(niveis, CATEGORICA)), **fora}


def _fora(grupo) -> bool:
    """True for categories outside the ordered levels (e.g. 'nao_sei')."""
    return grupo in FORA_DA_SEQUENCIA


def _estilo(grupo) -> str | tuple:
    """Dashed line for FORA_DA_SEQUENCIA, solid otherwise."""
    return (0, (4, 2)) if _fora(grupo) else "solid"


def _fora_para_o_fim(grupos: Sequence) -> list:
    """Keep the order of the levels and move FORA_DA_SEQUENCIA to the end."""
    grupos = list(grupos)
    return [g for g in grupos if not _fora(g)] + [g for g in grupos if _fora(g)]


def _ordem_grupos(serie: pd.Series, ordem: Sequence | None) -> list:
    """Order groups; FORA_DA_SEQUENCIA always goes last."""
    presentes = list(pd.unique(serie.dropna()))
    if ordem is None:
        if all(g in CORES_REDE for g in presentes):
            resultado = [g for g in CORES_REDE if g in presentes]
        elif isinstance(serie.dtype, pd.CategoricalDtype):
            resultado = [g for g in serie.cat.categories if g in presentes]
        else:
            resultado = sorted(presentes)
    else:
        resultado = [g for g in ordem if g in presentes]
    return _fora_para_o_fim(resultado)


def _rotulo(grupo, rotulos: Mapping | None) -> str:
    if rotulos and grupo in rotulos:
        return str(rotulos[grupo])
    return str(grupo)


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------


def _registrar_fontes(pastas: Sequence[str | Path] | None = None) -> list[str]:
    """Add IBM Plex (Serif, Sans, Mono) files to matplotlib's font manager.

    matplotlib's font cache may predate the font install, so the files are
    registered explicitly. Returns the families missing after registration.
    """
    arquivos = font_manager.findSystemFonts(fontpaths=pastas)
    if pastas is None:
        arquivos += font_manager.findSystemFonts()
    for arquivo in set(arquivos):
        if _PLEX_FILE.match(Path(arquivo).name):
            try:
                font_manager.fontManager.addfont(arquivo)
            except (OSError, RuntimeError):
                continue
    nomes = {f.name for f in font_manager.fontManager.ttflist}
    return [f for f in (FONTE_TITULO, FONTE_TEXTO, FONTE_NUMERO) if f not in nomes]


def aplicar_tema(pastas_fontes: Sequence[str | Path] | None = None) -> None:
    """Configure matplotlib with the project's visual identity."""
    faltando = _registrar_fontes(pastas_fontes)
    if faltando:
        warnings.warn(
            f"fonts not found: {faltando}; matplotlib will fall back to its "
            "default. Install IBM Plex or pass `pastas_fontes`.",
            stacklevel=2,
        )

    mpl.rcParams.update(
        {
            "figure.facecolor": CORES["fundo"],
            "figure.figsize": (8, 4.8),
            "figure.dpi": 110,
            "savefig.facecolor": CORES["fundo"],
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.25,
            "axes.facecolor": CORES["fundo"],
            "axes.edgecolor": CORES["eixo"],
            "axes.linewidth": 0.8,
            "axes.labelcolor": CORES["texto_secundario"],
            "axes.labelsize": 10,
            "axes.titlesize": 14,
            "axes.titlelocation": "left",
            "axes.titlecolor": CORES["texto"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "axes.axisbelow": True,
            "axes.prop_cycle": mpl.cycler(color=CATEGORICA),
            "grid.color": CORES["grade"],
            "grid.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.sans-serif": [FONTE_TEXTO, "DejaVu Sans"],
            "font.serif": [FONTE_TITULO, "DejaVu Serif"],
            "font.monospace": [FONTE_NUMERO, "DejaVu Sans Mono"],
            "font.size": 10,
            "text.color": CORES["texto"],
            "xtick.color": CORES["eixo"],
            "ytick.color": CORES["eixo"],
            "xtick.labelcolor": CORES["texto_secundario"],
            "ytick.labelcolor": CORES["texto_secundario"],
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "xtick.major.size": 3,
            "ytick.major.size": 0,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "legend.labelcolor": CORES["texto"],
            "lines.linewidth": 2,
            "lines.markersize": 6,
            "lines.solid_capstyle": "round",
            "patch.linewidth": 0,
        }
    )


# ---------------------------------------------------------------------------
# Shared layout helpers
# ---------------------------------------------------------------------------


def _novo_ax(ax, figsize):
    if ax is not None:
        return ax.figure, ax
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax


_ALTURA_LEGENDA = 20  # points reserved above the axes for the legend row
_ALTURA_SUBTITULO = 18  # points reserved for the subtitle line


def _textos(
    ax,
    titulo: str | None,
    subtitulo: str | None,
    rotulo_x: str | None,
    rotulo_y: str | None,
    nota: str | None,
) -> None:
    """Place caller-provided texts. Nothing is written when a text is None.

    Stacked above the axes, bottom to top: legend row (if any), subtitle,
    title. Call after _legenda.
    """
    base = 4 + (_ALTURA_LEGENDA if ax.get_legend() is not None else 0)
    if subtitulo:
        ax.annotate(
            subtitulo,
            xy=(0, 1),
            xycoords="axes fraction",
            xytext=(0, base),
            textcoords="offset points",
            ha="left",
            va="bottom",
            fontsize=10,
            color=CORES["texto_secundario"],
            annotation_clip=False,
        )
        base += _ALTURA_SUBTITULO
    if titulo:
        ax.set_title(
            titulo,
            fontfamily=FONTE_TITULO,
            fontweight="semibold",
            loc="left",
            pad=base + 4,
        )
    if rotulo_x is not None:
        ax.set_xlabel(rotulo_x)
    if rotulo_y is not None:
        ax.set_ylabel(rotulo_y)
    if nota:
        ax.annotate(
            nota,
            xy=(0, 0),
            xycoords="figure fraction",
            xytext=(4, -6),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=8,
            color=CORES["texto_secundario"],
            annotation_clip=False,
        )


def _numeros_mono(ax, eixos: str = "xy") -> None:
    """Render numeric tick labels in IBM Plex Mono."""
    for eixo in eixos:
        ax.tick_params(axis=eixo, labelfontfamily=FONTE_NUMERO)


def _legenda(ax, n_series: int) -> None:
    """One-row legend just above the axes, left aligned (>= 2 series)."""
    if n_series >= 2:
        ax.legend(
            loc="lower left",
            bbox_to_anchor=(0, 1),
            ncol=n_series,
            handlelength=1.6,
            columnspacing=1.4,
            borderaxespad=0.3,
            borderpad=0,
        )


# ---------------------------------------------------------------------------
# Distributions
# ---------------------------------------------------------------------------


def _kde_binned(valores: np.ndarray, grade: np.ndarray, suavizacao: float) -> np.ndarray:
    """Gaussian KDE via binning + convolution (fast for millions of rows)."""
    n = valores.size
    desvio = valores.std(ddof=1)
    iqr = np.subtract(*np.percentile(valores, [75, 25]))
    escala = min(desvio, iqr / 1.34) if iqr > 0 else desvio
    if escala <= 0 or n < 2:
        return np.zeros_like(grade)
    banda = 0.9 * escala * n ** (-0.2) * suavizacao  # Silverman's rule
    passo = grade[1] - grade[0]
    bordas = np.concatenate([grade - passo / 2, [grade[-1] + passo / 2]])
    contagem, _ = np.histogram(valores, bins=bordas)
    meia = int(np.ceil(4 * banda / passo))
    x = np.arange(-meia, meia + 1) * passo
    nucleo = np.exp(-0.5 * (x / banda) ** 2)
    nucleo /= nucleo.sum()
    dens = np.convolve(contagem, nucleo, mode="same")
    return dens / (n * passo)


def distribuicoes(
    df: pd.DataFrame,
    coluna_valor: str,
    coluna_grupo: str | None = None,
    *,
    tipo: str = "densidade",
    escala: str = "densidade",
    bins: int | Sequence[float] = 40,
    suavizacao: float = 1.0,
    intervalo: tuple[float, float] | None = None,
    ordem: Sequence | None = None,
    rotulos: Mapping | None = None,
    cores: Mapping | Sequence | None = None,
    sequencial: bool = False,
    destaque=None,
    mostrar_n: bool = False,
    preencher: bool = True,
    titulo: str | None = None,
    subtitulo: str | None = None,
    rotulo_x: str | None = None,
    rotulo_y: str | None = None,
    nota: str | None = None,
    ax=None,
    figsize: tuple[float, float] = (8, 4.8),
):
    """Overlaid densities or histograms of `coluna_valor`, one per group.

    tipo: "densidade" (Gaussian KDE, Silverman bandwidth times `suavizacao`)
        or "histograma" (step outlines, shared bins).
    escala: for histograms, "densidade" (area 1 per group) or "contagem".
        Densities are always normalized to area 1 per group.
    intervalo: (min, max) of the x range; defaults to the data range.
    mostrar_n: append the group's n to its legend label.
    Rows with missing values are dropped. Returns (fig, ax).
    """
    if tipo not in {"densidade", "histograma"}:
        raise ValueError("tipo must be 'densidade' or 'histograma'")
    if escala not in {"densidade", "contagem"}:
        raise ValueError("escala must be 'densidade' or 'contagem'")

    fig, ax = _novo_ax(ax, figsize)
    dados = df[[coluna_valor] + ([coluna_grupo] if coluna_grupo else [])].dropna()

    if coluna_grupo:
        grupos = _ordem_grupos(dados[coluna_grupo], ordem)
    else:
        grupos = [None]
    paleta = (
        _cores_grupos(grupos, cores, sequencial, destaque)
        if coluna_grupo
        else {None: CORES["principal"]}
    )

    valores_todos = dados[coluna_valor].to_numpy(dtype=float)
    lo, hi = intervalo if intervalo else (valores_todos.min(), valores_todos.max())
    if isinstance(bins, int):
        bordas = np.linspace(lo, hi, bins + 1)
    else:
        bordas = np.asarray(bins, dtype=float)
    grade = np.linspace(lo, hi, 512)

    # Highlighted group drawn last so it sits on top.
    ordem_desenho = sorted(grupos, key=lambda g: g == destaque) if destaque else grupos

    for g in ordem_desenho:
        sub = dados if g is None else dados[dados[coluna_grupo] == g]
        v = sub[coluna_valor].to_numpy(dtype=float)
        if v.size == 0:
            continue
        cor = paleta[g]
        rotulo = None
        if g is not None:
            rotulo = _rotulo(g, rotulos)
            if mostrar_n:
                rotulo += f" (n = {formatar_numero(v.size)})"
        largura = 2.6 if (destaque is not None and g == destaque) else 2

        if tipo == "densidade":
            y = _kde_binned(v, grade, suavizacao)
            if preencher:
                ax.fill_between(grade, y, color=cor, alpha=0.12, linewidth=0)
            ax.plot(grade, y, color=cor, linewidth=largura, label=rotulo, linestyle=_estilo(g))
        else:
            contagem, _ = np.histogram(v, bins=bordas, density=(escala == "densidade"))
            if preencher:
                ax.stairs(contagem, bordas, fill=True, color=cor, alpha=0.12)
            ax.stairs(contagem, bordas, color=cor, linewidth=largura, label=rotulo, linestyle=_estilo(g))

    ax.set_xlim(lo, hi)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_formatter(_formatador_eixo())
    ax.yaxis.set_major_formatter(_formatador_eixo())
    _numeros_mono(ax)
    _legenda(ax, len(grupos) if coluna_grupo else 1)
    _textos(ax, titulo, subtitulo, rotulo_x, rotulo_y, nota)
    return fig, ax


# ---------------------------------------------------------------------------
# Time series
# ---------------------------------------------------------------------------


def serie_temporal(
    df: pd.DataFrame,
    x: str,
    y: str,
    grupo: str | None = None,
    *,
    marcar_quebra: bool = False,
    quebra_entre: tuple[float, float] = QUEBRA_PADRAO,
    rotulo_quebra: str | None = None,
    conectar_quebra: bool = True,
    rotulo_direto: bool = True,
    marcadores: bool = True,
    ordem: Sequence | None = None,
    rotulos: Mapping | None = None,
    cores: Mapping | Sequence | None = None,
    sequencial: bool = False,
    destaque=None,
    casas_y: int | None = None,
    y_zero: bool = False,
    titulo: str | None = None,
    subtitulo: str | None = None,
    rotulo_x: str | None = None,
    rotulo_y: str | None = None,
    nota: str | None = None,
    ax=None,
    figsize: tuple[float, float] = (8, 4.8),
):
    """Lines of `y` over `x` (years), one per group.

    marcar_quebra: draw a dashed vertical line halfway between the two years
        in `quebra_entre` (default 2023 and 2024). `rotulo_quebra` is the
        text written next to it (none by default).
    conectar_quebra: if False, lines are not drawn across the break.
    rotulo_direto: write the group label at the end of each line (applies
        to up to 4 groups; a legend is always shown for >= 2 groups).
    destaque: one group drawn in ochre; the others turn neutral gray.
    Expects one row per (x, grupo); rows are sorted by x. Returns (fig, ax).
    """
    fig, ax = _novo_ax(ax, figsize)
    cols = [x, y] + ([grupo] if grupo else [])
    dados = df[cols].dropna(subset=[x, y]).sort_values(x)

    grupos = _ordem_grupos(dados[grupo], ordem) if grupo else [None]
    paleta = (
        _cores_grupos(grupos, cores, sequencial, destaque)
        if grupo
        else {None: CORES["principal"]}
    )
    if grupo:
        dup = dados.duplicated(subset=[x, grupo])
    else:
        dup = dados.duplicated(subset=[x])
    if dup.any():
        raise ValueError(f"more than one row per {x}" + (f" and {grupo}" if grupo else ""))

    meio_quebra = sum(quebra_entre) / 2
    ordem_desenho = sorted(grupos, key=lambda g: g == destaque) if destaque else grupos
    finais = []

    for g in ordem_desenho:
        sub = dados if g is None else dados[dados[grupo] == g]
        if sub.empty:
            continue
        cor = paleta[g]
        rotulo = None if g is None else _rotulo(g, rotulos)
        largura = 2.6 if (destaque is not None and g == destaque) else 2
        z = 3 if (destaque is not None and g == destaque) else 2

        if conectar_quebra or not marcar_quebra:
            partes = [sub]
        else:
            partes = [sub[sub[x] < meio_quebra], sub[sub[x] > meio_quebra]]
        for i, parte in enumerate(partes):
            if parte.empty:
                continue
            ax.plot(
                parte[x],
                parte[y],
                color=cor,
                linewidth=largura,
                marker="o" if marcadores else None,
                markersize=6,
                markeredgecolor=CORES["fundo"],
                markeredgewidth=1.5,
                linestyle=_estilo(g),
                label=rotulo if i == 0 else None,
                zorder=z,
            )
        ultimo = sub.iloc[-1]
        finais.append((ultimo[x], ultimo[y], rotulo))

    if marcar_quebra:
        ax.axvline(
            meio_quebra,
            color=CORES["texto_secundario"],
            linewidth=1,
            linestyle=(0, (4, 3)),
            zorder=1,
        )
        if rotulo_quebra:
            ax.annotate(
                rotulo_quebra,
                xy=(meio_quebra, 1),
                xycoords=ax.get_xaxis_transform(),
                xytext=(4, -2),
                textcoords="offset points",
                ha="left",
                va="top",
                fontsize=8,
                color=CORES["texto_secundario"],
            )

    # x axis: integer years only.
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{int(v)}"))
    ax.yaxis.set_major_formatter(_formatador_eixo(casas_y))
    if y_zero:
        ax.set_ylim(bottom=0)
    ax.margins(x=0.04)

    if grupo and rotulo_direto and len(grupos) <= 4 and finais:
        _rotulos_finais(ax, finais)

    _numeros_mono(ax)
    _legenda(ax, len(grupos) if grupo else 1)
    _textos(ax, titulo, subtitulo, rotulo_x, rotulo_y, nota)
    return fig, ax


def _rotulos_finais(ax, finais: list) -> None:
    """Write group labels to the right of each line end, nudged apart."""
    fig = ax.figure
    fig.canvas.draw()
    y0, y1 = ax.get_ylim()
    altura_px = ax.get_window_extent().height
    minimo = (y1 - y0) * 14 / max(altura_px, 1)  # ~14 px between labels
    itens = sorted(finais, key=lambda t: t[1])
    posicoes = []
    for _x, yv, _r in itens:
        alvo = yv if not posicoes else max(yv, posicoes[-1] + minimo)
        posicoes.append(alvo)
    x_max = max(t[0] for t in itens)
    for (xv, _yv, rotulo), yp in zip(itens, posicoes):
        ax.annotate(
            rotulo,
            xy=(x_max, yp),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            ha="left",
            fontsize=9,
            color=CORES["texto"],
            annotation_clip=False,
        )


# ---------------------------------------------------------------------------
# Bars with n
# ---------------------------------------------------------------------------


def barras_com_n(
    df: pd.DataFrame,
    coluna_categoria: str,
    coluna_valor: str,
    coluna_n: str,
    coluna_grupo: str | None = None,
    *,
    horizontal: bool = False,
    mostrar_valor: bool = True,
    casas_valor: int = 1,
    sufixo_valor: str = "",
    prefixo_n: str | None = None,
    ordem: Sequence | None = None,
    ordem_grupos: Sequence | None = None,
    rotulos: Mapping | None = None,
    rotulos_grupos: Mapping | None = None,
    cores: Mapping | Sequence | None = None,
    sequencial: bool = False,
    destaque=None,
    titulo: str | None = None,
    subtitulo: str | None = None,
    rotulo_x: str | None = None,
    rotulo_y: str | None = None,
    nota: str | None = None,
    ax=None,
    figsize: tuple[float, float] = (8, 4.8),
):
    """Bars of `coluna_valor` per category, each labeled with its n.

    Expects pre-aggregated data: one row per category (or per category and
    group), with the value in `coluna_valor` and the count in `coluna_n`.

    Without `coluna_grupo`: one series. Bars use the main color, or the
        sequential ramp across categories with sequencial=True (ordered
        bands), or ochre for the `destaque` category.
    Categories in FORA_DA_SEQUENCIA (e.g. "nao_sei") always go last, in
        gray, separated from the ordered levels by an extra gap.
    With `coluna_grupo`: grouped bars, one color per group (networks get
        CORES_REDE); `destaque` then names a group.
    Each bar gets its value (optional) and its n at the bar end; values
    use IBM Plex Mono and pt-BR separators. prefixo_n defaults to "n = ",
    or the compact "n=" for vertical bars with 3+ groups, where labels are
    narrow; with many groups or long n values prefer horizontal=True.
    Returns (fig, ax).
    """
    fig, ax = _novo_ax(ax, figsize)
    cols = [coluna_categoria, coluna_valor, coluna_n] + ([coluna_grupo] if coluna_grupo else [])
    dados = df[cols].dropna(subset=[coluna_categoria, coluna_valor])

    categorias = _ordem_grupos(dados[coluna_categoria], ordem)
    if ordem is None and not isinstance(dados[coluna_categoria].dtype, pd.CategoricalDtype):
        # keep input order
        categorias = _fora_para_o_fim(pd.unique(dados[coluna_categoria]))
    pos = np.arange(len(categorias), dtype=float)
    pos += np.array([_ESPACO_FORA if _fora(c) else 0.0 for c in categorias])

    if coluna_grupo:
        grupos = _ordem_grupos(dados[coluna_grupo], ordem_grupos)
        paleta = _cores_grupos(grupos, cores, sequencial, destaque)
    else:
        grupos = [None]
        if destaque is not None:
            paleta_cat = {
                c: (DESTAQUE if c == destaque else CORES["principal"]) for c in categorias
            }
        elif sequencial or cores is not None:
            paleta_cat = _cores_grupos(categorias, cores, sequencial)
        else:
            paleta_cat = {c: CORES["principal"] for c in categorias}
        paleta_cat.update({c: CORES["nao_sei"] for c in categorias if _fora(c)})

    k = len(grupos)
    if prefixo_n is None:
        prefixo_n = "n=" if (k >= 3 and not horizontal) else "n = "
    largura_total = 0.78
    largura = largura_total / k
    texto_cor = CORES["texto"]
    texto_sec = CORES["texto_secundario"]

    vmax = float(dados[coluna_valor].abs().max()) if len(dados) else 1.0

    for j, g in enumerate(grupos):
        sub = dados if g is None else dados[dados[coluna_grupo] == g]
        sub = sub.set_index(coluna_categoria).reindex(categorias)
        valores = sub[coluna_valor].to_numpy(dtype=float)
        ns = sub[coluna_n].to_numpy(dtype=float)
        desloc = (j - (k - 1) / 2) * largura
        if g is None:
            cor = [paleta_cat[c] for c in categorias]
            rotulo = None
        else:
            cor = paleta[g]
            rotulo = _rotulo(g, rotulos_grupos)

        kwargs = dict(
            color=cor,
            edgecolor=CORES["fundo"],
            linewidth=1.5,  # surface gap between adjacent bars
            label=rotulo,
            zorder=2,
        )
        if horizontal:
            barras = ax.barh(pos + desloc, valores, height=largura, **kwargs)
        else:
            barras = ax.bar(pos + desloc, valores, width=largura, **kwargs)

        for barra, v, n in zip(barras, valores, ns):
            if np.isnan(v):
                continue
            linhas = []
            if mostrar_valor:
                linhas.append((formatar_numero(v, casas_valor) + sufixo_valor, texto_cor))
            if not np.isnan(n):
                linhas.append((prefixo_n + formatar_numero(n), texto_sec))
            _anotar_barra(ax, barra, v, linhas, horizontal, k)

    rot_cat = [_rotulo(c, rotulos) for c in categorias]
    if horizontal:
        ax.set_yticks(pos, rot_cat)
        ax.invert_yaxis()
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", visible=True)
        ax.xaxis.set_major_formatter(_formatador_eixo())
        ax.set_xlim(0, vmax * 1.22)
        _numeros_mono(ax, "x")
        ax.tick_params(axis="y", length=0)
    else:
        ax.set_xticks(pos, rot_cat)
        ax.yaxis.set_major_formatter(_formatador_eixo())
        ax.set_ylim(0, vmax * (1.22 if mostrar_valor else 1.12))
        _numeros_mono(ax, "y")
        ax.tick_params(axis="x", length=0)

    _legenda(ax, k if coluna_grupo else 1)
    _textos(ax, titulo, subtitulo, rotulo_x, rotulo_y, nota)
    return fig, ax


def _anotar_barra(ax, barra, valor, linhas, horizontal: bool, k: int) -> None:
    """Stack the value and n labels just past the bar end."""
    tamanho = 7.5 if (k > 2 and not horizontal) else 9
    if horizontal:
        x = barra.get_x() + barra.get_width()
        y = barra.get_y() + barra.get_height() / 2
        # Two colors on one line: draw value, then n offset by its width.
        deslocamento = 4
        for t, cor in linhas:
            ann = ax.annotate(
                t,
                xy=(x, y),
                xytext=(deslocamento, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=tamanho,
                fontfamily=FONTE_NUMERO,
                color=cor,
            )
            ax.figure.canvas.draw()
            deslocamento += ann.get_window_extent().width * 72 / ax.figure.dpi + 6
    else:
        x = barra.get_x() + barra.get_width() / 2
        y = barra.get_height()
        desloc = 3
        for t, cor in reversed(linhas):
            ax.annotate(
                t,
                xy=(x, y),
                xytext=(0, desloc),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=tamanho,
                fontfamily=FONTE_NUMERO,
                color=cor,
            )
            desloc += tamanho + 2


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------


def salvar(fig, nome: str, *, dpi: int = 200, pasta: str | Path | None = None) -> Path:
    """Save `fig` as reports/figures/<nome>.png and return the path."""
    destino = Path(pasta) if pasta else FIGURES_DIR
    destino.mkdir(parents=True, exist_ok=True)
    nome = Path(nome).stem if nome.lower().endswith(".png") else nome
    caminho = destino / f"{nome}.png"
    fig.savefig(caminho, dpi=dpi, facecolor=CORES["fundo"])
    return caminho
