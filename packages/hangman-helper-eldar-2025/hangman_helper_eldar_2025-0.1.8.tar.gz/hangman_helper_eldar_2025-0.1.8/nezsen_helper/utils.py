import random
import string

# Sözləri saxlayan nümunə siyahı
WORDS = ["python", "hangman", "programming", "developer", "challenge"]

def choose_word(word_list=WORDS):
    """
    Random şəkildə bir söz seçir.
    """
    return random.choice(word_list).lower()

def display_word(secret_word, guessed_letters):
    """
    Hərfləri gizlədir və yalnız düzgün tapılmış hərfləri göstərir.
    """
    return " ".join([letter if letter in guessed_letters else "_" for letter in secret_word])

def is_guess_correct(secret_word, guess):
    """
    İstifadəçi tərəfindən daxil edilmiş hərfin sözdə olub-olmadığını yoxlayır.
    """
    return guess in secret_word

def is_word_guessed(secret_word, guessed_letters):
    """
    Sözün tamamilə tapılıb-tapılmadığını yoxlayır.
    """
    return all(letter in guessed_letters for letter in secret_word)

def validate_guess(guess):
    """
    Düzgünlük yoxlaması: yalnız 1 hərf, hərf olmalıdır və böyük-kiçik fərqi yoxdur.
    """
    if len(guess) != 1:
        return False, "Yalnız bir hərf daxil edin."
    if guess.lower() not in string.ascii_lowercase:
        return False, "Yalnız ingilis hərflərindən istifadə edin."
    return True, ""
