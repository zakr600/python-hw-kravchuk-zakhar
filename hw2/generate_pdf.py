from latexgen import latex_table, latex_image

table = [
    ["A", "B"],
    [1, 2],
    [3, 4],
]

doc = r"""
\documentclass{article}
\usepackage{graphicx}
\begin{document}
""" + latex_table(table) + "\n\n" + latex_image(
    "example.png", caption="Example image"
) + r"""
\end{document}
"""

with open("result.tex", "w") as f:
    f.write(doc)
