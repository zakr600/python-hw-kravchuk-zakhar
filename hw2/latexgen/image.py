def latex_image(path, width="0.8\\textwidth", caption=None):
    lines = [
        r"\begin{figure}[h]",
        r"\centering",
        rf"\includegraphics[width={width}]{{{path}}}",
    ]

    if caption:
        lines.append(rf"\caption{{{caption}}}")

    lines.append(r"\end{figure}")

    return "\n".join(lines)
