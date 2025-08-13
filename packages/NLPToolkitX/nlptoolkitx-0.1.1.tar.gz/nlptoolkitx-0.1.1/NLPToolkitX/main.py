# Unified NLP preprocessing pipeline
# Python 3.7+ compatible

from tabulate import tabulate
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import warnings
import string
import re
import unicodedata
import os

try:
    from NLPToolkitX.utils_slang import load_builtin_slang
except Exception:
    load_builtin_slang = lambda: {}

DEFAULT_SLANG = load_builtin_slang()

try:
    import torch
    _HAS_TORCH = True
except Exception:
    _HAS_TORCH = False

def has_torch() -> bool:
    return _HAS_TORCH

try:
    import emoji as _emoji
    _HAS_EMOJI = True
except Exception:
    _HAS_EMOJI = False

try:
    import nltk
    from nltk.stem import WordNetLemmatizer, PorterStemmer
    from nltk.corpus import wordnet
    from nltk import pos_tag
    _HAS_NLTK = True
except Exception:
    _HAS_NLTK = False

if _HAS_NLTK:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        # try classic tagger; if missing, try the newer *_eng variant
        try:
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception:
            nltk.download('averaged_perceptron_tagger_eng', quiet=True)
    except Exception:
        pass

try:
    import contractions as _contractions_lib
    _HAS_CONTRACTIONS_LIB = True
except Exception:
    _HAS_CONTRACTIONS_LIB = False

# ===================== Basic cleaners (compatibility) =====================
def to_lowercase(text: str) -> str:
    # ASCII-only lowercasing (kept to preserve original behavior)
    result = []
    for ch in text:
        if 'A' <= ch <= 'Z':
            result.append(chr(ord(ch) + 32))
        else:
            result.append(ch)
    return "".join(result)

_HTML_RE = re.compile(r"<.*?>")
_URL_RE = re.compile(r"""(?i)\b((?:https?://|ftp://|www\.)[^\s<>\"]+)""", re.VERBOSE)
exclude = string.punctuation

def remove_html_tags(text: str) -> str:
    return _HTML_RE.sub("", text)

def remove_url(text: str) -> str:
    return _URL_RE.sub("", text)

def remove_punctuation(text: str) -> str:
    for ch in exclude:
        text = text.replace(ch, " ")
    return text

# ===================== Utility: generic key=value loader =====================
def _load_key_value_file(file_path: Optional[str]) -> Dict[str, str]:
    """Generic loader for key=value files (case-insensitive keys)."""
    if not file_path:
        return {}
    kv = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    kv[k.strip().lower()] = v.strip()
    except Exception:
        return {}
    return kv

# ===================== Slang / Acronyms =====================
def load_slang_dictionary(file_path: Optional[str]) -> Dict[str, str]:
    """
    Loads slang key=value lines. Keys are matched case-insensitively.
    If file_path is None or not found, returns empty dict.
    """
    slang_dict = {}
    if not file_path:
        return slang_dict
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    slang_dict[key.upper()] = value.strip()
    except Exception:
        return {}
    return slang_dict


def chat_conversion(text: str, chat_words: Optional[Dict[str, str]] = None) -> str:
    # If user did not pass a dict, use the built-in slang shipped with the package
    chat_words = DEFAULT_SLANG if chat_words is None else chat_words
    if not chat_words:
        return text
    new_words = []
    for w in text.split():
        up = w.upper()
        new_words.append(chat_words.get(up, w))
    return " ".join(new_words)


# ===================== Stopwords =====================
DEFAULT_STOPWORDS = set([
    'i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves',
    'he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs',
    'themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be',
    'been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or',
    'because','as','until','while','of','at','by','for','with','about','against','between','into','through',
    'during','before','after','above','below','to','from','up','down','in','out','on','off','over','under',
    'again','further','then','once','here','there','when','where','why','how','all','any','both','each','few',
    'more','most','other','some','such','nor','only','own','same','so','than','too','very','s','t','can','will',
    'just','should','now',"'d"
])

# Note: intentionally do NOT include negators ("no","not","never","n't").

def tokenize(text: str) -> List[str]:
    return text.split(" ")

def remove_stop_words(words: List[str], stop_words: Optional[set] = None) -> List[str]:
    sw = stop_words if stop_words is not None else DEFAULT_STOPWORDS
    return [w for w in words if w.lower() not in sw]

