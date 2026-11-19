"""Apply perf-config dedup edits to the test instance. Run only after the game is closed."""
import os, re, shutil, sys

MC = os.path.expandvars(r"%APPDATA%\PrismLauncher\instances\1.12.2-edit\minecraft")

EDITS = {
    MC + r"\config\loliasm.cfg": [
        (r"(B:crashReportImprovements=)true", r"\1false"),
        (r"(B:returnToMainMenuAfterCrash=)true", r"\1false"),
        (r"(B:rewriteLoggingWithDeobfuscatedNames=)true", r"\1false"),
        (r"(B:logClassesThatCallBakedQuadCtor=)true", r"\1false"),
    ],
    MC + r"\optionsof.txt": [
        (r"(?m)^(ofSmartAnimations:)true", r"\1false"),
    ],
}

for path, subs in EDITS.items():
    shutil.copyfile(path, path + ".perf.bak")
    text = open(path, encoding="utf-8").read()
    for pat, rep in subs:
        text, n = re.subn(pat, rep, text)
        print(f"{path.split(chr(92))[-1]}: {pat} -> {n}")
    open(path, "w", encoding="utf-8", newline="").write(text)
