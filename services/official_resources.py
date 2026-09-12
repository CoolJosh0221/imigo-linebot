"""Small, reviewed referral directory; this is not a live legal knowledge base."""

import re

REVIEWED_ON = "2026-09-12"
RESOURCES = (
    {
        "name": "Taiwan Ministry of Labor / Workforce Development Agency",
        "url": "https://fw.wda.gov.tw/wda-employer/home/activity/2c95efb39c4e83f8019c5096415c07e6",
        "fact": "1955 provides free, 24-hour support in Indonesian, Vietnamese, English, Thai and Chinese.",
        "keywords": (
            "salary",
            "wages",
            "employer",
            "overtime",
            "labor",
            "labour",
            "1955",
            "gaji",
            "majikan",
            "lembur",
            "lương",
            "chủ lao động",
            "sahod",
            "amo",
            "ค่าแรง",
            "นายจ้าง",
            "薪資",
            "薪水",
            "工資",
            "雇主",
            "仲介",
            "加班",
        ),
    },
    {
        "name": "Taiwan National Immigration Agency",
        "url": "https://www.immigration.gov.tw/5475/5478/6928/6940/204896/204917/cp_news",
        "fact": "1990 is the Foreigners in Taiwan Hotline for living-in-Taiwan inquiries.",
        "keywords": (
            "immigration",
            "visa",
            "arc",
            "residence",
            "1990",
            "imigrasi",
            "izin tinggal",
            "cư trú",
            "thị thực",
            "paninirahan",
            "ตรวจคนเข้าเมือง",
            "居留",
            "簽證",
            "移民",
        ),
    },
)


def reference_context(message: str) -> str:
    text = message.casefold()
    matches = []
    for resource in RESOURCES:
        for keyword in resource["keywords"]:
            # Word boundaries prevent matches such as ARC in "search".
            latin = all(ord(char) < 128 for char in keyword)
            matched = (
                re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", text)
                if latin
                else keyword in text
            )
            if matched:
                matches.append(
                    f"{resource['name']}: {resource['fact']} Source: {resource['url']}"
                )
                break
    if not matches:
        return ""
    return (
        f"\nOFFICIAL REFERRALS (reviewed {REVIEWED_ON}):\n"
        + "\n".join(matches)
        + "\nUse relevant referrals and include their source URL when mentioning these services. "
        "When naming official agencies or contact details, use only the relevant entries "
        "listed here. Do not add other agencies, offices or contact details. "
        "Keep the answer to four short sentences plus the required disclaimer and source. "
        "These entries do not establish legal eligibility, fees or deadlines. "
        "Do not invent current rules, claim to have checked a website live, "
        "or offer to search for details you cannot verify.\n"
    )
