import re
import uniseg.wordbreak

DIGIT_RE = re.compile(r"\d")
PUNCT_OR_NON_PRINTING_CHARS = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f«´·»–—‘’‛“”„‟…‧∶━►、。〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿﹏！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～｟｠｢｣､"
PUNCT_OR_NON_PRINTING_CHARS_RE = re.compile(f"[{''.join(PUNCT_OR_NON_PRINTING_CHARS)}]")


def find_word_positions(s):
    word_char_groups = re.finditer(r"\w+", s, re.UNICODE)
    word_breaks = list(uniseg.wordbreak.word_breakables(s))
    # returns a list with the same length as s that contains every word breaking
    # opportunity, 0 for no break, 1 for break

    positions = []

    for match in word_char_groups:
        start = match.start()
        end = match.end()

        # Use uniseg's word_breakables to find word boundaries within Unicode word character groups
        current_position = start
        for i in range(start, end):
            # Check if a break is possible at this position
            if word_breaks[i] == 1:
                # If a break is possible, add the word from current_position to i
                if current_position != i:
                    positions.append(s[current_position:i])
                current_position = i

        # Append the last word segment if any
        if current_position != end:
            positions.append(s[current_position:end])

    return positions


def hash_tokenizer(text: str) -> str:
    text = text.strip()
    text = text.lower()
    # raw_words = uniseg.wordbreak.words(text)
    raw_words = find_word_positions(text)
    clean_words = []
    for word in raw_words:
        word = DIGIT_RE.sub("", word)
        word = PUNCT_OR_NON_PRINTING_CHARS_RE.sub("", word)
        word = word.strip()
        if word:
            clean_words.append(word)
    return clean_words


if __name__ == "__main__":
    text = """皆さん、我在インターネット上看到someone把几国language混在一起speak。

    我看到之后be like：それは我じゃないか！私もtry一tryです。

    虽然是混乱している句子ですけど、中文日本語プラスEnglish、挑戦スタート！

    我study日本語的时候，もし有汉字，我会很happy。

    Bueause中国人として、when I see汉字，すぐに那个汉字がわかります。

    But 我hate外来語、什么マクドナルド、スターバックス、グーグル、ディズニーランド、根本记不住カタカナhow to写、太難しい。

    以上です，byebye！

    Here's the website:https://simple.wikipedia.org/wiki/42_(answer)"""

    print(hash_tokenizer(text))
