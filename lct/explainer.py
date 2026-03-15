from __future__ import annotations

from pathlib import Path

from lct.schemas import AnalysisResult, HarnessResult


def read_source_text(source_path: str) -> str:
    try:
        return Path(source_path).read_text(encoding="utf-8")
    except OSError:
        return ""


def detect_topic_hints(source_code: str) -> list[str]:
    hints: list[str] = []

    if "scanf" in source_code:
        hints.append("Ton programme utilise scanf, donc il dépend fortement du format d'entrée.")
    if "printf" in source_code:
        hints.append("Vérifie aussi que printf affiche bien la valeur attendue.")
    if "while (1)" in source_code or "while(1)" in source_code:
        hints.append("Je vois une boucle infinie possible avec while(1).")
    if "[" in source_code and "]" in source_code:
        hints.append("Le code semble manipuler des tableaux ou des indices.")
    if "*" in source_code and "&" in source_code:
        hints.append("Le code semble utiliser des pointeurs ou des adresses.")
    if "for (" in source_code or "for(" in source_code:
        hints.append("Le code contient une boucle for, vérifie les bornes de la boucle.")
    if "if (" in source_code or "if(" in source_code:
        hints.append("Le code contient une condition if, vérifie bien la logique de la condition.")

    return hints


def explain_compile_error(stderr: str, source_code: str) -> list[str]:
    text = (
        stderr.lower()
        .replace("‘", "'")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )

    explanations: list[str] = []

    if "expected ';'" in text or "expected ';' before" in text:
        explanations.append("Il manque probablement un point-virgule ';' dans ton code.")
    if "undeclared" in text:
        explanations.append("Tu utilises probablement une variable qui n'a pas été déclarée.")
    if "expected ')'" in text or "expected ')' before" in text:
        explanations.append("Il manque probablement une parenthèse fermante ')'.")
    if "expected '}'" in text or "expected '}' before" in text:
        explanations.append("Il manque probablement une accolade fermante '}'.")
    if "expected expression" in text:
        explanations.append("Le compilateur attend une expression valide à cet endroit.")
    if "implicit declaration" in text:
        explanations.append("Une fonction semble utilisée sans déclaration correcte ou sans le bon include.")
    if "scanf" in source_code and "%d" in source_code and "&" not in source_code:
        explanations.append("Avec scanf, n'oublie pas souvent d'utiliser l'adresse des variables avec '&'.")

    if not explanations:
        explanations.append("Le compilateur a trouvé une erreur de syntaxe ou de déclaration.")
        explanations.append("Lis la ligne indiquée par GCC et vérifie les symboles juste avant l'erreur.")

    return explanations


def explain_runtime_timeout(source_code: str) -> list[str]:
    explanations = [
        "Le programme semble ne jamais se terminer avant le délai limite.",
        "La cause la plus probable est une boucle infinie ou une attente d'entrée non satisfaite.",
    ]

    if "while (1)" in source_code or "while(1)" in source_code:
        explanations.append("La boucle while(1) est un indice très fort de boucle infinie.")
    if "scanf" in source_code:
        explanations.append("Vérifie aussi si le programme attend une entrée clavier qui n'a pas été fournie.")

    return explanations


def explain_runtime_error(source_code: str) -> list[str]:
    explanations = [
        "Le programme compile, mais il échoue pendant l'exécution.",
        "Vérifie les accès mémoire, les divisions interdites, et les entrées utilisateur.",
    ]

    if "[" in source_code and "]" in source_code:
        explanations.append("Si tu utilises un tableau, vérifie que les indices restent dans les limites.")
    if "*" in source_code:
        explanations.append("Si tu utilises des pointeurs, vérifie qu'ils pointent vers une zone valide.")

    return explanations


def explain_logic_bug(source_code: str) -> list[str]:
    explanations = [
        "Le programme compile et s'exécute, mais le résultat ne correspond pas aux tests attendus.",
        "Cela indique probablement une erreur logique dans le calcul ou dans le traitement des entrées.",
    ]

    if "scanf" in source_code:
        explanations.append("Commence par vérifier que les valeurs lues avec scanf sont bien celles que tu crois utiliser.")
    if "+" in source_code or "-" in source_code or "*" in source_code or "/" in source_code:
        explanations.append("Vérifie surtout l'opérateur utilisé dans le calcul principal.")
    if "if (" in source_code or "if(" in source_code:
        explanations.append("Une condition if incorrecte peut facilement produire une mauvaise sortie.")
    if "for (" in source_code or "for(" in source_code:
        explanations.append("Vérifie aussi les bornes de boucle : début, fin, et incrément.")

    return explanations


def explain_tests_ok(source_code: str) -> list[str]:
    explanations = [
        "Tous les tests actuels passent.",
        "Cela veut dire que, pour ces cas de test, le programme se comporte comme attendu.",
    ]

    if "scanf" in source_code:
        explanations.append("Tu peux encore ajouter d'autres cas de test pour vérifier plus d'entrées possibles.")

    return explanations


def format_explanation_block(lines: list[str], topic_hints: list[str]) -> str:
    output_lines = ["Explication LCT :"]

    for line in lines:
        output_lines.append(f"- {line}")

    if topic_hints:
        output_lines.append("Indices utiles :")
        for hint in topic_hints:
            output_lines.append(f"- {hint}")

    return "\n".join(output_lines)


def explain_analysis_result(result: AnalysisResult) -> str:
    source_code = read_source_text(result.compile_result.source_path)
    topic_hints = detect_topic_hints(source_code)

    if result.mode == "compile_error":
        lines = explain_compile_error(result.compile_result.stderr, source_code)
    elif result.mode == "runtime_timeout":
        lines = explain_runtime_timeout(source_code)
    elif result.mode == "runtime_error":
        lines = explain_runtime_error(source_code)
    elif result.mode == "runtime_ok":
        lines = [
            "Le programme compile et s'exécute correctement pour ce lancement simple.",
            "Cela ne garantit pas encore qu'il est correct pour tous les cas de test.",
        ]
    else:
        lines = ["Résultat non reconnu par l'explainer local."]

    return format_explanation_block(lines, topic_hints)


def explain_harness_result(result: HarnessResult) -> str:
    source_code = read_source_text(result.compile_result.source_path)
    topic_hints = detect_topic_hints(source_code)

    if result.mode == "compile_error":
        lines = explain_compile_error(result.compile_result.stderr, source_code)
    elif result.mode == "runtime_timeout":
        lines = explain_runtime_timeout(source_code)
    elif result.mode == "runtime_error":
        lines = explain_runtime_error(source_code)
    elif result.mode == "logic_bug":
        lines = explain_logic_bug(source_code)
    elif result.mode == "tests_ok":
        lines = explain_tests_ok(source_code)
    else:
        lines = ["Résultat non reconnu par l'explainer local."]

    return format_explanation_block(lines, topic_hints)