# ===================== Contractions: PyPI first, then file/dict, then built-in =====================
_BUILTIN_CONTRACTIONS = {
    "ain't":"am not","aren't":"are not","can't":"can not","can't've":"can not have",
    "could've":"could have","couldn't":"could not","didn't":"did not","doesn't":"does not",
    "don't":"do not","hadn't":"had not","hasn't":"has not","haven't":"have not",
    "he's":"he is","she's":"she is","it's":"it is","i'm":"i am","i'll":"i will","i've":"i have",
    "isn't":"is not","let's":"let us","mightn't":"might not","mustn't":"must not",
    "shan't":"shall not","she'll":"she will","shouldn't":"should not","that's":"that is",
    "there's":"there is","they're":"they are","they've":"they have","wasn't":"was not",
    "we're":"we are","weren't":"were not","what's":"what is","who's":"who is",
    "won't":"will not","wouldn't":"would not","y'all":"you all","you're":"you are",
    "you've":"you have","we've":"we have"
}

def _build_contractions_regex(mapping: Dict[str, str]) -> Optional[re.Pattern]:
    if not mapping:
        return None
    return re.compile("|".join(map(re.escape, mapping.keys())), flags=re.IGNORECASE)

# ===================== Unicode / whitespace / accents =====================
def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)

def strip_accents(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

# ===================== Emojis =====================
def remove_emojis(text: str) -> str:
    if _HAS_EMOJI:
        return _emoji.replace_emoji(text, replace="")
    return re.sub(r"[\U00010000-\U0010FFFF]", "", text)

def demojize_text(text: str) -> str:
    if _HAS_EMOJI:
        return _emoji.demojize(text, language="en")
    return text

# ===================== Mentions / Hashtags / Numbers =====================
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#\w+")
_NUM_RE = re.compile(r"\b\d+(\.\d+)?\b")

def remove_urls(text: str) -> str:
    return _URL_RE.sub("", text)

def replace_urls(text: str, token: str = "URL"):
    return _URL_RE.sub(token, text)

def remove_mentions(text: str) -> str:
    return _MENTION_RE.sub("", text)

def replace_mentions(text: str, token: str = "USER"):
    return _MENTION_RE.sub(token, text)

def remove_hashtags(text: str) -> str:
    return _HASHTAG_RE.sub("", text)

def split_hashtags_to_words(text: str) -> str:
    def _split(tag: str) -> str:
        core = tag.lstrip("#")
        parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", core)
        return " ".join(parts) if parts else core
    return re.sub(r"#\w+", lambda m: _split(m.group(0)), text)

def handle_numbers(text: str, mode: str = "keep"):
    if mode == "mask":
        return _NUM_RE.sub("NUM", text)
    return text

# ===================== Repeats / Tokenizer / Negation =====================
def normalize_repeats(text: str, max_repeats: int = 2) -> str:
    return re.sub(r"(.)\1{%d,}" % (max_repeats,), r"\1" * max_repeats, text)

_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?")

def smart_tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text)

_PUNCT_BREAK_RE = re.compile(r"[.!?,;:]")

def apply_negation_scope(tokens: List[str]) -> List[str]:
    """
    Adds _NEG to tokens after a negation trigger up to next punctuation or max_scope tokens.
    Triggers: no, not, never, n't
    """
    neg = False
    scope_count = 0
    max_scope = 3  # Limit negation tagging to 3 tokens max
    out = []
    for tok in tokens:
        low = tok.lower()
        if _PUNCT_BREAK_RE.match(tok):
            neg = False
            scope_count = 0
            out.append(tok)
            continue
        if low in ("no", "not", "never") or low.endswith("n't"):
            neg = True
            scope_count = 0
            out.append(low)
            continue
        if neg:
            out.append(tok + "_NEG")
            scope_count += 1
            if scope_count >= max_scope:
                neg = False
        else:
            out.append(tok)
    return out


# ===================== Lemmatization / Stemming =====================
def _map_pos(tag: str):
    if not _HAS_NLTK:
        return None
    if tag.startswith('J'):
        return wordnet.ADJ
    if tag.startswith('V'):
        return wordnet.VERB
    if tag.startswith('N'):
        return wordnet.NOUN
    if tag.startswith('R'):
        return wordnet.ADV
    return wordnet.NOUN

def lemmatize_tokens(tokens: List[str]) -> List[str]:
    if not _HAS_NLTK:
        return tokens
    try:
        tags = pos_tag(tokens)
        lemm = WordNetLemmatizer()
        return [lemm.lemmatize(t, _map_pos(p)) for t, p in tags]
    except Exception:
        return tokens

