"""Flex Message templates for IMIGO LINE Bot"""
from typing import Dict, Any


def create_welcome_flex_message(language: str = "en") -> Dict[str, Any]:
    """
    Create a welcome flex message with language selection buttons

    Args:
        language: Language code for the welcome message

    Returns:
        Flex message JSON structure
    """
    # Multi-language welcome texts
    welcome_texts = {
        "en": "Welcome to IMIGO!",
        "zh": "歡迎使用 IMIGO！",
        "id": "Selamat datang di IMIGO!",
        "vi": "Chào mừng đến với IMIGO!",
    }

    subtitle_texts = {
        "en": "Your AI assistant for migrant workers in Taiwan",
        "zh": "您在台灣的 AI 助手",
        "id": "Asisten AI Anda di Taiwan",
        "vi": "Trợ lý AI của bạn tại Đài Loan",
    }

    select_language_texts = {
        "en": "Please select your preferred language:",
        "zh": "請選擇您的語言：",
        "id": "Silakan pilih bahasa Anda:",
        "vi": "Vui lòng chọn ngôn ngữ của bạn:",
    }

    return {
        "type": "bubble",
        "hero": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "👋",
                    "size": "xxl",
                    "align": "center",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": welcome_texts.get(language, welcome_texts["en"]),
                    "weight": "bold",
                    "size": "xl",
                    "align": "center",
                    "color": "#1E90FF",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": subtitle_texts.get(language, subtitle_texts["en"]),
                    "size": "sm",
                    "align": "center",
                    "color": "#666666",
                    "margin": "sm",
                    "wrap": True
                }
            ],
            "backgroundColor": "#F0F8FF",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": select_language_texts.get(language, select_language_texts["en"]),
                    "weight": "bold",
                    "size": "md",
                    "margin": "md",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🇬🇧 English",
                                "text": "/lang en"
                            },
                            "style": "primary",
                            "color": "#1E90FF"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🇹🇼 繁體中文",
                                "text": "/lang zh"
                            },
                            "style": "primary",
                            "color": "#FF6347"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🇮🇩 Bahasa Indonesia",
                                "text": "/lang id"
                            },
                            "style": "primary",
                            "color": "#32CD32"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🇻🇳 Tiếng Việt",
                                "text": "/lang vi"
                            },
                            "style": "primary",
                            "color": "#FFD700"
                        }
                    ]
                }
            ]
        }
    }


def create_new_user_welcome_flex() -> Dict[str, Any]:
    """
    Create a multi-language welcome flex message for brand new users
    Shows welcome in all languages before they select one

    Returns:
        Flex message JSON structure
    """
    return {
        "type": "bubble",
        "hero": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "👋",
                    "size": "xxl",
                    "align": "center",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": "IMIGO",
                    "weight": "bold",
                    "size": "xxl",
                    "align": "center",
                    "color": "#1E90FF",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": "AI Assistant for Migrant Workers",
                    "size": "xs",
                    "align": "center",
                    "color": "#666666",
                    "margin": "sm"
                }
            ],
            "backgroundColor": "#F0F8FF",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🌐 Choose Your Language",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": "選擇您的語言",
                    "size": "sm",
                    "align": "center",
                    "color": "#666666"
                },
                {
                    "type": "text",
                    "text": "Pilih Bahasa Anda",
                    "size": "sm",
                    "align": "center",
                    "color": "#666666"
                },
                {
                    "type": "text",
                    "text": "Chọn Ngôn Ngữ",
                    "size": "sm",
                    "align": "center",
                    "color": "#666666",
                    "margin": "none"
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🇬🇧 English",
                                "text": "/lang en"
                            },
                            "style": "primary",
                            "color": "#1E90FF",
                            "height": "sm"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🇹🇼 繁體中文",
                                "text": "/lang zh"
                            },
                            "style": "primary",
                            "color": "#FF6347",
                            "height": "sm"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🇮🇩 Bahasa Indonesia",
                                "text": "/lang id"
                            },
                            "style": "primary",
                            "color": "#32CD32",
                            "height": "sm"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🇻🇳 Tiếng Việt",
                                "text": "/lang vi"
                            },
                            "style": "primary",
                            "color": "#FFD700",
                            "height": "sm"
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "We can help with work, health, translation, and more!",
                    "size": "xxs",
                    "color": "#888888",
                    "align": "center",
                    "wrap": True
                }
            ]
        }
    }


