def latex_table(data):
    if not data or not all(isinstance(row, list) for row in data):
        raise ValueError("Input must be a non-empty 2D list")

    cols = len(data[0])
    if any(len(row) != cols for row in data):
        raise ValueError("All rows must have the same length")

    col_spec = "|" + "|".join(["c"] * cols) + "|"

    def format_row(row):
        return " & ".join(map(str, row)) + r" \\ \hline"

    body = "\n".join(map(format_row, data))

    return (
        r"\begin{tabular}{" + col_spec + "}\n"
        r"\hline" + "\n"
        + body + "\n"
        r"\end{tabular}"
    )
