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
                        "data": "category_labor",
                        "displayText": lang_categories["labor"]
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
                        "data": "category_government",
                        "displayText": lang_categories["government"]
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
                        "data": "category_healthcare",
                        "displayText": lang_categories["healthcare"]
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
                        "data": "category_translate",
                        "displayText": lang_categories["translate"]
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
                        "data": "category_daily",
                        "displayText": lang_categories["daily"]
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
            "indonesia": "Indonesia Office (KDEI)",
            "vietnam": "Vietnam Office (VECO)",
            "philippines": "Philippines Office (MECO)",
            "labor": "Labor Bureau",
            "trafficking": "Anti-Trafficking"
        },
        "zh": {
            "police": "警察",
            "fire": "消防/救護車",
            "worker": "外勞專線",
            "indonesia": "印尼代表處 (KDEI)",
            "vietnam": "越南代表處 (VECO)",
            "philippines": "菲律賓代表處 (MECO)",
            "labor": "勞工局",
            "trafficking": "反人口販運"
        },
        "id": {
            "police": "Polisi",
            "fire": "Pemadam/Ambulans",
            "worker": "Hotline Pekerja",
            "indonesia": "Kantor Indonesia (KDEI)",
            "vietnam": "Kantor Vietnam (VECO)",
            "philippines": "Kantor Filipina (MECO)",
            "labor": "Dinas Tenaga Kerja",
            "trafficking": "Anti Perdagangan"
        },
        "vi": {
            "police": "Cảnh Sát",
            "fire": "Cứu Hỏa/Cấp Cứu",
            "worker": "Đường Dây Nóng",
            "indonesia": "Văn Phòng Indonesia (KDEI)",
            "vietnam": "Văn Phòng Việt Nam (VECO)",
            "philippines": "Văn Phòng Philippines (MECO)",
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
                create_contact_box(labels["vietnam"], "+886-2-2516-6626"),
                create_contact_box(labels["philippines"], "+886-2-2508-1719"),
                {
                    "type": "separator",
                    "margin": "lg"
                },
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


def create_category_carousel(language: str = "en") -> Dict[str, Any]:
    """
    Create a carousel menu for service categories
    """
    categories = {
        "en": {
            "labor": {"title": "💼 Work Issues", "desc": "Labor rights, disputes, and regulations"},
            "government": {"title": "🏛️ Govt Services", "desc": "Permits, taxes, and legal docs"},
            "healthcare": {"title": "🏥 Healthcare", "desc": "Hospitals, insurance, and medical info"},
            "translate": {"title": "🌐 Translation", "desc": "Translate text or voice instantly"},
            "daily": {"title": "🏠 Daily Life", "desc": "Transport, housing, and living tips"},
            "emergency": {"title": "🚨 Emergency", "desc": "Police, ambulance, and hotlines"},
        },
        "zh": {
            "labor": {"title": "💼 工作問題", "desc": "勞工權益、糾紛與法規"},
            "government": {"title": "🏛️ 政府服務", "desc": "居留證、稅務與法律文件"},
            "healthcare": {"title": "🏥 醫療保健", "desc": "醫院、健保與醫療資訊"},
            "translate": {"title": "🌐 翻譯服務", "desc": "即時文字或語音翻譯"},
            "daily": {"title": "🏠 日常生活", "desc": "交通、住宿與生活小撇步"},
            "emergency": {"title": "🚨 緊急聯絡", "desc": "警察、救護車與求助專線"},
        },
        "id": {
            "labor": {"title": "💼 Masalah Kerja", "desc": "Hak pekerja, perselisihan, dan aturan"},
            "government": {"title": "🏛️ Layanan Govt", "desc": "Izin, pajak, dan dokumen hukum"},
            "healthcare": {"title": "🏥 Kesehatan", "desc": "RS, asuransi, dan info medis"},
            "translate": {"title": "🌐 Terjemahan", "desc": "Terjemahkan teks/suara instan"},
            "daily": {"title": "🏠 Sehari-hari", "desc": "Transportasi, hunian, dan tips"},
            "emergency": {"title": "🚨 Darurat", "desc": "Polisi, ambulans, dan hotline"},
        },
        "vi": {
            "labor": {"title": "💼 Công Việc", "desc": "Quyền lợi, tranh chấp, quy định"},
            "government": {"title": "🏛️ Chính Phủ", "desc": "Giấy tờ, thuế, pháp lý"},
            "healthcare": {"title": "🏥 Y Tế", "desc": "Bệnh viện, bảo hiểm, y khoa"},
            "translate": {"title": "🌐 Dịch Thuật", "desc": "Dịch văn bản hoặc giọng nói"},
            "daily": {"title": "🏠 Đời Sống", "desc": "Đi lại, nhà ở, mẹo vặt"},
            "emergency": {"title": "🚨 Khẩn Cấp", "desc": "Cảnh sát, cấp cứu, đường dây nóng"},
        }
    }

    texts = categories.get(language, categories["en"])

    bubbles = []
    
    # Order of keys to display
    keys = ["labor", "government", "healthcare", "translate", "daily", "emergency"]

    for key in keys:
        data = texts[key]
        # Define color based on original mapping (simplified here or reuse)
        colors = {
            "labor": "#1E90FF",
            "government": "#FF6347",
            "healthcare": "#32CD32",
            "translate": "#FFD700",
            "daily": "#9370DB",
            "emergency": "#DC143C"
        }
        color = colors.get(key, "#1E90FF")

        bubbles.append({
            "type": "bubble",
            "size": "micro",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": data["title"],
                        "weight": "bold",
                        "color": "#FFFFFF",
                        "size": "sm",
                        "wrap": True
                    }
                ],
                "backgroundColor": color,
                "paddingAll": "12px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": data["desc"],
                        "size": "xs",
                        "color": "#666666",
                        "wrap": True,
                        "maxLines": 3
                    }
                ],
                "paddingAll": "12px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback" if key != "emergency" else "message",
                            "label": "Select",
                            "data": f"category_{key}" if key != "emergency" else None,
                            "text": "/emergency" if key == "emergency" else None,
                            "displayText": data["title"] if key != "emergency" else None
                        },
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "paddingAll": "12px"
            }
        })

    return {
        "type": "carousel",
        "contents": bubbles
    }