def create_help_flex_message(language: str = "en") -> Dict[str, Any]:
    """
    Create a help menu flex message with category buttons

    Args:
        language: Language code for help message

    Returns:
        Flex message JSON structure
    """
    help_titles = {
        "en": "How can I help you?",
        "zh": "我能幫您什麼？",
        "id": "Bagaimana saya bisa membantu?",
        "vi": "Tôi có thể giúp gì?",
    }

    categories = {
        "en": {
            "labor": "💼 Work Issues",
            "government": "🏛️ Government Services",
            "healthcare": "🏥 Healthcare",
            "translate": "🌐 Translation",
            "daily": "🏠 Daily Life",
            "emergency": "🚨 Emergency",
        },
        "zh": {
            "labor": "💼 工作問題",
            "government": "🏛️ 政府服務",
            "healthcare": "🏥 醫療保健",
            "translate": "🌐 翻譯",
            "daily": "🏠 日常生活",
            "emergency": "🚨 緊急聯絡",
        },
        "id": {
            "labor": "💼 Masalah Kerja",
            "government": "🏛️ Layanan Pemerintah",
            "healthcare": "🏥 Kesehatan",
            "translate": "🌐 Terjemahan",
            "daily": "🏠 Kehidupan Sehari-hari",
            "emergency": "🚨 Darurat",
        },
        "vi": {
            "labor": "💼 Vấn Đề Công Việc",
            "government": "🏛️ Dịch Vụ Chính Phủ",
            "healthcare": "🏥 Y Tế",
            "translate": "🌐 Dịch Thuật",
            "daily": "🏠 Cuộc Sống Hàng Ngày",
            "emergency": "🚨 Khẩn Cấp",
        }
    }

    lang_categories = categories.get(language, categories["en"])

    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": help_titles.get(language, help_titles["en"]),
                    "weight": "bold",
                    "size": "xl",
                    "color": "#FFFFFF"
                }
            ],
            "backgroundColor": "#1E90FF",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": lang_categories["labor"],
                        "data": "category_labor"
                    },
                    "style": "primary",
                    "color": "#1E90FF",
                    "margin": "md",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": lang_categories["government"],
                        "data": "category_government"
                    },
                    "style": "primary",
                    "color": "#FF6347",
                    "margin": "sm",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": lang_categories["healthcare"],
                        "data": "category_healthcare"
                    },
                    "style": "primary",
                    "color": "#32CD32",
                    "margin": "sm",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": lang_categories["translate"],
                        "data": "category_translate"
                    },
                    "style": "primary",
                    "color": "#FFD700",
                    "margin": "sm",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": lang_categories["daily"],
                        "data": "category_daily"
                    },
                    "style": "primary",
                    "color": "#9370DB",
                    "margin": "sm",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": lang_categories["emergency"],
                        "text": "/emergency"
                    },
                    "style": "primary",
                    "color": "#DC143C",
                    "margin": "sm",
                    "height": "sm"
                }
            ]
        }
    }


def create_emergency_flex_message(language: str = "en") -> Dict[str, Any]:
    """
    Create emergency contacts flex message

    Args:
        language: Language code for emergency message

    Returns:
        Flex message JSON structure
    """
    emergency_titles = {
        "en": "🚨 Emergency Contacts",
        "zh": "🚨 緊急聯絡電話",
        "id": "🚨 Kontak Darurat",
        "vi": "🚨 Liên Hệ Khẩn Cấp",
    }

    contact_labels = {
        "en": {
            "police": "Police",
            "fire": "Fire/Ambulance",
            "worker": "Worker Hotline",
            "indonesia": "Indonesia Office",
            "labor": "Labor Bureau",
            "trafficking": "Anti-Trafficking"
        },
        "zh": {
            "police": "警察",
            "fire": "消防/救護車",
            "worker": "外勞專線",
            "indonesia": "印尼代表處",
            "labor": "勞工局",
            "trafficking": "反人口販運"
        },
        "id": {
            "police": "Polisi",
            "fire": "Pemadam/Ambulans",
            "worker": "Hotline Pekerja",
            "indonesia": "Kantor Indonesia",
            "labor": "Dinas Tenaga Kerja",
            "trafficking": "Anti Perdagangan"
        },
        "vi": {
            "police": "Cảnh Sát",
            "fire": "Cứu Hỏa/Cấp Cứu",
            "worker": "Đường Dây Nóng",
            "indonesia": "Văn Phòng Indonesia",
            "labor": "Cục Lao Động",
            "trafficking": "Chống Buôn Người"
        }
    }

    labels = contact_labels.get(language, contact_labels["en"])

    def create_contact_box(label: str, number: str, urgent: bool = False) -> Dict[str, Any]:
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                    "weight": "bold" if urgent else "regular"
                },
                {
                    "type": "text",
                    "text": number,
                    "size": "sm",
                    "color": "#DC143C" if urgent else "#1E90FF",
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "margin": "md"
        }

    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": emergency_titles.get(language, emergency_titles["en"]),
                    "weight": "bold",
                    "size": "xl",
                    "color": "#FFFFFF"
                }
            ],
            "backgroundColor": "#DC143C",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                create_contact_box(labels["police"], "110", urgent=True),
                create_contact_box(labels["fire"], "119", urgent=True),
                {
                    "type": "separator",
                    "margin": "lg"
                },
                create_contact_box(labels["worker"], "1955"),
                create_contact_box(labels["indonesia"], "+886-2-2356-5156"),
                create_contact_box(labels["labor"], "1955"),
                create_contact_box(labels["trafficking"], "113"),
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "📞 Call Police (110)",
                        "uri": "tel:110"
                    },
                    "style": "primary",
                    "color": "#DC143C"
                }
            ]
        }
    }
