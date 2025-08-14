import unittest
import os
from indo_normalizer import Normalizer

class TestIndoNormalizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Setup yang dijalankan sekali sebelum semua test method di kelas ini.
        Menginisialisasi Normalizer.
        Ini akan memuat korpus dari text_normalizer/corpus/ Anda yang sudah ada.
        """
        print("\n--- Inisialisasi Normalizer untuk Pengujian ---")
        cls.normalizer = Normalizer()
        print("Normalizer berhasil diinisialisasi. Memuat korpus dari text_normalizer/corpus/.")

    # Tidak perlu tearDownClass untuk membersihkan korpus atau functions.py
    # karena kita tidak lagi membuat dummy file tersebut di sini.

    def test_text_to_words_basic(self):
        """Uji tokenisasi dasar dengan kata dan tanda baca."""
        text = "Halo, apa kabar?"
        # Asumsi: tokenize_text memisahkan kata, tanda baca, dan tidak menyertakan spasi eksplisit.
        expected_tokens = ['Halo', ',', 'apa', 'kabar', '?']
        self.assertEqual(self.normalizer.text_to_words(text), expected_tokens)

    def test_text_to_words_empty_string(self):
        """Uji tokenisasi string kosong."""
        text = ""
        expected_tokens = []
        self.assertEqual(self.normalizer.text_to_words(text), expected_tokens)

    def test_text_to_words_only_punctuation(self):
        """Uji tokenisasi string hanya berisi tanda baca."""
        text = "!!!???"
        expected_tokens = ['!', '!', '!', '?', '?', '?']
        self.assertEqual(self.normalizer.text_to_words(text), expected_tokens)

    def test_normalize_text_repetitions(self):
        """Uji normalisasi pengulangan huruf berlebihan."""
        text = "tungguuuuuuuu pusinggg aku yaaaaa"
        # Sesuaikan 'expected_text' ini dengan perilaku functions.py Anda yang sebenarnya
        expected_text = "tunggu pusing aku ya"
        normalized_text, counts = self.normalizer.normalize_text(text)
        self.assertEqual(normalized_text, expected_text)
        self.assertGreaterEqual(counts.get('double_letters_words', 0), 3) # Ada 3 kata yang seharusnya dinormalisasi

    def test_normalize_text_leet(self):
        """Uji normalisasi leet speech berbasis korpus."""
        text = "aku k3ren pake h4lo"
        expected_text = "aku kEren pakai hAlo"
        normalized_text, counts = self.normalizer.normalize_text(text)
        self.assertEqual(normalized_text, expected_text)
        self.assertGreaterEqual(counts.get('known_leet_words', 0), 2)

    def test_normalize_text_forced_leet(self):
        """Uji normalisasi leet speech paksa (tanpa ada di korpus common_words)."""
        text = "nama z4k1 l4k5uuuuuy" # Asumsi 'zaki' tidak ada di common_words, jadi akan dipaksa normalisasi
        expected_text = "nama zAki maksud"
        normalized_text, counts = self.normalizer.normalize_text(text)
        self.assertEqual(normalized_text, expected_text)
        self.assertGreaterEqual(counts.get('known_leet_words', 0), 1)

    def test_normalize_text_abbreviations(self):
        """Uji normalisasi singkatan umum."""
        text = "yg penting kamu bgt lagi males"
        expected_text = "yang penting kamu banget lagi malas"
        normalized_text, counts = self.normalizer.normalize_text(text)
        self.assertEqual(normalized_text, expected_text)
        self.assertGreaterEqual(counts.get('abbreviated_words', 0), 2)

    def test_normalize_text_slang(self):
        """Uji normalisasi kata slang."""
        text = "dia sukanya ngikutin dan nyamain, padahal aku yang nemuin"
        # Perhatikan: 'bgt' akan dinormalisasi oleh abbr sebelum slangs
        expected_text = "dia sukanya mengikuti dan menyamakan, padahal aku yang menemukan"
        normalized_text, counts = self.normalizer.normalize_text(text)
        self.assertEqual(normalized_text, expected_text)
        self.assertGreaterEqual(counts.get('slangs', 0), 3) # ngikutin, nyamain, nemuin

    def test_normalize_text_typo(self):
        """Uji koreksi typo."""
        text = "saya kerjain tugas kompurer"
        expected_text = "saya kerjain tugas komputer"
        normalized_text, counts = self.normalizer.normalize_text(text)
        self.assertEqual(normalized_text, expected_text)
        self.assertGreaterEqual(counts.get('typo_words', 0), 1)

    def test_normalize_text_combined(self):
        """Uji kombinasi berbagai jenis normalisasi dalam satu kalimat."""
        text = "H4loooo, akU k3ren bgt! g4j3 kyknya btw ini masssaaa aku s4raninnn kamu n4nti JEMpyUt aku yaa. pusinggg bgt!"
        # Ini adalah output yang diharapkan berdasarkan fungsi dan korpus yang konsisten.
        # Anda mungkin perlu menyesuaikan ini jika logika fungsi Anda menghasilkan output yang sedikit berbeda.
        expected_text = "HAlo, akU kEren banget! enggak jelas kyknya btw ini masa aku sarankan kamu nAnti jemput aku yaa. pusing banget!"
        normalized_text, counts = self.normalizer.normalize_text(text)
        self.assertEqual(normalized_text, expected_text)
        
        # Periksa bahwa setiap jenis normalisasi terjadi setidaknya sejumlah ini
        self.assertGreaterEqual(counts.get('double_letters_words', 0), 4)
        self.assertGreaterEqual(counts.get('known_leet_words', 0), 5)
        self.assertGreaterEqual(counts.get('random_leet_words', 0), 0)
        self.assertGreaterEqual(counts.get('abbreviated_words', 0), 2)
        self.assertGreaterEqual(counts.get('slangs', 0), 0)
        self.assertGreaterEqual(counts.get('typo_words', 0), 1)

    def test_count_alays(self):
        """Uji fungsi count_alays."""
        text = "Aku 4L@y bgt, m3mang. Ini t3ks uji."
        alay_count = self.normalizer.count_alays(text)
        # Jumlah alay: 4L@y (leet), m3mang (forced), t3ks (forced)
        self.assertEqual(alay_count, 3)

    def test_count_slangs(self):
        """Uji fungsi count_slangs."""
        text = "lagi gaje, btw mau kemana? nyebur?"
        # Jumlah slang: gaje, btw, nyenengin
        slang_count = self.normalizer.count_slangs(text)
        self.assertEqual(slang_count, 2)

    def test_empty_string_inputs(self):
        """Uji semua fungsi dengan input string kosong."""
        self.assertEqual(self.normalizer.text_to_words(""), [])
        normalized_text, counts = self.normalizer.normalize_text("")
        self.assertEqual(normalized_text, "")
        self.assertEqual(dict(counts), {}) # Harus dict kosong
        self.assertEqual(self.normalizer.count_alays(""), 0)
        self.assertEqual(self.normalizer.count_slangs(""), 0)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)