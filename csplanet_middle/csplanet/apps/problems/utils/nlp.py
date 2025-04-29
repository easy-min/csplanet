# csplanet/apps/problems/utils/nlp.py
from konlpy.tag import Okt

okt = Okt()

def tokenize_terms(text: str) -> set[str]:
    if not text:
        return set()
    tokens = set()
    for word, tag in okt.pos(text):
        # 명사, 동사, 형용사만 뽑아서 소문자로 정규화
        if tag in ('Noun', 'Verb', 'Adjective'):
            tokens.add(word.lower())
    return tokens