def stem_tokens(tokens: List[str]) -> List[str]:
    if not _HAS_NLTK:
        return tokens
    try:
        stemmer = PorterStemmer()
        return [stemmer.stem(t) for t in tokens]
    except Exception:
        return tokens

# ===================== N-grams =====================
def build_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    if n <= 1:
        return tokens
    return ["_".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

# ===================== Vectorization helpers =====================
def build_vocab(token_lists: List[List[str]], min_freq: int = 1, specials: Optional[List[str]] = None) -> Dict[str, int]:
    specials = specials or ["<PAD>", "<UNK>"]
    freq: Dict[str, int] = {}
    for toks in token_lists:
        for t in toks:
            freq[t] = freq.get(t, 0) + 1
    vocab: Dict[str, int] = {}
    idx = 0
    for sp in specials:
        if sp not in vocab:
            vocab[sp] = idx; idx += 1
    for t, c in sorted(freq.items(), key=lambda x: (-x[1], x[0])):
        if c >= min_freq and t not in vocab:
            vocab[t] = idx; idx += 1
    return vocab

def texts_to_sequences(token_lists: List[List[str]], vocab: Dict[str, int]) -> List[List[int]]:
    unk = vocab.get("<UNK>")
    return [[vocab.get(t, unk) for t in toks] for toks in token_lists]

def pad_sequences(seqs: List[List[int]], maxlen: Optional[int] = None, pad_value: int = 0, truncating: str = "post") -> np.ndarray:
    if maxlen is None:
        maxlen = max((len(s) for s in seqs), default=0)
    arr = np.full((len(seqs), maxlen), pad_value, dtype=np.int64)
    for i, s in enumerate(seqs):
        if not s:
            continue
        if len(s) <= maxlen:
            if truncating == "pre":
                arr[i, -len(s):] = s
            else:
                arr[i, :len(s)] = s
        else:
            arr[i, :] = s[-maxlen:] if truncating == "pre" else s[:maxlen]
    return arr

# ===================== Unified, configurable pipeline =====================
class PreprocessConfig:
    def __init__(
        self,
        lowercase: bool = True,
        strip_html: bool = True,
        urls: str = "mask",      # "keep" | "remove" | "mask"
        mentions: str = "mask",  # "keep" | "remove" | "mask"
        hashtags: str = "split", # "keep" | "remove" | "split"
        numbers: str = "keep",   # "keep" | "remove" | "mask"
        emojis: str = "remove",  # "keep" | "remove" | "demojize"
        contractions: bool = True,
        contractions_file: Optional[str] = None,          # your contractions.txt path
        contractions_dict: Optional[Dict[str, str]] = None,  # pass a dict directly
        accents: bool = True,
        repeats_to: int = 2,
        punctuation: str = "space",  # "keep" | "remove" | "space"
        tokenize: str = "smart",     # "simple" | "smart"
        stopwords: Optional[set] = None,
        negation_scope: bool = True,
        lemmatize: bool = True,
        stem: bool = False,          # usually use either lemma OR stem
        slang_dict: Optional[Dict[str, str]] = None,
    ):
        self.lowercase = lowercase
        self.strip_html = strip_html
        self.urls = urls
        self.mentions = mentions
        self.hashtags = hashtags
        self.numbers = numbers
        self.emojis = emojis
        self.contractions = contractions
        self.contractions_file = contractions_file
        self.contractions_dict = contractions_dict
        self.accents = accents
        self.repeats_to = repeats_to
        self.punctuation = punctuation
        self.tokenize = tokenize
        self.stopwords = stopwords
        self.negation_scope = negation_scope
        self.lemmatize = lemmatize
        self.stem = stem
        self.slang_dict = slang_dict

_PUNCT_TABLE = str.maketrans({c: " " for c in string.punctuation})
_PUNCT_REMOVE_TABLE = str.maketrans("", "", string.punctuation)


def _get_contractions_mapping_and_regex(cfg: 'PreprocessConfig'):
    # Priority: PyPI lib -> user dict -> file -> built-in
    if _HAS_CONTRACTIONS_LIB:
        return None, None   # signal to use library
    if cfg.contractions_dict:
        mapping = {k.lower(): v for k, v in cfg.contractions_dict.items()}
    elif cfg.contractions_file:
        mapping = _load_key_value_file(cfg.contractions_file)
    else:
        mapping = _BUILTIN_CONTRACTIONS
    regex = _build_contractions_regex(mapping)
    return mapping, regex


def expand_contractions(text: str, cfg: Optional['PreprocessConfig'] = None) -> str:
    """Use PyPI `contractions` if available; else use dict/regex fallback (dict from cfg or file, else built-in)."""
    if cfg is None:
        cfg = PreprocessConfig()
    if not cfg.contractions:
        return text
    if _HAS_CONTRACTIONS_LIB:
        try:
            return _contractions_lib.fix(text)
        except Exception:
            pass  # fall through
    mapping, regex = _get_contractions_mapping_and_regex(cfg)
    if not mapping or not regex:
        return text
    def _repl(m):
        key = m.group(0)
        return mapping.get(key.lower(), key)
    return regex.sub(_repl, text)


def process_text(text: str, cfg: Optional[PreprocessConfig] = None) -> List[str]:
    if cfg is None:
        cfg = PreprocessConfig()

    # 1) Base normalization
    text = normalize_unicode(text)
    if cfg.strip_html:
        text = _HTML_RE.sub("", text)
    if cfg.contractions:
        text = expand_contractions(text, cfg)

    # URLs / Mentions / Hashtags
    if cfg.urls == "remove":
        text = remove_urls(text)
    elif cfg.urls == "mask":
        text = replace_urls(text)
    if cfg.mentions == "remove":
        text = remove_mentions(text)
    elif cfg.mentions == "mask":
        text = replace_mentions(text)
    if cfg.hashtags == "remove":
        text = remove_hashtags(text)
    elif cfg.hashtags == "split":
        text = split_hashtags_to_words(text)

    # Numbers / Emojis
    text = handle_numbers(text, cfg.numbers)
    if cfg.emojis == "remove":
        text = remove_emojis(text)
    elif cfg.emojis == "demojize":
        text = demojize_text(text)

    # Lowercase, accents, repeats, slang
    if cfg.lowercase:
        text = text.lower()
    if cfg.accents:
        text = strip_accents(text)
    if cfg.repeats_to and cfg.repeats_to > 1:
        text = normalize_repeats(text, cfg.repeats_to)
    text = chat_conversion(text, cfg.slang_dict)

    # Punctuation
    if cfg.punctuation == "space":
        text = text.translate(_PUNCT_TABLE)
    elif cfg.punctuation == "remove":
        text = text.translate(_PUNCT_REMOVE_TABLE)
    text = normalize_whitespace(text)

    # Tokenize
    tokens = smart_tokenize(text) if cfg.tokenize == "smart" else text.split()

    # Stopwords
    tokens = remove_stop_words(tokens, cfg.stopwords)

    # Negation
    if cfg.negation_scope:
        tokens = apply_negation_scope(tokens)

    # Lemma / Stem
    if cfg.lemmatize:
        tokens = lemmatize_tokens(tokens)
    elif cfg.stem:
        tokens = stem_tokens(tokens)

    return [t for t in tokens if t]


def process_dataframe(df: pd.DataFrame, text_col: str = "text", cfg: Optional[PreprocessConfig] = None) -> List[List[str]]:
    if cfg is None:
        cfg = PreprocessConfig()
    processed = []
    for t in df[text_col].astype(str).tolist():
        processed.append(process_text(t, cfg))
    return processed

# ===================== Vocabulary / Encoders (unified) =====================

def vocabulary_words(input_data):
    """
    Backward-compatible: if DataFrame, assumes text column 'text' and uses process_text().
    If str, returns processed tokens. If list (tokens or lists of tokens), returns as-is.
    """
    if isinstance(input_data, pd.DataFrame):
        cfg = PreprocessConfig()
        return process_dataframe(input_data, text_col="text", cfg=cfg)
    elif isinstance(input_data, str):
        cfg = PreprocessConfig()
        return process_text(input_data, cfg=cfg)
    elif isinstance(input_data, list):
        return input_data
    else:
        raise TypeError("Input must be a pandas DataFrame, a string, or a list of tokens.")


def label_encode(data, column_name: Optional[str] = None):
    """
    Returns mapping {label: int} and prints a pretty table.
    Accepts: list, list of lists, or DataFrame + column_name
    """
    if isinstance(data, list):
        if any(isinstance(i, list) for i in data):
            flattened = [it for sub in data for it in sub]
        else:
            flattened = data
        unique = sorted(set(flattened))
    elif isinstance(data, pd.DataFrame):
        if column_name is None:
            raise ValueError("Provide column_name for DataFrame inputs.")
        unique = sorted(set(data[column_name].tolist()))
    else:
        raise TypeError("data must be list or DataFrame")

    label_to_int = {lbl: i + 1 for i, lbl in enumerate(unique)}  # 1-based like original

    # Pretty table (pure Python; no torch required)
    table = [[" "] + unique]
    for lbl in unique:
        row = [lbl] + [label_to_int[lbl] if lbl == col else 0 for col in unique]
        table.append(row)
    print(tabulate(table, headers="firstrow", tablefmt="grid"))
    return label_to_int




def one_hot_encode(data, column_name: Optional[str] = None):
    """
    Returns (one_hot_matrix, labels_list) and prints a pretty table.
    If PyTorch is installed, uses torch.Tensor; otherwise falls back to numpy.ndarray with a warning.
    """
    if isinstance(data, list):
        if any(isinstance(i, list) for i in data):
            flattened = [it for sub in data for it in sub]
        else:
            flattened = data
        unique = sorted(set(flattened))
    elif isinstance(data, pd.DataFrame):
        if column_name is None:
            raise ValueError("Provide column_name for DataFrame inputs.")
        unique = sorted(set(data[column_name].tolist()))
    else:
        raise TypeError("data must be list or DataFrame")

    if _HAS_TORCH:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        I = torch.eye(len(unique), dtype=torch.int32, device=device)
        rows_for_table = [I[i].cpu().numpy().tolist() for i in range(len(unique))]
    else:
        warnings.warn(
            "⚠️ Torch not found — falling back to NumPy. "
            "For faster performance, install with: pip install NLPToolkitX[torch]",
            UserWarning
        )
        I = np.eye(len(unique), dtype=np.int32)
        rows_for_table = [I[i].tolist() for i in range(len(unique))]

    # Pretty table
    table = [[" "] + unique]
    for i, lbl in enumerate(unique):
        row = [lbl] + rows_for_table[i]
        table.append(row)
    print(tabulate(table, headers="firstrow", tablefmt="grid"))
    return I, unique


# ===================== Diagnostics & Validation =====================

def contractions_source(cfg: Optional[PreprocessConfig] = None) -> str:
    """Report which contractions source will be used: 'pypi', 'dict', 'file', or 'builtin' (or 'disabled')."""
    if cfg is None:
        cfg = PreprocessConfig()
    if not cfg.contractions:
        return "disabled"
    if _HAS_CONTRACTIONS_LIB:
        return "pypi"
    if cfg.contractions_dict:
        return "dict"
    if cfg.contractions_file and _load_key_value_file(cfg.contractions_file):
        return "file"
    return "builtin"


def validate_config(cfg: Optional[PreprocessConfig] = None) -> Dict[str, str]:
    """Light sanity checks and a short summary of key toggles."""
    if cfg is None:
        cfg = PreprocessConfig()
    issues = []

    if cfg.lemmatize and cfg.stem:
        issues.append("Both lemmatize and stem are True; consider enabling only one.")

    if cfg.tokenize not in ("smart", "simple"):
        issues.append("tokenize must be 'smart' or 'simple'.")

    if cfg.urls not in ("keep", "remove", "mask"):
        issues.append("urls must be one of: keep/remove/mask.")
    if cfg.mentions not in ("keep", "remove", "mask"):
        issues.append("mentions must be one of: keep/remove/mask.")
    if cfg.hashtags not in ("keep", "remove", "split"):
        issues.append("hashtags must be one of: keep/remove/split.")
    if cfg.numbers not in ("keep", "remove", "mask"):
        issues.append("numbers must be one of: keep/remove/mask.")
    if cfg.emojis not in ("keep", "remove", "demojize"):
        issues.append("emojis must be one of: keep/remove/demojize.")
    if cfg.punctuation not in ("keep", "remove", "space"):
        issues.append("punctuation must be one of: keep/remove/space.")

    summary = {
        "contractions_source": contractions_source(cfg),
        "tokenize": cfg.tokenize,
        "negation_scope": str(cfg.negation_scope),
        "lemmatize": str(cfg.lemmatize),
        "stem": str(cfg.stem),
        "urls": cfg.urls,
        "mentions": cfg.mentions,
        "hashtags": cfg.hashtags,
        "numbers": cfg.numbers,
        "emojis": cfg.emojis,
        "punctuation": cfg.punctuation,
    }
    return {"issues": "; ".join(issues) if issues else "none", **summary}


