"""Text-Datenbank: Sprüche pro Keyword pro Sprache.

Sprachen: English (en), Deutsch (de).
Keywords EN (16): coffee, work, sarcasm, monday, cat, dog, nurse, gym, dad, mom,
                  coding, pizza, beer, teacher, firefighter, random
Keywords DE (11): coffee, work, sarcasm, monday, cat, dog, firefighter, nurse,
                  dad, mom, random
"""

from __future__ import annotations

import random

TEXTS: dict[str, dict[str, list[str]]] = {
    "en": {
        "coffee": [
            "But First Coffee",
            "Powered By Coffee",
            "Coffee Is My Personality",
            "Decaf? No Thanks.",
            "Talk To Me After Coffee",
            "Coffee Then Things",
            "Espresso Yourself",
            "Life Begins After Coffee",
            "May Your Coffee Be Strong",
            "Coffee: Because Adulting Is Hard",
        ],
        "work": [
            "Error 404 Motivation Not Found",
            "I Work Hard Because Milliseconds Matter",
            "Meeting Should Have Been An Email",
            "Professionally Over It",
            "Working Hard Or Hardly Working",
            "Out Of Office Mentally",
            "I'm Not Lazy, I'm On Energy Saving Mode",
            "Five More Minutes Of Fame",
            "Ctrl Alt Delete My Career",
        ],
        "sarcasm": [
            "Sarcasm Is My Love Language",
            "I'm Not Always Sarcastic, Sometimes I Sleep",
            "Sarcasm Loading Please Wait",
            "Caution: Sarcasm Levels Critical",
            "Sarcasm: Because Punching Is Frowned Upon",
            "Fluent In Sarcasm",
            "My Sarcasm Level Depends On Your Question",
            "Sarcastic Comment Loading",
        ],
        "monday": [
            "Monday Should Be Illegal",
            "I Survived Monday Once",
            "Monday The Curse Of The Calendar",
            "All Mondays Must Be Destroyed",
            "Not Today Monday",
            "Monday: Proof The Week Hates You",
            "Dear Monday, Go Away",
            "Monday Mood: NO.",
        ],
        "cat": [
            "My Cat Is My Therapist",
            "Cat Hair Is My Accessory",
            "Everything I Do Is Because Of The Cat",
            "Cats Before People",
            "Professional Cat Servant",
            "My Boss Has Whiskers",
            "Crazy Cat Person And Proud",
            "The Cat Chose Me",
        ],
        "dog": [
            "My Dog Is My Best Friend",
            "Sorry I'm Busy Walking My Dog",
            "Dog Mom Life",
            "Dog Dad Mode On",
            "Life Is Better With A Dog",
            "All You Need Is Love And A Dog",
            "Rescue Is My Favorite Breed",
            "Warning: Dog May Steal Your Seat",
        ],
        "nurse": [
            "Nursing Is A Work Of Heart",
            "Keep Calm I'm A Nurse",
            "Nurse Life Saving Lives One Shift At A Time",
            "Coffee Scrubs And Rubber Gloves",
            "Nurses Can't Fix Stupid But We Can Sedate It",
            "Stay Calm And Nurse On",
            "Eat Sleep Nurse Repeat",
        ],
        "gym": [
            "Sore Today Strong Tomorrow",
            "No Pain No Gain",
            "Gym Is My Therapy",
            "Lift Heavy Laugh Often",
            "Do You Even Lift?",
            "Sweat Is Just Fat Crying",
            "Beast Mode: Always On",
            "Train Insane Or Remain The Same",
        ],
        "dad": [
            "Best Dad Ever",
            "Dad Jokes Champion",
            "World's Okayest Dad",
            "Dad Fuel: Coffee And Bad Jokes",
            "The Man The Myth The Dad",
            "Dad: The Man The Legend",
            "Trust Me I'm A Dad",
        ],
        "mom": [
            "Best Mom Ever",
            "Mom Life Chose Me",
            "World's Okayest Mom",
            "Coffee Fueled Mom Powered",
            "Mom Of The Year Every Year",
            "Mama Bear Mode On",
            "Running On Mom Energy",
        ],
        "coding": [
            "It Works On My Machine",
            "Eat Sleep Code Repeat",
            "Talk Is Cheap Show Me The Code",
            "There Are 10 Types Of People",
            "Programmer By Day Gamer By Night",
            "Code Is Poetry",
            "Keep Calm And Debug On",
            "50 Lines Of Code 49 Bugs",
            "I Speak Fluent Python",
            "Ctrl S Is My Cardio",
        ],
        "pizza": [
            "Pizza Is My Soul Mate",
            "In Pizza We Crust",
            "Pizza Makes Everything Better",
            "Cut Me Some Pizza Cake",
            "Pizza First Everything Else Later",
            "You Can't Make Everyone Happy You're Not Pizza",
            "Carbs Are Calling",
            "Pizza Is Always A Good Idea",
        ],
        "beer": [
            "Beer Me",
            "Life Is Brewtiful",
            "Beer Makes Everything Funnier",
            "Hops To It",
            "Officially Off Beer Duty",
            "Good Beer Better Friends",
            "I'm Here For The Beer",
            "Craft Beer Consumer Since Forever",
        ],
        "teacher": [
            "Teacher Off Duty",
            "Teaching Is My Superpower",
            "I Teach What's Your Superpower",
            "Coffee Teacher Fuel",
            "Best Teacher Ever",
            "It's A Good Day To Teach",
            "Teacher Exhausted But Blessed",
        ],
        "firefighter": [
            "Firefighter Running Into Danger",
            "Rescue Save Fight Repeat",
            "Firefighter Heart Lion Courage",
            "Fearless Since Forever",
            "Born To Fight Fire",
            "Heat Nothing Give Everything",
            "Rescue Those In Need",
        ],
        "random": [
            "Bold Designs For Bold People",
            "Normal Is Boring",
            "Too Weird To Live Too Rare To Die",
            "Introvert But Willing To Discuss Design",
            "Overthinker In Chief",
            "Professional Overthinker",
            "Wear Your Attitude",
            "Silence Is Golden Duct Tape Is Silver",
            "Emotional Support Human",
            "Main Character Energy",
        ],
    },
    "de": {
        "coffee": [
            "Erstmal Kaffee",
            "Kaffee Ist Meine Persoenlichkeit",
            "Ohne Kaffee Kein Kommentar",
            "Rede Mit Mir Nach Dem Kaffee",
            "Kaffee Macht Mich Menschlich",
            "Entkoffeiniert? Nein Danke.",
            "Kaffee Und Dann Die Welt",
            "Mein Bluttyp Ist Kaffee",
        ],
        "work": [
            "Motivation Wird Geladen Fehler 404",
            "Arbeitest Du Oder Bist Du Beschaeftigt",
            "Dieses Meeting Waere Eine Email Gewesen",
            "Berufsmuessig Genervt",
            "Ich Bin Nicht Faul Ich Lade Nur",
            "Feierabend Im Kopf",
            "Strg Alt Entf Fur Meine Karriere",
        ],
        "sarcasm": [
            "Meine Geduld Hat Gekuendigt",
            "Sarkasmus Ist Meine Zweite Sprache",
            "Ich Bin Nicht Immer Sarkastisch Manchmal Schlafe Ich",
            "Sarkasmus Level: Kritisch",
            "Fluessig In Sarkasmus",
            "Warnung Sarkasmus Vorraus",
            "Antwortet Nur Mit Sarkasmus",
        ],
        "monday": [
            "Montag Sollte Verboten Sein",
            "Montag Der Fluch Des Kalenders",
            "Nicht Heute Montag",
            "Montag Ich Hasse Dich",
            "Alle Montage Muessen Zerstoert Werden",
            "Montag: Beweis Dass Die Woche Dich Hasst",
            "Montags Bin Ich Nur Deko",
        ],
        "cat": [
            "Meine Katze Ist Mein Therapeut",
            "Katzenhaar Ist Mein Accessoire",
            "Alles Was Ich Tue Ist Wegen Der Katze",
            "Katzen Vor Menschen",
            "Professioneller Katzenbediensteter",
            "Mein Chef Hat Schnurrhaare",
            "Die Katze Hat Mich Ausgesucht",
        ],
        "dog": [
            "Mein Hund Ist Mein Bester Freund",
            "Keine Zeit Ich Gassiere Den Hund",
            "Hundemama Leben",
            "Hundepapa Modus An",
            "Leben Ist Besser Mit Hund",
            "Rettungshund Is Meine Lieblingsrasse",
            "Warnung Hund Klaurt Deinen Platz",
        ],
        "firefighter": [
            "Retten Loeschen Bergen Schuetzen",
            "Feuerwehrherz Loewenmut",
            "Geboren Um Zu Loeschen",
            "Furchtlos Seit Immer",
            "Wo Andere Rennen Wir Hinein",
            "Feuerwehr Laeuft Gefahr Entgegen",
            "Mut bedeutet Auch Atemschutz",
        ],
        "nurse": [
            "Pflege Ist Herzenssache",
            "Ruhe Bewahren Ich Bin Pflegekraft",
            "Kaffee Kittel Und Handschuhe",
            "Pflegen Retten Durchhalten",
            "Essen Schlafen Pflegen Wiederholen",
            "Pflegekraft Von Beruf Held Von Berufung",
        ],
        "dad": [
            "Bester Papa Der Welt",
            "Papa Witz Champion",
            "Der Mann Der Mythos Der Papa",
            "Vertrau Mir Ich Bin Papa",
            "Papa Tankt Kaffee Und Flueche",
            "Weltbester Durchschnittspapa",
        ],
        "mom": [
            "Beste Mama Der Welt",
            "Mama Baer Modus An",
            "Mama Leben Hat Mich Gewaehlt",
            "Kaffeebetriebene Mama",
            "Mama Des Jahres Jedes Jahr",
            "Laeuft Auf Mama Energie",
        ],
        "random": [
            "Zeichen Setzen Jeden Tag",
            "Normal Ist Langweilig",
            "Profi Ueberdenker",
            "Trage Deine Haltung",
            "Hauptfigur Energie",
            "Schweigen Ist Golden Panzerband Ist Silber",
            "Emotionale Unterstuetzung Mensch",
            "Zu Selten Um Normale Zu Sein",
        ],
    },
}

SUPPORTED_LANGUAGES = ("en", "de")


def keywords(lang: str) -> list[str]:
    """Verfügbare Keywords für eine Sprache."""
    lang = lang.lower()
    if lang not in TEXTS:
        raise ValueError(f"Sprache nicht unterstützt: {lang!r} (erlaubt: {SUPPORTED_LANGUAGES})")
    return list(TEXTS[lang].keys())


def texts_for(lang: str, keyword: str) -> list[str]:
    """Alle Sprüche für Sprache+Keyword (leere Liste falls unbekannt)."""
    return list(TEXTS.get(lang.lower(), {}).get(keyword.lower(), []))


def random_text(lang: str, keyword: str | None = None, rng: random.Random | None = None) -> str:
    """Zufälliger Spruch; keyword=None wählt ein zufälliges Keyword."""
    rng = rng or random
    lang = lang.lower()
    if lang not in TEXTS:
        raise ValueError(f"Sprache nicht unterstützt: {lang!r}")
    kw = keyword or rng.choice(list(TEXTS[lang].keys()))
    pool = TEXTS[lang].get(kw.lower())
    if not pool:
        raise ValueError(f"Keine Texte für Keyword {kw!r} in Sprache {lang!r}")
    return rng.choice(pool)
