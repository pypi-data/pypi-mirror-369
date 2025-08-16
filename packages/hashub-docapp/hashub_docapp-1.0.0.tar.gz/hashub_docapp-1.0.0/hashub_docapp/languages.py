"""
Language Helper for Hashub DocApp SDK

OCR dil kodları ve ISO 639-1 standart kodları arasında dönüşüm sağlar.
lang_dic_code_first.json dosyasından otomatik olarak oluşturulmuştur.
"""

from typing import Dict, List, Optional, Tuple


class LanguageHelper:
    """
    OCR language codes and ISO 639-1 conversion helper.
    
    Allows users to work with standard ISO codes instead of 
    internal API language codes.
    """
    
    # API language codes to language info mapping
    LANGUAGES = {
        "lang_afr_af": {"native": "Afrikaans", "english": "Afrikaans", "iso": "af"},
        "lang_amh_am": {"native": "አማርኛ", "english": "Amharic", "iso": "am"},
        "lang_ara_ar": {"native": "العربية", "english": "Arabic", "iso": "ar"},
        "lang_hye_hy": {"native": "հայերեն", "english": "Armenian", "iso": "hy"},
        "lang_aze_az": {"native": "Azərbaycanca", "english": "Azerbaijani", "iso": "az"},
        "lang_eus_eu": {"native": "Euskara", "english": "Basque", "iso": "eu"},
        "lang_ben_bn": {"native": "বাংলা", "english": "Bengali", "iso": "bn"},
        "lang_bel_be": {"native": "беларуская", "english": "Belarusian", "iso": "be"},
        "lang_bos_bs": {"native": "Bosanski", "english": "Bosnian", "iso": "bs"},
        "lang_bul_bg": {"native": "български", "english": "Bulgarian", "iso": "bg"},
        "lang_cat_es": {"native": "Català", "english": "Catalan", "iso": "es"},
        "lang_ces_cs": {"native": "čeština", "english": "Czech", "iso": "cs"},
        "lang_chi_sim_zh": {"native": "中文 (简体)", "english": "Chinese (Simplified)", "iso": "zh"},
        "lang_chi_tra_zh": {"native": "中文 (繁體)", "english": "Chinese (Traditional)", "iso": "zh"},
        "lang_cos_co": {"native": "Corsu", "english": "Corsican", "iso": "co"},
        "lang_hrv_hr": {"native": "Hrvatski", "english": "Croatian", "iso": "hr"},
        "lang_dan_da": {"native": "Dansk", "english": "Danish", "iso": "da"},
        "lang_nld_nl": {"native": "Nederlands", "english": "Dutch", "iso": "nl"},
        "lang_eng_en": {"native": "English", "english": "English", "iso": "en"},
        "lang_epo_eo": {"native": "Esperanto", "english": "Esperanto", "iso": "eo"},
        "lang_est_et": {"native": "Eesti", "english": "Estonian", "iso": "et"},
        "lang_fin_fi": {"native": "Suomi", "english": "Finnish", "iso": "fi"},
        "lang_fra_fr": {"native": "Français", "english": "French", "iso": "fr"},
        "lang_glg_gl": {"native": "Galego", "english": "Galician", "iso": "gl"},
        "lang_kat_ka": {"native": "ქართული", "english": "Georgian", "iso": "ka"},
        "lang_deu_de": {"native": "Deutsch", "english": "German", "iso": "de"},
        "lang_ell_el": {"native": "Ελληνικά", "english": "Greek", "iso": "el"},
        "lang_guj_gu": {"native": "ગુજરાતી", "english": "Gujarati", "iso": "gu"},
        "lang_hat_ht": {"native": "Kreyòl ayisyen", "english": "Haitian (Creole)", "iso": "ht"},
        "lang_heb_he": {"native": "עִברִית", "english": "Hebrew", "iso": "he"},
        "lang_hin_hi": {"native": "हिन्दी", "english": "Hindi", "iso": "hi"},
        "lang_hun_hu": {"native": "Magyar", "english": "Hungarian", "iso": "hu"},
        "lang_isl_is": {"native": "Íslenska", "english": "Icelandic", "iso": "is"},
        "lang_ind_id": {"native": "Bahasa Indonesia", "english": "Indonesian", "iso": "id"},
        "lang_gle_ga": {"native": "Gaeilge", "english": "Irish", "iso": "ga"},
        "lang_ita_it": {"native": "Italiano", "english": "Italian", "iso": "it"},
        "lang_jpn_ja": {"native": "日本語", "english": "Japanese", "iso": "ja"},
        "lang_khm_km": {"native": "ភាសាខ្មែរ", "english": "Khmer", "iso": "km"},
        "lang_kor_ko": {"native": "한국어", "english": "Korean", "iso": "ko"},
        "lang_kmr_ku": {"native": "Kurdî", "english": "Kurdish", "iso": "ku"},
        "lang_lao_lo": {"native": "ລາວ", "english": "Lao", "iso": "lo"},
        "lang_lat_la": {"native": "Latina", "english": "Latin", "iso": "la"},
        "lang_lav_lv": {"native": "Latviešu", "english": "Latvian", "iso": "lv"},
        "lang_lit_lt": {"native": "Lietuvių", "english": "Lithuanian", "iso": "lt"},
        "lang_mkd_mk": {"native": "македонски", "english": "Macedonian", "iso": "mk"},
        "lang_mal_ml": {"native": "മലയാളം", "english": "Malayalam", "iso": "ml"},
        "lang_mlt_mt": {"native": "Malti", "english": "Maltese", "iso": "mt"},
        "lang_nor_no": {"native": "Norsk", "english": "Norwegian", "iso": "no"},
        "lang_ori_or": {"native": "ଓଡ଼ିଆ", "english": "Oriya", "iso": "or"},
        "lang_pus_ps": {"native": "پښتو", "english": "Pashto", "iso": "ps"},
        "lang_fas_fa": {"native": "فارسی", "english": "Persian", "iso": "fa"},
        "lang_pol_pl": {"native": "Polski", "english": "Polish", "iso": "pl"},
        "lang_por_pt": {"native": "Português", "english": "Portuguese", "iso": "pt"},
        "lang_pan_pa": {"native": "ਪੰਜਾਬੀ", "english": "Punjabi", "iso": "pa"},
        "lang_ron_ro": {"native": "Română", "english": "Romanian", "iso": "ro"},
        "lang_rus_ru": {"native": "Русский", "english": "Russian", "iso": "ru"},
        "lang_san_sa": {"native": "संस्कृतम्", "english": "Sanskrit", "iso": "sa"},
        "lang_srp_sr": {"native": "српски", "english": "Serbian", "iso": "sr"},
        "lang_slk_sk": {"native": "Slovenčina", "english": "Slovak", "iso": "sk"},
        "lang_slv_sl": {"native": "Slovenščina", "english": "Slovenian", "iso": "sl"},
        "lang_spa_es": {"native": "Español", "english": "Spanish", "iso": "es"},
        "lang_swa_sw": {"native": "Kiswahili", "english": "Swahili", "iso": "sw"},
        "lang_swe_sv": {"native": "Svenska", "english": "Swedish", "iso": "sv"},
        "lang_syr_ar": {"native": "ܣܘܪܝܝܐ", "english": "Syriac", "iso": "ar"},
        "lang_tam_ta": {"native": "தமிழ்", "english": "Tamil", "iso": "ta"},
        "lang_tat_tt": {"native": "татар теле", "english": "Tatar", "iso": "tt"},
        "lang_tel_te": {"native": "తెలుగు", "english": "Telugu", "iso": "te"},
        "lang_tha_th": {"native": "ไทย", "english": "Thai", "iso": "th"},
        "lang_bod_bo": {"native": "བོད་སྐད", "english": "Tibetan", "iso": "bo"},
        "lang_tur_tr": {"native": "Türkçe", "english": "Turkish", "iso": "tr"},
        "lang_ukr_uk": {"native": "українська", "english": "Ukrainian", "iso": "uk"},
        "lang_urd_ur": {"native": "اردو", "english": "Urdu", "iso": "ur"},
        "lang_uzb_uz": {"native": "Oʻzbekcha", "english": "Uzbek", "iso": "uz"},
        "lang_vie_vi": {"native": "Tiếng Việt", "english": "Vietnamese", "iso": "vi"},
        "lang_cym_cy": {"native": "Cymraeg", "english": "Welsh", "iso": "cy"},
        "lang_yid_yi": {"native": "ייִדיש", "english": "Yiddish", "iso": "yi"}
    }
    
    # Build reverse mapping (ISO -> API code)
    _ISO_TO_API = {}
    for api_code, info in LANGUAGES.items():
        iso = info["iso"]
        if iso not in _ISO_TO_API:
            _ISO_TO_API[iso] = []
        _ISO_TO_API[iso].append(api_code)
    
    @classmethod
    def iso_to_api_code(cls, iso_code: str) -> str:
        """
        Convert ISO 639-1 code to API language code.
        
        Args:
            iso_code: ISO 639-1 language code (e.g., 'en', 'tr', 'zh')
            
        Returns:
            API language code (e.g., 'lang_eng_en', 'lang_tur_tr')
            
        Raises:
            ValueError: If ISO code is not supported
            
        Examples:
            >>> LanguageHelper.iso_to_api_code('en')
            'lang_eng_en'
            >>> LanguageHelper.iso_to_api_code('tr')
            'lang_tur_tr'
            >>> LanguageHelper.iso_to_api_code('zh')
            'lang_chi_sim_zh'  # Returns simplified Chinese by default
        """
        iso_lower = iso_code.lower()
        
        if iso_lower not in cls._ISO_TO_API:
            raise ValueError(f"Unsupported ISO language code: {iso_code}")
        
        # Return first match (for languages with multiple variants like Chinese)
        return cls._ISO_TO_API[iso_lower][0]
    
    @classmethod
    def api_code_to_iso(cls, api_code: str) -> str:
        """
        Convert API language code to ISO 639-1 code.
        
        Args:
            api_code: API language code (e.g., 'lang_eng_en')
            
        Returns:
            ISO 639-1 language code (e.g., 'en')
            
        Raises:
            ValueError: If API code is not found
        """
        if api_code not in cls.LANGUAGES:
            raise ValueError(f"Unknown API language code: {api_code}")
        
        return cls.LANGUAGES[api_code]["iso"]
    
    @classmethod
    def get_language_info(cls, code: str) -> Dict[str, str]:
        """
        Get language information by API code or ISO code.
        
        Args:
            code: Either API code (lang_xxx_xx) or ISO code (xx)
            
        Returns:
            Dictionary with native, english, iso, and api_code
            
        Examples:
            >>> LanguageHelper.get_language_info('tr')
            {'native': 'Türkçe', 'english': 'Turkish', 'iso': 'tr', 'api_code': 'lang_tur_tr'}
        """
        if code.startswith('lang_'):
            # API code
            if code not in cls.LANGUAGES:
                raise ValueError(f"Unknown API language code: {code}")
            info = cls.LANGUAGES[code]
            return {
                'native': info['native'],
                'english': info['english'],
                'iso': info['iso'],
                'api_code': code
            }
        else:
            # ISO code
            api_code = cls.iso_to_api_code(code)
            info = cls.LANGUAGES[api_code]
            return {
                'native': info['native'],
                'english': info['english'],
                'iso': info['iso'],
                'api_code': api_code
            }
    
    @classmethod
    def list_languages(cls, filter_iso: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        List all supported languages or filter by ISO codes.
        
        Args:
            filter_iso: Optional list of ISO codes to filter by
            
        Returns:
            List of language dictionaries
        """
        languages = []
        
        for api_code, info in cls.LANGUAGES.items():
            if filter_iso and info['iso'] not in filter_iso:
                continue
                
            languages.append({
                'api_code': api_code,
                'iso': info['iso'],
                'english': info['english'],
                'native': info['native']
            })
        
        return sorted(languages, key=lambda x: x['english'])
    
    @classmethod
    def get_popular_languages(cls) -> List[Dict[str, str]]:
        """
        Get most commonly used languages for OCR.
        
        Returns:
            List of popular language dictionaries
        """
        popular_iso = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko',
            'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi'
        ]
        return cls.list_languages(filter_iso=popular_iso)
    
    @classmethod
    def search_languages(cls, query: str) -> List[Dict[str, str]]:
        """
        Search languages by name or ISO code.
        
        Args:
            query: Search query (case insensitive)
            
        Returns:
            List of matching language dictionaries
        """
        query_lower = query.lower()
        results = []
        
        for api_code, info in cls.LANGUAGES.items():
            if (query_lower in info['english'].lower() or 
                query_lower in info['native'].lower() or
                query_lower == info['iso'].lower()):
                results.append({
                    'api_code': api_code,
                    'iso': info['iso'],
                    'english': info['english'],
                    'native': info['native']
                })
        
        return sorted(results, key=lambda x: x['english'])
    
    @classmethod
    def get_language_variants(cls, iso_code: str) -> List[str]:
        """
        Get all API code variants for an ISO code.
        
        Some languages like Chinese have multiple variants (simplified/traditional).
        
        Args:
            iso_code: ISO 639-1 code
            
        Returns:
            List of API codes for the language
        """
        iso_lower = iso_code.lower()
        return cls._ISO_TO_API.get(iso_lower, [])


def get_language_code(iso_or_api: str) -> str:
    """
    Convenience function to get API language code from ISO or API code.
    
    Args:
        iso_or_api: ISO code ('en') or API code ('lang_eng_en')
        
    Returns:
        API language code
        
    Examples:
        >>> get_language_code('en')
        'lang_eng_en'
        >>> get_language_code('lang_eng_en')
        'lang_eng_en'
    """
    if iso_or_api.startswith('lang_'):
        return iso_or_api
    else:
        return LanguageHelper.iso_to_api_code(iso_or_api)


def get_language_display_name(iso_or_api: str, prefer_native: bool = False) -> str:
    """
    Get display name for a language.
    
    Args:
        iso_or_api: ISO code or API code
        prefer_native: Use native name instead of English name
        
    Returns:
        Language display name
        
    Examples:
        >>> get_language_display_name('tr')
        'Turkish'
        >>> get_language_display_name('tr', prefer_native=True)
        'Türkçe'
    """
    info = LanguageHelper.get_language_info(iso_or_api)
    return info['native'] if prefer_native else info['english']
