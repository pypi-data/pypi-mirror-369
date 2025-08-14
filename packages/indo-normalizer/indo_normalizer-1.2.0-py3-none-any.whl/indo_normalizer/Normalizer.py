import re
import pandas as pd
import os
import collections

# Mengimpor semua fungsi dari file functions.py (impor relatif)
from .functions import (
    tokenize_text,
    normalize_repetitions,
    is_abbreviation,
    normalize_leet,
    normalize_forced_leet,
    slang_to_formal,
    is_typo
)

class Normalizer:
    """
    Kelas untuk menormalisasi teks Bahasa Indonesia dan menghitung statistik terkait.
    Memuat korpus dari common_words.txt dan slangs.csv.
    """
    _COMMON_WORDS = set()
    _SLANG_TO_FORMAL_MAP = {}
    _COMMON_WORDS_SORTED = []

    def __init__(self):
        """
        Inisialisasi Normalizer dan memuat korpus yang diperlukan.
        File korpus diasumsikan berada di subfolder 'corpus/' di dalam package 'text_normalizer'.
        """
        # Dapatkan direktori dari file Normalizer.py ini
        base_dir = os.path.dirname(os.path.abspath(__file__))
        corpus_dir = os.path.join(base_dir, 'corpus')

        self.common_words_path = os.path.join(corpus_dir, 'common_words.txt')
        self.slangs_csv_path = os.path.join(corpus_dir, 'slangs.csv')

        # Load COMMON_WORDS
        try:
            with open(self.common_words_path, "r", encoding="utf-8") as f:
                # Read line by line to preserve order and handle each word
                # Also, strip whitespace and convert to lowercase for each word
                words = [line.strip().lower() for line in f if line.strip()]

                # Assign to the class-level sorted list (preserving order)
                Normalizer._COMMON_WORDS_SORTED = words 
                
                # Also assign to the set for faster O(1) lookups later
                Normalizer._COMMON_WORDS = set(words) 
                
            print(f"Korpus '{self.common_words_path}' berhasil dimuat. ({len(Normalizer._COMMON_WORDS_SORTED)} kata)")
        except FileNotFoundError:
            print(f"WARNING: '{self.common_words_path}' not found. Some normalization features may not work.")
            Normalizer._COMMON_WORDS = set()
            Normalizer._COMMON_WORDS_SORTED = [] # Ensure it's empty if file not found
        except Exception as e:
            print(f"WARNING: Error loading '{self.common_words_path}': {e}. Some normalization features may not work.")
            Normalizer._COMMON_WORDS = set()
            Normalizer._COMMON_WORDS_SORTED = [] # Ensure it's empty if error occurs

        # Load SLANG_TO_FORMAL_MAP
        if os.path.exists(self.slangs_csv_path):
            try:
                df_slang = pd.read_csv(self.slangs_csv_path)
                if 'slang' in df_slang.columns and 'formal' in df_slang.columns:
                    # Convert both slang and formal to lowercase for consistency
                    # This ensures your map keys and values are ready for matching
                    Normalizer._SLANG_TO_FORMAL_MAP = dict(zip(df_slang['slang'].str.lower(), df_slang['formal'].str.lower()))
                    print(f"Korpus '{self.slangs_csv_path}' berhasil dimuat. ({len(Normalizer._SLANG_TO_FORMAL_MAP)} pasangan)")
                else:
                    print(f"WARNING: '{self.slangs_csv_path}' must have 'slang' and 'formal' columns. Slang map empty.")
                    Normalizer._SLANG_TO_FORMAL_MAP = {} # Ensure it's empty if columns missing
            except Exception as e:
                print(f"WARNING: Error loading '{self.slangs_csv_path}': {e}. Slang map empty.")
                Normalizer._SLANG_TO_FORMAL_MAP = {} # Ensure it's empty on error
        else:
            print(f"WARNING: '{self.slangs_csv_path}' not found. Slang map empty.")
            Normalizer._SLANG_TO_FORMAL_MAP = {} # Ensure it's empty if file not found

    def text_to_words(self, s: str) -> list[str]:
        return re.findall(r"\w+|[^\w\s]", s, re.UNICODE)

    def normalize_text(self, s: str) -> tuple[str, dict]:
        """
        2) Normalisasi teks input 's' melalui serangkaian langkah:
           - Tokenisasi
           - Normalisasi pengulangan huruf
           - Normalisasi leet (korpus)
           - Normalisasi leet paksa
           - Cek singkatan (terhadap common_words)
           - Normalisasi slang
           - Koreksi typo (terhadap common_words)

        Mengembalikan teks yang dinormalisasi dan dictionary counts dari setiap operasi.
        """
        if not s:
            return "", collections.defaultdict(int)

        counts = collections.defaultdict(int)
        # Tokenisasi awal
        initial_tokens = tokenize_text(s)
        
        # --- Tahap 1: Normalisasi Pengulangan dan Leet ---
        # Kita akan kumpulkan hasil sementara dari tahap ini di sini
        temp_tokens_after_leet_stage = []

        for token in initial_tokens:
            original_token_for_leet = token # Simpan original_token khusus untuk tahap leet
            processed_token_for_leet_stage = token

            # Hanya proses token yang kemungkinan adalah kata (mengandung huruf atau angka)
            if re.search(r'[a-zA-Z0-9]', token, re.UNICODE):
                # 1. Panggil normalize_repetitions
                temp_rep_token = normalize_repetitions(processed_token_for_leet_stage)
                if temp_rep_token != processed_token_for_leet_stage:
                    counts['double_letters_words'] += 1
                processed_token_for_leet_stage = temp_rep_token

                # 2. Panggil normalize_leet (meneruskan common_words_set) dan normalize_forced_leet
                processed_token_after_soft_leet = normalize_leet(processed_token_for_leet_stage, self._COMMON_WORDS)
                
                # Default: anggap token tidak berubah dulu
                final_token_for_this_stage = processed_token_for_leet_stage

                # Jika normalize_leet berhasil mengubah token
                if processed_token_after_soft_leet != processed_token_for_leet_stage:
                    final_token_for_this_stage = processed_token_after_soft_leet
                    counts['known_leet_words'] += 1
                else:
                    # Jika normalize_leet TIDAK mengubah token, maka coba FORCED LEET
                    if re.search(r'[0-9!@$]', original_token_for_leet):
                        
                        # Asumsi normalize_forced_leet sekarang mengembalikan list[str]
                        # (Jika itu yang kamu inginkan untuk "bgt2" -> "bgt bgt")
                        temp_forced_leet_result_list = normalize_forced_leet(processed_token_for_leet_stage)
                        
                        # Jika forced leet berhasil mengubah token
                        # Kita cek elemen pertama atau apakah listnya lebih dari satu
                        if temp_forced_leet_result_list[0] != processed_token_for_leet_stage or len(temp_forced_leet_result_list) > 1:
                            # Jika ada perubahan atau pecah jadi banyak token
                            temp_tokens_after_leet_stage.extend(temp_forced_leet_result_list)
                            counts['random_leet_words'] += 1
                            # Lanjutkan ke token berikutnya di loop awal, karena ini sudah ditambahkan
                            continue 
                        else:
                            # Forced leet tidak mengubahnya, biarkan token aslinya dari tahap ini
                            final_token_for_this_stage = processed_token_for_leet_stage
                    else:
                        # Kondisi forced leet tidak terpenuhi, biarkan token aslinya dari tahap ini
                        final_token_for_this_stage = processed_token_for_leet_stage
                
                # Jika token diproses dan tidak di-extend oleh forced leet multi-token, tambahkan di sini
                temp_tokens_after_leet_stage.append(final_token_for_this_stage)
            else:
                # Jika token bukan kata (hanya tanda baca), tambahkan langsung
                temp_tokens_after_leet_stage.append(token)

        # --- Titik Krusial: Gabungkan dan Tokenisasi Ulang ---
        # Gabungkan token-token yang sudah dinormalisasi leet
        temp_joined_text = "".join(temp_tokens_after_leet_stage)

        # Tokenisasi ulang teks yang sudah bersih dari leet
        retokenized_tokens = tokenize_text(temp_joined_text)
        
        # --- Tahap 2: Normalisasi Singkatan, Slang, dan Typo ---
        final_normalized_tokens = []
        for token_after_leet in retokenized_tokens:
            processed_token = token_after_leet # Token baru untuk tahap ini

            # 3. Cek is_abbreviation (terhadap COMMON_WORDS)
            if processed_token.lower() not in self._COMMON_WORDS:
                # found_abbr_conversion = False # Tidak lagi dibutuhkan jika langsung break
                for common_word in self._COMMON_WORDS_SORTED:
                    if is_abbreviation(processed_token, common_word):
                        if processed_token.lower() != common_word.lower():
                            processed_token = common_word
                            counts['abbreviated_words'] += 1
                        break # Hentikan setelah menemukan kecocokan

            # 4. Panggil slang_to_formal (meneruskan slang_map)
            temp_token_slang = slang_to_formal(processed_token, self._SLANG_TO_FORMAL_MAP)
            if temp_token_slang != processed_token:
                counts['slangs'] += 1
            processed_token = temp_token_slang

            # 5. Panggil is_typo (terhadap COMMON_WORDS)
            if processed_token.lower() not in self._COMMON_WORDS:
                alpha_chars = sum(c.isalpha() for c in processed_token)
                if len(processed_token) // 2 < alpha_chars:
                    for common_word_target in self._COMMON_WORDS_SORTED:
                        if is_typo(processed_token.lower(), common_word_target):
                            processed_token = common_word_target
                            counts['typo_words'] += 1
                            break # Hentikan setelah menemukan kecocokan
            
            final_normalized_tokens.append(processed_token)

        # Gabungkan kembali token final menjadi string
        final_text = "".join(final_normalized_tokens)

        return final_text, dict(counts)

    def count_alays(self, s: str) -> int:
        """
        3) Menghitung total kemunculan normalisasi alay
           dalam teks 's'. Memanggil `normalize_text` secara internal.
        """
        _, counts = self.normalize_text(s) # Panggil metode dari instance kelas
        return counts.get('known_leet_words', 0) + counts.get('random_leet_words', 0)

    def count_slangs(self, s: str) -> int:
        """
        4) Menghitung total kemunculan normalisasi slang (slang_to_formal) dalam teks 's'.
           Memanggil `normalize_text` secara internal.
        """
        _, counts = self.normalize_text(s) # Panggil metode dari instance kelas
        return counts.get('slangs', 0)

if __name__ == "__main__":
    print("--- Menjalankan Demo Normalizer ---")
    
    # Inisialisasi Normalizer
    normalizer_instance = Normalizer()

    # Teks yang akan diuji
    text_to_test = "lagi gaje, btw mau kemana? nyebur?"

    # Lakukan normalisasi
    normalized_text, normalization_counts = normalizer_instance.normalize_text(text_to_test)

    # Dapatkan jumlah alay dan slang
    alay_count = normalizer_instance.count_alays(text_to_test)
    slang_count = normalizer_instance.count_slangs(text_to_test)

    print(f"\nOriginal Text: '{text_to_test}'")
    print(f"Normalized Text: '{normalized_text}'")
    print(f"Normalization Counts: {normalization_counts}")
    print(f"Total Alay Count: {alay_count}")
    print(f"Total Slang Count: {slang_count}")

    print("\n--- Demo Selesai ---")