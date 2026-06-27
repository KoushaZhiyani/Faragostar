import re


# =========================================================
# COLUMN EXCLUSION ENGINE
# =========================================================

def should_exclude_column(column, rules):
    """
    Check if a column should be excluded based on rules.

    Supported rules:
    - "=COLUMN"   -> exact match
    - "*_SUFFIX"  -> suffix match
    - "PREFIX_*"  -> prefix match
    - regex object
    """

    col = column.upper()

    for rule in rules:

        # Exact match
        if isinstance(rule, str) and rule.startswith("="):
            if col == rule[1:].upper():
                return True

        # Suffix match
        elif isinstance(rule, str) and rule.startswith("*"):
            if col.endswith(rule[1:].upper()):
                return True

        # Prefix match
        elif isinstance(rule, str) and rule.endswith("*"):
            if col.startswith(rule[:-1].upper()):
                return True

        # Regex
        elif hasattr(rule, "search"):
            if rule.search(column):
                return True

    return False


# =========================================================
# SQL VALUE SPLITTER
# =========================================================

def split_sql_values(values_text):
    """
    Safely split SQL VALUES(...) content into individual values.
    """

    values = []
    current = []

    in_single = False
    in_double = False
    paren_depth = 0

    i = 0
    n = len(values_text)

    while i < n:
        ch = values_text[i]

        # Escape handling
        if ch == "\\":
            current.append(ch)
            if i + 1 < n:
                current.append(values_text[i + 1])
                i += 2
                continue

        # Single quotes
        if ch == "'" and not in_double:

            if in_single and i + 1 < n and values_text[i + 1] == "'":
                current.append("''")
                i += 2
                continue

            in_single = not in_single
            current.append(ch)
            i += 1
            continue

        # Double quotes
        if ch == '"' and not in_single:

            if in_double and i + 1 < n and values_text[i + 1] == '"':
                current.append('""')
                i += 2
                continue

            in_double = not in_double
            current.append(ch)
            i += 1
            continue

        # Split only at top-level commas
        if not in_single and not in_double:

            if ch == "(":
                paren_depth += 1

            elif ch == ")":
                paren_depth -= 1

            elif ch == "," and paren_depth == 0:
                values.append("".join(current).strip())
                current = []
                i += 1
                continue

        current.append(ch)
        i += 1

    if current:
        values.append("".join(current).strip())

    return values


# =========================================================
# PARSE INSERT STATEMENT
# =========================================================

def parse_insert(stmt):
    """
    Extract:
    - table name
    - columns
    - values
    """

    header = re.search(
        r'INSERT\s+INTO\s+`?([\w_]+)`?\s*\(',
        stmt,
        re.IGNORECASE
    )

    if not header:
        return None

    table = header.group(1)

    # ----------------------------
    # Extract column section
    # ----------------------------
    start = stmt.find("(", header.end() - 1)

    depth = 1
    pos = start + 1

    while pos < len(stmt) and depth > 0:
        if stmt[pos] == "(":
            depth += 1
        elif stmt[pos] == ")":
            depth -= 1
        pos += 1

    columns_text = stmt[start + 1:pos - 1]

    columns = [
        c.strip().strip("`")
        for c in columns_text.split(",")
    ]

    # ----------------------------
    # Extract VALUES section
    # ----------------------------
    values_match = re.search(r"\bVALUES\b", stmt, re.IGNORECASE)
    if not values_match:
        return None

    start_v = stmt.find("(", values_match.end())
    if start_v == -1:
        return None

    depth = 1
    end_v = start_v + 1

    in_single = False
    in_double = False

    while end_v < len(stmt):

        ch = stmt[end_v]

        if ch == "'" and not in_double:
            in_single = not in_single

        elif ch == '"' and not in_single:
            in_double = not in_double

        elif not in_single and not in_double:

            if ch == "(":
                depth += 1

            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break

        end_v += 1

    values_text = stmt[start_v + 1:end_v]
    values = split_sql_values(values_text)

    return table, columns, values


# =========================================================
# PROCESS INSERT
# =========================================================

def process_insert(stmt, target_table=None, exclude_rules=None):
    """
    Clean and transform INSERT statement.
    """

    if exclude_rules is None:
        exclude_rules = ["*_LABEL"]

    parsed = parse_insert(stmt)

    if not parsed:
        return stmt

    table, columns, values = parsed

    if len(columns) != len(values):
        print("Mismatch columns/values")
        return stmt

    keep = [
        i for i, col in enumerate(columns)
        if not should_exclude_column(col, exclude_rules)
    ]

    new_cols = [columns[i] for i in keep]
    new_vals = [values[i] for i in keep]

    table = target_table or table

    cols_sql = ", ".join(f"`{c}`" for c in new_cols)
    vals_sql = ", ".join(new_vals)

    return f"INSERT INTO `{table}` ({cols_sql}) VALUES ({vals_sql});"


# =========================================================
# SPLIT SQL FILE INTO STATEMENTS
# =========================================================

def split_statements(sql):
    """
    Split SQL file into statements safely.
    """

    statements = []
    current = []

    in_single = False
    in_double = False

    for ch in sql:

        if ch == "'" and not in_double:
            in_single = not in_single

        elif ch == '"' and not in_single:
            in_double = not in_double

        if ch == ";" and not in_single and not in_double:
            current.append(ch)
            statements.append("".join(current))
            current = []
        else:
            current.append(ch)

    if current:
        statements.append("".join(current))

    return statements


# =========================================================
# MAIN PIPELINE
# =========================================================

def fix_insert_statements(
    input_file,
    output_file,
    target_table=None,
    exclude_rules=None
):
    """
    Process SQL file:
    - remove selected columns
    - optionally rename table
    """

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    statements = split_statements(content)

    output = []

    for stmt in statements:

        if re.match(r"^\s*INSERT\s+INTO", stmt, re.IGNORECASE):
            stmt = process_insert(
                stmt,
                target_table,
                exclude_rules
            )

        output.append(stmt)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(output))

    print(f"Done -> {output_file}")


# =========================================================
# EXAMPLE RUN
# =========================================================

if __name__ == "__main__":

    fix_insert_statements(
        "pmt_kharid_kala_grid.sql",
        "pmt_kharid_kala_grid_edited.sql",
        target_table="new_table",
        exclude_rules=[
            "*_LABEL",   # default behavior
            "=APP_STATUS",
            "=APP_NUMBER",
        ]
    )