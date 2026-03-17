from __future__ import annotations

from pathlib import Path

from lct.knowledge_base import detect_topics_in_source


def read_source_text(source_path: str | None) -> str:
    if not source_path:
        return ""

    try:
        return Path(source_path).read_text(encoding="utf-8")
    except OSError:
        return ""


def detect_topic_hints(source_code: str) -> list[str]:
    hints: list[str] = []

    topics = detect_topics_in_source(source_code)

    for topic in topics:
        topic_id = topic.get("id", "")
        title = topic.get("title", "")

        if topic_id == "printf":
            hints.append("Vérifie aussi que printf affiche bien la valeur attendue.")
        elif topic_id == "scanf":
            hints.append("Ton programme utilise scanf, donc il dépend fortement du format d'entrée.")
        elif topic_id == "while":
            hints.append("Je vois une boucle while, donc vérifie bien la condition d'arrêt.")
        else:
            hints.append(f"Le code semble utiliser la notion suivante : {title}.")

    return hints


def explain_analysis_result(result, source_path: str | None = None) -> str:
    lines: list[str] = []
    source_code = read_source_text(source_path)
    topic_hints = detect_topic_hints(source_code)

    lines.append("Explication LCT :")

    if result.mode == "compile_error":
        stderr = result.compile_result.stderr.lower()

        if "source file not found" in stderr or "no such file or directory" in stderr:
            lines.append("- Le fichier source demandé n'existe pas ou le chemin est faux.")
            lines.append("- Vérifie le nom du fichier et le dossier indiqué dans la commande.")
        elif "expected ';'" in stderr:
            lines.append("- Il manque probablement un point-virgule ';' dans ton code.")
        elif "undefined reference" in stderr:
            lines.append("- Une fonction semble utilisée sans déclaration correcte ou sans le bon include.")
        else:
            lines.append("- Le compilateur a trouvé une erreur de syntaxe ou de déclaration.")
            lines.append("- Lis la ligne indiquée par GCC et vérifie les symboles juste avant l’erreur.")
            

    elif result.mode == "runtime_timeout":
        lines.append("- Le programme ne s'est pas terminé avant le délai limite.")
        lines.append("- La cause la plus probable est une boucle infinie ou une attente d'entrée non satisfaite.")

        if "while (1)" in source_code or "while(1)" in source_code:
            lines.append("- La boucle while(1) est un indice très fort de boucle infinie.")

    elif result.mode == "runtime_error":
        lines.append("- Le programme a bien compilé, mais il a échoué pendant l'exécution.")
        lines.append("- Vérifie les divisions, les accès mémoire, et les entrées utilisateur.")

    elif result.mode == "runtime_ok":
        lines.append("- Le programme compile et s'exécute correctement pour ce lancement simple.")
        lines.append("- Cela ne garantit pas encore qu'il est correct pour tous les cas de test.")

    else:
        lines.append("- Résultat non reconnu par l'explicateur actuel.")

    if topic_hints:
        lines.append("Indices utiles :")
        for hint in topic_hints:
            lines.append(f"- {hint}")

    return "\n".join(lines)


def explain_harness_result(result, source_path: str | None = None) -> str:
    lines: list[str] = []
    source_code = read_source_text(source_path)
    topic_hints = detect_topic_hints(source_code)

    lines.append("Explication LCT :")

    if result.mode == "compile_error":
        lines.append("- Le programme ne compile pas, donc les tests n'ont pas pu être exécutés.")
        lines.append("- Corrige d'abord les erreurs de compilation avant de vérifier la logique.")

    elif result.mode == "runtime_timeout":
        lines.append("- Au moins un test a dépassé le temps limite.")
        lines.append("- Cela indique souvent une boucle infinie ou une lecture d'entrée bloquante.")

        if "while (1)" in source_code or "while(1)" in source_code:
            lines.append("- Je vois une boucle infinie possible avec while(1).")

    elif result.mode == "logic_bug":
        lines.append("- Le programme compile et s’exécute, mais le résultat ne correspond pas aux tests attendus.")
        lines.append("- Cela indique probablement une erreur logique dans le calcul ou dans le traitement des entrées.")
        lines.append("- Commence par vérifier que les valeurs lues avec scanf sont bien celles que tu crois utiliser.")

        if "-" in source_code and "printf" in source_code:
            lines.append("- Vérifie surtout l'opérateur utilisé dans le calcul principal.")

    elif result.mode == "all_passed":
        lines.append("- Tous les tests sont passés.")
        lines.append("- Le comportement observé correspond aux résultats attendus pour cette série de tests.")

    else:
        lines.append("- Résultat de test non reconnu par l'explicateur actuel.")

    if topic_hints:
        lines.append("Indices utiles :")
        for hint in topic_hints:
            lines.append(f"- {hint}")

    return "\n".join(lines)