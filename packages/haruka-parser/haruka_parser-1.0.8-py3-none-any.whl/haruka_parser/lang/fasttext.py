from fasttext.FastText import _FastText
import json
from collections import defaultdict
import string
import re
import unicodedata
from .blocks import unicodeBlock
# from haruka_parser.dictionary.language import FastTextLangeuageList

# def _makeNonAlphaRe():
#     nonAlpha = ["[^"]
#     for i in range(sys.maxunicode):
#         c = chr(i)
#         if c.isalpha():
#             nonAlpha.append(c)
#     nonAlpha.append("]")
#     nonAlpha = "".join(nonAlpha)
#     return re.compile(nonAlpha)


# nonAlphaRe = _makeNonAlphaRe()
spaceRe = re.compile("\s+", re.UNICODE)
PUNCTUATION = string.punctuation
PUNCTUATION += "0123456789！？。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."
PUNCTUATION = re.escape(PUNCTUATION)
nonAlphaRe = re.compile(f"[{PUNCTUATION}]")

# BASIC_LATIN = "en ceb ha so tlh id haw la sw eu nr nso zu xh ss st tn ts".split()
# EXTENDED_LATIN = "cs af pl hr ro sk sl tr hu az et sq ca es fr de nl it da is nb sv fi lv pt ve lt tl cy".split()
# ALL_LATIN = BASIC_LATIN + EXTENDED_LATIN
# CYRILLIC = "ru uk kk uz mn sr mk bg ky".split()
# ARABIC = "ar fa ps ur".split()
# DEVANAGARI = "hi ne".split()

def _get_fasttext_langs(lang):
    return list(filter(lambda x: lang in x, FastTextLangeuageList))

def _update_fasttext_langs(fasttext_model):
    global FastTextLangeuageList, ARABIC, CYRILLIC, DEVANAGARI, LATIN, CHINESE, KOREA, JAPANESE, SINGLETONS, PT, UNKNOWN

    labels = fasttext_model.get_labels()
    FastTextLangeuageList = [i.split("__label__")[1] for i in labels]

    ARABIC = _get_fasttext_langs("Arab")
    CYRILLIC = _get_fasttext_langs("Cyrl")
    DEVANAGARI = _get_fasttext_langs("Deva")
    LATIN = _get_fasttext_langs("Latn")
    CHINESE = _get_fasttext_langs("Hans") + _get_fasttext_langs("Hant") + _get_fasttext_langs("Hani")
    JAPANESE = _get_fasttext_langs("Jpan")
    KOREA = _get_fasttext_langs("Hang")

    SINGLETONS = [
        ("Armenian", _get_fasttext_langs("Armn")),
        ("Hebrew", _get_fasttext_langs("Hebr")),
        ("Bengali", _get_fasttext_langs("Beng")),
        ("Gurmukhi", _get_fasttext_langs("Guru")),
        ("Greek", _get_fasttext_langs("Grek")),
        ("Gujarati", _get_fasttext_langs("Gujr")),
        ("Oriya", _get_fasttext_langs("Orya")),
        ("Tamil", _get_fasttext_langs("Taml")),
        ("Telugu", _get_fasttext_langs("Telu")),
        ("Kannada", _get_fasttext_langs("Knda")),
        ("Malayalam", _get_fasttext_langs("Mlym")),
        ("Sinhala", _get_fasttext_langs("Sinh")),
        ("Thai", _get_fasttext_langs("Thai")),
        ("Lao", _get_fasttext_langs("Laoo")),
        ("Tibetan", _get_fasttext_langs("Tibt")),
        ("Myanmar", _get_fasttext_langs("Mymr")),
        ("Georgian", _get_fasttext_langs("Geor")),
        ("Mongolian", "khk_Cyrl"),
        ("Khmer", _get_fasttext_langs("Khmr")),
    ]

    PT = "pt_BR pt_PT".split()

    UNKNOWN = "UNKNOWN"

    # print(FastTextLangeuageList)

    # print(ARABIC, "\n\n",CYRILLIC, "\n\n", DEVANAGARI, "\n\n", LATIN, "\n\n", CHINESE, "\n\n", JAPANESE, "\n\n", KOREA, "\n\n", SINGLETONS, "\n\n", PT, "\n\n", UNKNOWN)
    # exit()


def normalize(u):
    """Convert to normalized unicode.
    Remove non-alpha chars and compress runs of spaces.
    """
    u = unicodedata.normalize("NFC", u)
    # u = u.translate(str.maketrans("", "", PUNCTUATION))
    u = nonAlphaRe.sub(" ", u)
    u = spaceRe.sub(" ", u)
    u = u.strip()
    return u


