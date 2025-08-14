#!/usr/bin/env python
"""
Literalise
==========
"""

from __future__ import annotations

import os
import re
import sys
from textwrap import dedent

import matplotlib.font_manager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import colour

__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "PATH_MODULE_HINTS",
    "literalise",
]

PATH_MODULE_HINTS = os.path.join(
    os.path.dirname(__file__), "..", "colour", "hints", "__init__.py"
)


def literalise(path_module_hints: str = PATH_MODULE_HINTS) -> None:
    """
    Write various literals in the `colour.hints` module.

    Parameters
    ----------
    path_module_hints
        Path to the hints module.
    """

    with open(path_module_hints) as file_module_hints:
        content = file_module_hints.read()

    font_scalings = [
        scaling
        for scaling in matplotlib.font_manager.font_scalings
        if scaling is not None
    ]

    content = re.sub(
        "# LITERALISE::BEGIN.*?# LITERALISE::END",
        dedent(
            f"""
            # LITERALISE::BEGIN
            LiteralChromaticAdaptationTransform = \
                Literal{sorted(colour.CHROMATIC_ADAPTATION_TRANSFORMS)}

            LiteralColourspaceModel = Literal{sorted(colour.COLOURSPACE_MODELS)}

            LiteralRGBColourspace = Literal{sorted(colour.RGB_COLOURSPACES.keys())}

            LiteralLogEncoding = Literal{sorted(colour.LOG_ENCODINGS)}

            LiteralLogDecoding = Literal{sorted(colour.LOG_DECODINGS)}

            LiteralOETF = Literal{sorted(colour.OETFS)}

            LiteralOETFInverse = Literal{sorted(colour.OETF_INVERSES)}

            LiteralEOTF = Literal{sorted(colour.EOTFS)}

            LiteralEOTFInverse = Literal{sorted(colour.EOTF_INVERSES)}

            LiteralCCTFEncoding = Literal{sorted(colour.CCTF_ENCODINGS)}

            LiteralCCTFDecoding = Literal{sorted(colour.CCTF_DECODINGS)}

            LiteralOOTF = Literal{sorted(colour.OOTFS)}

            LiteralOOTFInverse = Literal{sorted(colour.OOTF_INVERSES)}

            LiteralLUTReadMethod = Literal{sorted(colour.io.LUT_READ_METHODS)}

            LiteralLUTWriteMethod = Literal{sorted(colour.io.LUT_WRITE_METHODS)}

            LiteralDeltaEMethod = Literal{sorted(colour.DELTA_E_METHODS)}

            LiteralFontScaling = Literal{font_scalings}
            # LITERALISE::END
            """
        ).strip(),
        content,
        flags=re.DOTALL,
    )

    with open(path_module_hints, "w") as file_module_hints:
        file_module_hints.write(content)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    literalise()
