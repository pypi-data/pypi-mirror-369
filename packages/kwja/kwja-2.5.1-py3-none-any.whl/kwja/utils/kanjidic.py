import unicodedata
from importlib.abc import Traversable
from importlib.resources import as_file
from pathlib import Path
from typing import Any, Union

from kwja.utils.constants import KATA2HIRA


class KanjiDic:
    def __init__(self, fpath: Union[Path, Traversable]) -> None:
        self.entries: dict[str, Any] = {
            "°": {
                "reading": ["ど"],
            },
            "&": {
                "reading": ["あんど"],
            },
            ".": {
                "reading": ["てん"],
            },
            ":": {
                "reading": ["じ"],  # 11:00: じゅういちじ
            },
            "1": {
                "reading": [
                    "いち",
                    "いっ",
                    "ひと",
                    "ひとつ",
                    "わん",
                    "ふぁーすと",
                    "じゅう",
                    "じゅっ",
                    "ひゃく",
                    "ひゃっ",
                    "いっぴゃく",
                    "せん",
                    "いっせん",
                    "まん",
                    "いちまん",
                    "じゅうまん",
                    "ひゃくまん",
                    "せんまん",
                    "いっせんまん",
                    "おく",
                    "おっ",
                    "いちおく",
                    "じゅうおく",
                    "じゅくおっ",
                    "ひゃくおく",
                    "ひゃくおっ",
                    "せんおく",
                    "せんおっ",
                    "いっせんおく",
                    "いっせんおっ",
                    "ちょう",
                    "いっちょう",
                ],
            },
            "2": {
                "reading": [
                    "に",
                    "じ",
                    "ふた",
                    "ふたつ",
                    "つー",
                    "とぅー",
                    "せかんど",
                    "にじゅう",
                    "にじゅっ",
                    "にひゃく",
                    "にひゃっ",
                    "にせん",
                    "にまん",
                    "にじゅうまん",
                    "にひゃくまん",
                    "にせんまん",
                    "におく",
                    "におっ",
                    "にじゅうおく",
                    "にじゅうおっ",
                    "にひゃくおく",
                    "にひゃくおっ",
                    "にせんおく",
                    "にせんおっ",
                    "にちょう",
                ],
            },
            "3": {
                "reading": [
                    "さん",
                    "み",
                    "みっつ",
                    "みっ",
                    "すりー",
                    "さーど",
                    "さんじゅう",
                    "さんじゅっ",
                    "さんびゃく",
                    "さんびゃっ",
                    "さんぜん",
                    "さんまん",
                    "さんじゅうまん",
                    "さんびゃくまん",
                    "さんぜんまん",
                    "さんおく",
                    "さんおっ",
                    "さんじゅうおく",
                    "さんじゅうおっ",
                    "さんびゃくおく",
                    "さんびゃくおっ",
                    "さんぜんおく",
                    "さんぜんおっ",
                    "さんちょう",
                ],
            },
            "4": {
                "reading": [
                    "し",
                    "よ",
                    "よっつ",
                    "よっ",
                    "よん",
                    "ふぉー",
                    "ふぉーす",
                    "よんじゅう",
                    "よんじゅっ",
                    "よんひゃく",
                    "よんひゃっ",
                    "よんせん",
                    "よんまん",
                    "よんじゅうまん",
                    "よんひゃくまん",
                    "よんせんまん",
                    "よんおく",
                    "よんおっ",
                    "よんじゅうおく",
                    "よんじゅうおっ",
                    "よんひゃくおく",
                    "よんひゃくおっ",
                    "よんせんおく",
                    "よんせんおっ",
                    "よんちょう",
                ],
            },
            "5": {
                "reading": [
                    "ご",
                    "いつ",
                    "いつ",
                    "ふぁいぶ",
                    "ふぃふす",
                    "ごじゅう",
                    "ごじゅっ",
                    "ごひゃく",
                    "ごひゃっ",
                    "ごせん",
                    "ごまん",
                    "ごじゅうまん",
                    "ごひゃくまん",
                    "ごぜんまん",
                    "ごおく",
                    "ごおっ",
                    "ごじゅうおく",
                    "ごじゅうおっ",
                    "ごひゃくおく",
                    "ごひゃくおっ",
                    "ごぜんおく",
                    "ごぜんおっ",
                    "ごちょう",
                ],
            },
            "6": {
                "reading": [
                    "ろく",
                    "ろっ",
                    "む",
                    "むっ",
                    "むっつ",
                    "しっくす",
                    "ろくじゅう",
                    "ろくじゅっ",
                    "ろっぴゃく",
                    "ろっぴゃっ",
                    "ろくせん",
                    "ろくまん",
                    "ろくじゅうまん",
                    "ろっぴゃくまん",
                    "ろくせんまん",
                    "ろくおく",
                    "ろくおっ",
                    "ろくじゅうおく",
                    "ろくじゅうおっ",
                    "ろっぴゃくおく",
                    "ろっぴゃくおっ",
                    "ろくせんおく",
                    "ろくせんおっ",
                    "ろくちょう",
                ],
            },
            "7": {
                "reading": [
                    "しち",
                    "なな",
                    "ななつ",
                    "なの",
                    "せぶん",
                    "ななじゅう",
                    "ななじゅっ",
                    "ななひゃく",
                    "ななひゃっ",
                    "ななせん",
                    "ななまん",
                    "ななじゅうまん",
                    "ななひゃくまん",
                    "ななせんまん",
                    "ななおく",
                    "ななおっ",
                    "ななじゅうおく",
                    "ななじゅうおっ",
                    "ななひゃくおく",
                    "ななひゃくおっ",
                    "ななせんおく",
                    "ななせんおっ",
                    "ななちょう",
                ],
            },
            "8": {
                "reading": [
                    "はち",
                    "はっ",
                    "や",
                    "やっつ",
                    "えいと",
                    "はちじゅう",
                    "はちじゅっ",
                    "はっぴゃく",
                    "はっぴゃっ",
                    "はっせん",
                    "はちまん",
                    "はちじゅうまん",
                    "はっぴゃくまん",
                    "はっせんまん",
                    "はちおく",
                    "はちおっ",
                    "はちじゅうおく",
                    "はちじゅうおっ",
                    "はっぴゃくおく",
                    "はっぴゃくおっ",
                    "はっせんおく",
                    "はっせんおっ",
                    "はっちょう",
                ],
            },
            "9": {
                "reading": [
                    "きゅう",
                    "く",
                    "ここの",
                    "ここのつ",
                    "ないん",
                    "きゅうじゅう",
                    "きゅうじゅっ",
                    "きゅうひゃく",
                    "きゅうひゃっ",
                    "きゅうせん",
                    "きゅうまん",
                    "きゅうじゅうまん",
                    "きゅうひゃくまん",
                    "きゅうせんまん",
                    "きゅうおく",
                    "きゅうおっ",
                    "きゅうじゅうおく",
                    "きゅうじゅうおっ",
                    "きゅうひゃくおく",
                    "きゅうひゃくおっ",
                    "きゅうせんおく",
                    "きゅうせんおっ",
                    "きゅうちょう",
                ],
            },
            "0": {
                "reading": ["れい", "ぜろ", "まる"],
                # "じゅう", "じゅっ", "ひゃく", "ひゃっ", "せん", "まん", "おく", "おっ", "ちょう"],
            },
        }
        if isinstance(fpath, Traversable):
            with as_file(fpath) as path:
                self._parse(path)
        else:
            self._parse(fpath)

    def _parse(self, path: Path) -> None:
        with open(path) as fp:
            for line in fp:
                if len(line) <= 0 or line[0] == "#":
                    continue
                fields = line.rstrip().split(" ")
                struct: dict[str, Any] = {
                    "has_nanori": False,
                }
                self.entries[fields.pop(0)] = struct
                fields.pop(0)  # jis
                while len(fields) > 0:
                    f = fields.pop(0)
                    if len(f) <= 0:
                        continue
                    if f[0] == "B":
                        struct["radical_number"] = int(f[1:])
                    elif f[0] == "C":
                        struct["radical_number_classical"] = int(f[1:])
                    elif f[0] == "S":
                        struct["strokes"] = int(f[1:])
                    elif f[0] == "G":
                        struct["grade"] = int(f[1:])
                    elif f[0] == "F":
                        struct["freq"] = int(f[1:])
                    elif f[0] == "T":
                        struct["has_nanori"] = True
                    elif f[0] == "Y":
                        # pinyin
                        if "pinyin" not in struct:
                            struct["pinyin"] = [f[1:]]
                        else:
                            struct["pinyin"].append(f[1:])
                    elif f[0] == "W":
                        # korean
                        if "korean" not in struct:
                            struct["korean"] = [f[1:]]
                        else:
                            struct["korean"].append(f[1:])
                    elif unicodedata.name(f[0])[0:8] in ("HIRAGANA", "KATAKANA"):
                        f = f.translate(KATA2HIRA)
                        if f[-1] == "-":
                            f = f[:-1]
                        if "reading" not in struct:
                            struct["reading"] = [f]
                        else:
                            struct["reading"].append(f)
                    elif f[0] == "{":
                        if f[-1] == "}":
                            gloss = f[1:-1]
                        else:
                            gloss = f[1:] + " "
                            while len(fields) > 0:
                                f2 = fields.pop(0)
                                if f2[-1] == "}":
                                    gloss += f2[:-1]
                                    break
                                else:
                                    gloss += f2 + " "
                        if "gloss" not in struct:
                            struct["gloss"] = [gloss]
                        else:
                            struct["gloss"].append(gloss)
