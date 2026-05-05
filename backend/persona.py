"""
persona.py – Extracts user persona from conversation messages.
Only includes traits supported by multiple messages.
"""

import re
from typing import List, Dict
from collections import Counter

HABIT_PATTERNS = [
    (r"\b(sleep|slept|sleeping|nap|insomnia|bedtime|wake up|woke up|alarm)\b", "sleep"),
    (r"\b(stay up late|up late|late night|all[- ]?nighter|can't sleep)\b", "sleep"),
    (r"\b(breakfast|lunch|dinner|snack|eat|eating|ate|cook|cooking|meal|food)\b", "food"),
    (r"\b(coffee|tea|chai|drink|drinking|water|juice)\b", "food"),
    (r"\b(gym|workout|exercise|run|running|jog|yoga|walk|fitness)\b", "exercise"),
    (r"\b(study|studying|studied|homework|assignment|revision|exam prep)\b", "study"),
    (r"\b(work|working|office|meeting|deadline|project)\b", "work"),
    (r"\b(scroll|scrolling|instagram|youtube|netflix|binge|gaming|game)\b", "screen_time"),
    (r"\b(every day|everyday|always|usually|normally|routine|habit|daily)\b", "routine_marker"),
]

PERSONAL_FACT_PATTERNS = [
    (r"\b(my mom|my dad|my brother|my sister|my friend|my bf|my gf|my girlfriend|my boyfriend)\b", "relationship"),
    (r"\b(my family|my parents|my wife|my husband|my partner)\b", "relationship"),
    (r"\b(my exam|my test|my interview|my birthday|my graduation)\b", "event"),
    (r"\b(i live in|i'm from|i am from|my college|my school|my university)\b", "location"),
    (r"\b(i love|i hate|i like|i prefer|my favorite|my fav|i enjoy)\b", "preference"),
]

PERSONALITY_MARKERS = {
    "humor": [r"\b(lol|lmao|haha|hehe|rofl|funny|joke|kidding|jk)\b"],
    "seriousness": [r"\b(seriously|important|critical|urgent|focus|worried|concern)\b"],
    "emotional": [r"\b(feel|feeling|sad|happy|angry|upset|frustrated|anxious|stressed)\b"],
    "supportive": [r"\b(don't worry|it's okay|you got this|proud of you|believe in you)\b"],
    "analytical": [r"\b(because|therefore|however|in my opinion|I think|logically)\b"],
}


def _analyze_habits(messages: List[Dict]) -> List[str]:
    category_counts: Dict[str, int] = Counter()
    for msg in messages:
        content = msg["content"].lower()
        for pattern, category in HABIT_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                category_counts[category] += 1

    habits = []
    label_map = {
        "sleep": "Mentions sleep-related topics frequently",
        "food": "Regularly discusses food, meals, or drinks",
        "exercise": "Shows interest in fitness or exercise",
        "study": "Frequently mentions studying or academic work",
        "work": "Often discusses work-related activities",
        "screen_time": "Engages with social media, streaming, or gaming",
        "routine_marker": "References daily routines or habitual activities",
    }
    for cat, label in label_map.items():
        if category_counts.get(cat, 0) >= 2:
            habits.append(label)
    return habits


def _analyze_personal_facts(messages: List[Dict]) -> List[str]:
    facts_found: Dict[str, set] = {}
    for msg in messages:
        content = msg["content"]
        for pattern, category in PERSONAL_FACT_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if category not in facts_found:
                    facts_found[category] = set()
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 50)
                facts_found[category].add(content[start:end].strip())

    facts = []
    for category, snippets in facts_found.items():
        for snippet in list(snippets)[:3]:
            facts.append(f'[{category}] "{snippet}"')
    return facts


def _analyze_personality(messages: List[Dict]) -> List[str]:
    trait_counts: Dict[str, int] = Counter()
    total = len(messages)
    for msg in messages:
        content = msg["content"].lower()
        for trait, patterns in PERSONALITY_MARKERS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    trait_counts[trait] += 1
                    break

    traits = []
    for trait, count in trait_counts.most_common():
        ratio = count / max(total, 1)
        if count >= 3:
            intensity = "Highly" if ratio > 0.3 else ("Moderately" if ratio > 0.15 else "Somewhat")
            traits.append(f"{intensity} {trait} — detected in {count} messages ({ratio:.0%})")
    return traits


def _analyze_communication_style(messages: List[Dict]) -> List[str]:
    if not messages:
        return []
    style = []
    lengths = [len(m["content"]) for m in messages]
    avg_length = sum(lengths) / len(lengths)

    if avg_length < 30:
        style.append(f"Short, concise messages (avg ~{avg_length:.0f} chars)")
    elif avg_length < 80:
        style.append(f"Moderate message length (avg ~{avg_length:.0f} chars)")
    else:
        style.append(f"Detailed, longer messages (avg ~{avg_length:.0f} chars)")

    emoji_pat = re.compile(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]")
    emoji_ratio = sum(1 for m in messages if emoji_pat.search(m["content"])) / len(messages)
    if emoji_ratio > 0.3:
        style.append(f"Heavy emoji user ({emoji_ratio:.0%} of messages)")
    elif emoji_ratio > 0.1:
        style.append(f"Moderate emoji usage ({emoji_ratio:.0%} of messages)")
    else:
        style.append(f"Rarely uses emojis ({emoji_ratio:.0%} of messages)")

    informal = re.compile(r"\b(gonna|wanna|gotta|kinda|bruh|bro|dude|lol|omg|idk)\b", re.IGNORECASE)
    inf_ratio = sum(1 for m in messages if informal.search(m["content"])) / len(messages)
    if inf_ratio > 0.3:
        style.append(f"Highly informal tone ({inf_ratio:.0%} use slang)")
    elif inf_ratio > 0.1:
        style.append("Mix of formal and informal language")
    else:
        style.append("Generally formal or neutral tone")

    q_ratio = sum(1 for m in messages if "?" in m["content"]) / len(messages)
    if q_ratio > 0.15:
        style.append(f"Inquisitive — {q_ratio:.0%} of messages are questions")

    return style


def extract_persona(messages: List[Dict]) -> Dict[str, List[str]]:
    """Extract user persona from conversation messages."""
    return {
        "habits": _analyze_habits(messages),
        "personal_facts": _analyze_personal_facts(messages),
        "personality_traits": _analyze_personality(messages),
        "communication_style": _analyze_communication_style(messages),
    }