def _identify(sample, scripts):
    res = []

    if len(sample) < 3:
        return res

    if "Chinese" in scripts:
        res.extend(CHINESE)

    if "Korea" in scripts:
        res.extend(KOREA)

    if "Japanese" in scripts:
        res.extend(JAPANESE)

    if "Cyrillic" in scripts:
        res.extend(CYRILLIC)

    if "Arabic" in scripts:
        res.extend(ARABIC)

    if "Devanagari" in scripts:
        res.extend(DEVANAGARI)

    # Try languages with unique scripts
    for blockName, langName in SINGLETONS:
        if blockName in scripts:
            res.extend(langName)

    # if "Latin Extended Additional" in scripts:
    #     res.extend("vie_Latn")

    # if "Extended Latin" in scripts or "Basic Latin" in scripts:
    #     res.extend(LATIN)

    return res

CHINESE_BLOCKS = {"康熙部首", "注音", "汉字部首补充"}

JAPANESE_BLOCKS = {
    "平假名",
    "片假名",
    "假名扩充甲",
    "假名扩充乙",
    "假名补充",
    "小型假名扩充",
    "片假名音标扩充"
}

def find_runs(text):
    """Count the number of characters in each character block"""
    run_types = defaultdict(int)

    totalCount = 0

    for c in text:
        if c.isalpha():
            block = unicodeBlock(c)
            zh_block, en_block = block[0], block[-1]

            # if en_block.endswith(" Supplement"):
            #     en_block = en_block[:-11]
            # if en_block not in {"Basic Latin", "Latin Extended Additional"}:
            #     en_block = en_block.split()[0]

            if "CJK" in en_block or "中日韩" in zh_block:
                run_types["Chinese"] += 1
                run_types["Japanese"] += 1
                run_types["Korea"] += 1
            elif zh_block in CHINESE_BLOCKS:
                run_types["Chinese"] += 1
            elif zh_block in JAPANESE_BLOCKS:
                run_types["Japanese"] += 1
                run_types["Japanese_ONLY"] += 1
            elif "谚文" in zh_block:
                run_types["Korea"] += 1
                run_types["Korea_ONLY"] += 1
            elif "阿拉伯" in zh_block:
                run_types["Arabic"] += 1
            else:
                run_types[en_block.split()[0]] += 1
            totalCount += 1

    # import pprint
    # pprint.pprint(run_types)

    # return run types that used for 40% or more of the string
    # always return basic latin if found more than 15%
    # and extended additional latin if over 10% (for Vietnamese)
    relevant_runs = []
    for key, value in run_types.items():
        pct = (value * 100) / totalCount
        if pct >= 30:
            relevant_runs.append(key)
        elif key == "Korea_ONLY" and (pct >= 15):
            return ["Korea"]
        elif key == "Japanese_ONLY" and (pct >= 15):
            return ["Japanese"]
        # elif key == "Basic Latin" and (pct >= 15):
        #     relevant_runs.append(key)
        # elif key == "Latin Extended Additional" and (pct >= 10):
        #     relevant_runs.append(key)

    return relevant_runs


def guess_lang(text):
    # text = normalize(text)
    return _identify(text, find_runs(text))


def _predict_language(ft_model, text):
    
    if not hasattr(_predict_language, '_last_model') or _predict_language._last_model != ft_model:
        _update_fasttext_langs(ft_model)
        _predict_language._last_model = ft_model
    
    text = normalize(text)
    guess_lang_list = guess_lang(text)

    # If there is only one possibility to return directly (certainly not for Chinese)
    # if len(guess_lang_list) == 1:
    #     return guess_lang_list[0], 1.0

    # text = text.replace("\n", " ").replace("\t", " ").strip()
    label = ft_model.predict(text, -1, threshold=0.1) # -1e6

    # If there are multiple guess possibilities, return the one with the highest score
    if len(guess_lang_list) >= 1:
        for lang, score in zip(label[0], label[1]):
            lang = lang.split("__label__")[1]
            if score > 0.2 and lang in guess_lang_list:
                return lang, label

    # If there is no guess, return the one with the highest score; if there is a guess and no guess possibility is larger than 0.3, return unknown (expect to drop data with low confidence)
    for lang, score in zip(label[0], label[1]):
        lang = lang.split("__label__")[1]
        if score > 0.5:
            return lang, label

    return "unknown", label


def predict_language(ft_model, text, with_score=False):
    lang, label = _predict_language(ft_model, text)

    if with_score:
        return lang, label
    return lang


if __name__ == "__main__":
    if "ft_model" not in globals():
        ft_model = _FastText(model_path="model.bin")

    for line in open("zho_Hans.00000000.jsonl").readlines():
        data = json.loads(line)
        content = "\n".join([i for i in data["texts"] if i])
        lang = predict_language(content)
        if lang != "zho_Hans":
            print(lang, normalize(content[:100]))
