"""
Notes, scales, and chords definitions.

A few definitions:

* Scale Quality: The characteristic sound or "flavor" of a scale, determined by its
specific pattern of intervals (semitones) from the root note.
Examples include major, minor, pentatonic, blues, or whole-tone.
* Chord Quality: The characteristic sound or "flavor" of a chord, determined by its
specific combination of intervals (semitones) above its root note.
Common examples include major, minor, diminished, augmented, or dominant 7th.
* Semitone Pattern: A numerical representation of a musical scale or chord, showing
the precise distance in semitones (half-steps) of each note from the starting (root)
note. For example, the semitone pattern for a major scale is [0, 2, 4, 5, 7, 9, 11].

"""

from typing import Dict, Sequence, Tuple
from tonal.util import (
    note_name_pattern,
    parse_note_name,
    add_pattern_aliases,
)

import re


# Define root notes to MIDI note numbers
root_notes: Dict[str, int] = {
    "C": 60,
    "C#": 61,
    "Db": 61,
    "D": 62,
    "D#": 63,
    "Eb": 63,
    "E": 64,
    "F": 65,
    "F#": 66,
    "Gb": 66,
    "G": 67,
    "G#": 68,
    "Ab": 68,
    "A": 69,
    "A#": 70,
    "Bb": 70,
    "B": 71,
}

# Regex to match root note at the start of a scale string (e.g., 'C', 'C#', 'Db', etc.), followed by space or end
root_note_re = re.compile(r"^([A-Ga-g][#b]?)(?=\s|$)")

scale_quality = {
    # Western Diatonic & Common Scales (retained as before)
    "major": (0, 2, 4, 5, 7, 9, 11),
    "natural_minor": (0, 2, 3, 5, 7, 8, 10),
    "harmonic_minor": (0, 2, 3, 5, 7, 8, 11),
    "melodic_minor_ascending": (0, 2, 3, 5, 7, 9, 11),
    "melodic_minor_descending": (0, 2, 3, 5, 7, 8, 10),
    "major_pentatonic": (0, 2, 4, 7, 9),
    "minor_pentatonic": (0, 3, 5, 7, 10),
    "blues": (0, 3, 5, 6, 7, 10),
    "chromatic": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
    "whole_tone": (0, 2, 4, 6, 8, 10),
    "diminished": (0, 2, 3, 5, 6, 8, 9, 11),
    "diminished_half_whole": (0, 1, 3, 4, 6, 7, 9, 10),
    "augmented": (0, 3, 4, 7, 8, 11),
    "lydian": (0, 2, 4, 6, 7, 9, 11),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "phrygian": (0, 1, 3, 5, 7, 8, 10),
    "locrian": (0, 1, 3, 4, 6, 8, 10),
    "aeolian": (0, 2, 3, 5, 7, 8, 10),
    "ionian": (0, 2, 4, 5, 7, 9, 11),
    # Major Jazz Scales (distinct or commonly named in jazz)
    "bebop_dominant": (
        0,
        2,
        4,
        5,
        7,
        9,
        10,
        11,
    ),  # Mixolydian with added M7 (or b7, M7)
    "bebop_major": (0, 2, 4, 5, 7, 8, 9, 11),  # Major with added b6 (or M6, b6)
    "bebop_minor": (0, 2, 3, 4, 5, 7, 9, 10),  # Dorian with added M3 (or m3, M3)
    "bebop_melodic_minor": (0, 2, 3, 5, 7, 8, 9, 11),  # Melodic Minor with added b6
    "altered": (0, 1, 3, 4, 6, 8, 10),  # 7th mode of Melodic Minor, aka Super Locrian
    "lydian_dominant": (
        0,
        2,
        4,
        6,
        7,
        9,
        10,
    ),  # 4th mode of Melodic Minor, aka Mixolydian #11
    "phrygian_dominant": (
        0,
        1,
        4,
        5,
        7,
        8,
        10,
    ),  # 5th mode of Harmonic Minor (also common in Middle Eastern music)
    # Indian Ragas (distinct from Western scales, or now canonical here)
    # Re-checking semitone patterns and prioritizing jazz names
    "todi": (0, 1, 3, 6, 7, 8, 11),  # Hindustani Todi Thaat
    "poorvi": (0, 1, 4, 6, 7, 8, 11),  # Hindustani Poorvi Thaat
    "marwa": (0, 1, 4, 6, 7, 9, 11),  # Hindustani Marwa Thaat
    "chalanata": (0, 3, 5, 6, 7, 10, 11),  # Melakarta 36
    "hamsadhwani": (0, 4, 7, 9, 11),  # Pentatonic raga
    # Potential clashes:
    "bhairav": (0, 1, 4, 5, 7, 8, 11),  # Hindustani Bhairav Thaat
    "chakravakam": (0, 1, 4, 5, 7, 9, 10),  # Melakarta 16
    "malkauns": (0, 3, 5, 8, 10),  # Pentatonic raga
}

_scale_quality_western_aliases = {
    # Western Aliases
    "": "major",
    "maj": "major",
    "M": "major",
    "min": "natural_minor",
    "m": "natural_minor",
    "minor": "natural_minor",
    "harmonic": "harmonic_minor",
    "melodic": "melodic_minor_ascending",
    "penta major": "major_pentatonic",
    "penta min": "minor_pentatonic",
    "pentatonic": "major_pentatonic",
    "penta": "major_pentatonic",
    "minor penta": "minor_pentatonic",
    "major penta": "major_pentatonic",
    "whl tone": "whole_tone",
    "diminished": "diminished",
    "dim": "diminished",
    "diminished (whole-half)": "diminished",
    "diminished (half-whole)": "diminished_half_whole",
    "aug": "augmented",
    "chrom": "chromatic",
    "blues scale": "blues",
    "dor": "dorian",
    "phr": "phrygian",
    "lyd": "lydian",
    "mix": "mixolydian",
    "aeo": "aeolian",
    "ion": "ionian",
    "nat min": "natural_minor",
    "harm min": "harmonic_minor",
    "mel min asc": "melodic_minor_ascending",
    "mel min desc": "melodic_minor_descending",
    "w-h dim": "diminished",
    "h-w dim": "diminished_half_whole",
}

_scale_quality_jazz_aliases = {
    # Jazz Aliases
    "bebop dom": "bebop_dominant",
    "bebop maj": "bebop_major",
    "bebop min": "bebop_minor",
    "bebop dorian": "bebop_minor",  # Common alias for bebop minor
    "bebop melodic": "bebop_melodic_minor",
    "alt": "altered",
    "super locrian": "altered",
    "lyd dom": "lydian_dominant",
    "mixolydian #11": "lydian_dominant",
    "acoustic scale": "lydian_dominant",  # Also sometimes called this
    "phryg dom": "phrygian_dominant",
    "dominant phrygian": "phrygian_dominant",
    "mixolydian b2 b6": "phrygian_dominant",  # If you want to get descriptive
}

_scale_quality_raga_aliases = {
    # Indian Raga Aliases
    # Aliases for Ragas whose patterns match Western/Jazz scales:
    "bilawal": "major",  # Hindustani Thaat for Major
    "ionian raga": "major",
    "shankarabharanam": "major",  # Carnatic Melakarta 29 for Major
    "dheerasankarabharanam": "major",  # Carnatic Melakarta 29 for Major
    "kharaharapriya": "dorian",  # Carnatic Melakarta 22 for Dorian
    "melakarta 22": "dorian",
    "kafi": "dorian",  # Hindustani Thaat for Dorian
    "harikambhoji": "mixolydian",  # Carnatic Melakarta 28 for Mixolydian
    "melakarta 28": "mixolydian",
    "khamaj": "mixolydian",  # Hindustani Thaat for Mixolydian
    "natabhairavi": "natural_minor",  # Carnatic Melakarta 20 for Natural Minor
    "melakarta 20": "natural_minor",
    "asavari": "natural_minor",  # Hindustani Thaat for Natural Minor / Aeolian
    "aeolian raga": "natural_minor",
    "hanumatodi": "phrygian",  # Carnatic Melakarta 8 for Phrygian
    "melakarta 8": "phrygian",
    "phrygian raga": "phrygian",
    "kalyan": "lydian",  # Hindustani Thaat for Lydian
    "kirwani": "harmonic_minor",  # Melakarta 21, identical to Harmonic Minor
    "melakarta 21": "harmonic_minor",
    "mayamalavagowla": "bhairav",  # Carnatic Melakarta 15
    "melakarta 15": "bhairav",
    "bhupali": "major_pentatonic",  # Hindustani Raga identical to Major Pentatonic
    "mohnam": "major_pentatonic",  # Carnatic equivalent of Bhupali / Major Pentatonic
    "durga": "major_pentatonic",
    "deshkar": "major_pentatonic",
    "carnatic major": "major",  # Common reference for the Carnatic major scale
    "carnatic minor": "natural_minor",  # Common reference for the Carnatic natural minor scale
    # Aliases for Ragas unique to scale_quality (or now canonical here)
    "bhairav thaat": "bhairav",
    "todi thaat": "todi",
    "poorvi thaat": "poorvi",
    "marwa thaat": "marwa",
    "melakarta 36": "chalanata",
    "melakarta 16": "chakravakam",
    "hansadhwani raga": "hamsadhwani",
    "malkauns raga": "malkauns",
    "indian m minor": "malkauns",  # A less common, but sometimes used, description
}

_scale_quality_backcompat_aliases = {
    # Back-compat aliases mapping spaced names to underscored canonical names
    "natural minor": "natural_minor",
    "harmonic minor": "harmonic_minor",
    "melodic minor ascending": "melodic_minor_ascending",
    "melodic minor descending": "melodic_minor_descending",
    "major pentatonic": "major_pentatonic",
    "minor pentatonic": "minor_pentatonic",
    "whole tone": "whole_tone",
    "bebop dominant": "bebop_dominant",
    "bebop major": "bebop_major",
    "bebop minor": "bebop_minor",
    "bebop melodic minor": "bebop_melodic_minor",
    "lydian dominant": "lydian_dominant",
    "phrygian dominant": "phrygian_dominant",
}

scale_quality_alias = {
    **_scale_quality_western_aliases,
    **_scale_quality_jazz_aliases,
    **_scale_quality_raga_aliases,
    **_scale_quality_backcompat_aliases,
}


# TODO: Separate base and aliases
# TODO: Verify completeness and more chord definitions if needed
# TODO: See if defs can be infered from parsing the chord names
# Define quality and extension intervals
chord_quality: Dict[str, Sequence[int]] = {
    "": (0, 4, 7),  # Major triad, 'C' -> 'Cmaj
    "maj": (0, 4, 7),  # Major triad
    "M": (0, 4, 7),  # Major triad
    "m": (0, 3, 7),  # Minor triad
    "min": (0, 3, 7),  # Minor triad
    "dim": (0, 3, 6),  # Diminished triad
    "aug": (0, 4, 8),  # Augmented triad
    "7": (0, 4, 7, 10),  # Dominant 7th
    "7M": (0, 4, 7, 11),  # Major 7th
    "maj7": (0, 4, 7, 11),  # Major 7th
    "min7": (0, 3, 7, 10),  # Minor 7th
    "minmaj7": (0, 3, 7, 11),  # Minor major 7th
    "dim7": (0, 3, 6, 9),  # Diminished 7th
    "hdim7": (0, 3, 6, 10),  # Half-diminished 7th
    "aug7": (0, 4, 8, 10),  # Augmented 7th
    "6": (0, 4, 7, 9),  # Major 6th
    "min6": (0, 3, 7, 9),  # Minor 6th
    "9": (0, 4, 7, 10, 14),  # Dominant 9th
    "maj9": (0, 4, 7, 11, 14),  # Major 9th
    "min9": (0, 3, 7, 10, 14),  # Minor 9th
    "11": (0, 4, 7, 10, 14, 17),  # Dominant 11th
    "maj11": (0, 4, 7, 11, 14, 17),  # Major 11th
    "min11": (0, 3, 7, 10, 14, 17),  # Minor 11th
    "13": (0, 4, 7, 10, 14, 17, 21),  # Dominant 13th
    "maj13": (0, 4, 7, 11, 14, 17, 21),  # Major 13th
    "min13": (0, 3, 7, 10, 14, 17, 21),  # Minor 13th
}

# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------


def register_root_note(note_name: str, midi_value: int) -> None:
    """Register a new root note with its MIDI value.

    Args:
        note_name: The name of the note (e.g., 'C', 'C#', 'Db')
        midi_value: The MIDI note number (0-127)

    >>> register_root_note('H', 71)  # German notation for B
    >>> root_notes['H']
    71
    """
    if not (0 <= midi_value <= 127):
        raise ValueError(f"MIDI value must be between 0 and 127, got {midi_value}")
    root_notes[note_name] = midi_value


def register_scale_quality(quality_name: str, semitone_pattern: Sequence[int]) -> None:
    """Register a new scale quality with its semitone pattern.

    Args:
        quality_name: The name of the scale quality
        semitone_pattern: Sequence of semitone intervals from root

    >>> register_scale_quality('custom_scale', (0, 2, 5, 7, 10))
    >>> scale_quality['custom_scale']
    (0, 2, 5, 7, 10)
    """
    pattern_tuple = tuple(semitone_pattern)
    if not all(isinstance(x, int) and 0 <= x <= 11 for x in pattern_tuple):
        raise ValueError("Semitone pattern must contain integers between 0 and 11")
    if 0 not in pattern_tuple:
        raise ValueError("Semitone pattern must include 0 (the root note)")
    scale_quality[quality_name] = pattern_tuple


def register_scale_quality_alias(alias: str, canonical_name: str) -> None:
    """Register an alias for an existing scale quality.

    Args:
        alias: The alias name
        canonical_name: The existing scale quality name or alias

    >>> register_scale_quality_alias('my_major', 'major')
    >>> scale_quality_alias['my_major']
    'major'
    """
    # Verify that the canonical name exists (either in scale_quality or as an alias)
    try:
        semitone_pattern(canonical_name)
    except ValueError:
        raise ValueError(
            f"Canonical name '{canonical_name}' is not a valid scale quality"
        )
    scale_quality_alias[alias] = canonical_name


def register_chord_quality(quality_name: str, semitone_pattern: Sequence[int]) -> None:
    """Register a new chord quality with its semitone pattern.

    Args:
        quality_name: The name of the chord quality
        semitone_pattern: Sequence of semitone intervals from root

    >>> register_chord_quality('my_chord', (0, 4, 7, 10, 13))
    >>> chord_quality['my_chord']
    (0, 4, 7, 10, 13)
    """
    pattern_tuple = tuple(semitone_pattern)
    if not all(isinstance(x, int) and x >= 0 for x in pattern_tuple):
        raise ValueError("Semitone pattern must contain non-negative integers")
    if 0 not in pattern_tuple:
        raise ValueError("Semitone pattern must include 0 (the root note)")
    chord_quality[quality_name] = pattern_tuple


def list_root_notes() -> Dict[str, int]:
    """List all registered root notes.

    Returns:
        Dictionary mapping note names to MIDI values

    >>> notes = list_root_notes()
    >>> 'C' in notes
    True
    >>> notes['C']
    60
    """
    return dict(root_notes)


def list_scale_qualities(include_aliases: bool = False) -> Dict[str, Sequence[int]]:
    """List all registered scale qualities.

    Args:
        include_aliases: If True, include aliases in the listing

    Returns:
        Dictionary mapping quality names to semitone patterns

    >>> qualities = list_scale_qualities()
    >>> 'major' in qualities
    True
    >>> qualities['major']
    (0, 2, 4, 5, 7, 9, 11)
    """
    result = dict(scale_quality)
    if include_aliases:
        for alias, canonical in scale_quality_alias.items():
            if canonical in scale_quality:
                result[alias] = scale_quality[canonical]
            elif canonical in scale_quality_alias:
                # Handle alias chains
                try:
                    pattern = semitone_pattern(canonical)
                    result[alias] = pattern
                except ValueError:
                    pass  # Skip invalid aliases
    return result


def list_scale_quality_aliases() -> Dict[str, str]:
    """List all registered scale quality aliases.

    Returns:
        Dictionary mapping aliases to canonical names

    >>> aliases = list_scale_quality_aliases()
    >>> 'maj' in aliases
    True
    >>> aliases['maj']
    'major'
    """
    return dict(scale_quality_alias)


def list_chord_qualities() -> Dict[str, Sequence[int]]:
    """List all registered chord qualities.

    Returns:
        Dictionary mapping quality names to semitone patterns

    >>> qualities = list_chord_qualities()
    >>> 'maj' in qualities
    True
    >>> qualities['maj']
    (0, 4, 7)
    """
    return dict(chord_quality)


# TODO: Make a framework for user-defined aliases


# -----------------------------------------------------------------------------
# Validation & Utilities
# -----------------------------------------------------------------------------


# Define a specific error for incorrect scale specifications
class IncorrectScaleSpecification(ValueError):
    """Raised when a scale string cannot be parsed/validated into root and quality."""


def list_scales_string() -> str:
    """Return a user-friendly help string describing scale syntax and valid values.

    Includes:
    - Anatomy of a scale specification
    - Valid roots
    - Valid qualities (including aliases)
    """
    valid_roots = sorted(list_root_notes().keys())
    valid_roots_fmt = ", ".join(f"'{r}'" for r in valid_roots)

    valid_qualities = sorted(list_scale_qualities(include_aliases=True).keys())
    # show qualities as a wrapped, indented list for readability
    qualities_fmt = "\n  - " + "\n  - ".join(
        [q if q else "<empty string>" for q in valid_qualities]
    )

    return (
        "Scale specification anatomy: '<root> <quality>' (case-insensitive).\n"
        "- Root is optional (defaults to 'C' in some contexts).\n"
        "- Empty quality means 'major' (alias '').\n\n"
        f"Valid roots: {valid_roots_fmt}.\n"
        f"Valid qualities (including aliases):{qualities_fmt}\n"
    )


def validate_scale_semitone_pattern_uniquness(scale_quality: dict) -> bool:
    """
    Validates that all scale qualities have unique semitone patterns.
    """
    seen = {}
    for name, pattern in scale_quality.items():
        pattern_tuple = tuple(pattern)
        if pattern_tuple in seen:
            raise ValueError(
                f"Scale quality '{name}' has a non-unique semitone pattern. "
                f"Duplicates: {seen[pattern_tuple]} and {name}"
            )
        seen[pattern_tuple] = name
    return True


def validate_scale_aliases(scale_quality: dict, scale_aliases: dict) -> bool:
    """
    Validates that all values in the scale_aliases dictionary are valid keys
    in the scale_qualities dictionary.

    Args:
        scale_quality (dict): The dictionary of canonical scale qualities and patterns.
        scale_aliases (dict): The dictionary of scale aliases.

    Returns:
        bool: True if all aliases are valid, False otherwise.
    """
    all_valid = True
    invalid_aliases = []
    for alias_key, canonical_name in scale_aliases.items():
        if canonical_name not in scale_quality:
            print(
                f"Validation Error: Alias '{alias_key}' points to "
                f"non-existent scale quality '{canonical_name}' in scale_quality."
            )
            invalid_aliases.append(alias_key)
            all_valid = False

    if not all_valid:
        raise ValueError(f"Invalid aliases found: {invalid_aliases}")


# validate_scale_semitone_pattern_uniquness(scale_quality)  # Disabled: duplicate patterns are allowed for now  # TODO: move duplicates to aliases
validate_scale_aliases(scale_quality, scale_quality_alias)


# -----------------------------------------------------------------------------
# Access and Usage
# -----------------------------------------------------------------------------


def semitone_pattern(quality: str) -> tuple:
    """
    Get the semitone pattern for a given scale quality string.
    Looks in scale_quality, then in scale_quality_alias (using the alias to look in scale_quality).
    Raises ValueError if not found.

    >>> semitone_pattern('major')
    (0, 2, 4, 5, 7, 9, 11)
    >>> semitone_pattern('maj')
    (0, 2, 4, 5, 7, 9, 11)
    >>> semitone_pattern('')
    (0, 2, 4, 5, 7, 9, 11)
    >>> semitone_pattern('dorian')
    (0, 2, 3, 5, 7, 9, 10)

    """
    if quality in scale_quality:
        return scale_quality[quality]
    elif quality in scale_quality_alias:
        alias = scale_quality_alias[quality]
        if alias in scale_quality:
            return scale_quality[alias]
        elif alias in scale_quality_alias:
            # Handle alias chaining (e.g., '' -> 'major' -> scale_quality)
            return semitone_pattern(alias)
    raise ValueError(f"Unknown scale quality: {quality}")


def scale_params(scale: str, midi_notes: bool = False):
    """
    Parse a scale specification string and return (root_note, scale_quality).
    If midi_notes is True, returns (root_note_midi, semitone_pattern).
    If midi_notes is False, returns (root_note_str, scale_quality_str).
    The root_note can be an empty string (meaning default root).

    >>> scale_params('C major')
    ('C', 'major')
    >>> scale_params('dorian')
    ('', 'dorian')
    >>> scale_params('C')
    ('C', '')
    >>> scale_params('C', midi_notes=True)
    (60, (0, 2, 4, 5, 7, 9, 11))
    >>> scale_params('dorian', midi_notes=True)
    (None, (0, 2, 3, 5, 7, 9, 10))

    """
    s = scale.strip()
    m = root_note_re.match(s)
    if m and m.group(1).upper() in (k.upper() for k in root_notes):
        root = m.group(1).capitalize()
        quality = s[len(root) :].strip()
    else:
        root = ""
        quality = s.strip()

    # If only root is given, quality is empty string (defaults to major via alias '')
    if quality == "" and root:
        quality = ""

    # Validate root and quality; build helpful error if invalid
    invalid_root = False
    if root and root.upper() not in (k.upper() for k in root_notes):
        invalid_root = True

    try:
        pattern = semitone_pattern(quality)
    except ValueError:
        pattern = None
        invalid_quality = True
    else:
        invalid_quality = False

    if invalid_root or invalid_quality:
        problems = []
        if invalid_root:
            problems.append(f"unknown root '{root}'")
        if invalid_quality:
            problems.append(f"unknown scale quality '{quality}'")
        problems_text = "; ".join(problems) if problems else "invalid specification"

        raise IncorrectScaleSpecification(
            (
                f"Incorrect scale specification: '{scale}' ({problems_text}).\n"
                + list_scales_string()
            )
        )

    if midi_notes:
        root_midi = root_notes[root] if root else None
        return root_midi, pattern
    else:
        return root, quality


def scale_midi_notes(
    scale: str = "C major",
    midi_range: Tuple[int, int] = (0, 127),
    *,
    default_root: str = "C",
) -> tuple:
    """
    Return a tuple of all MIDI note numbers in the given range that belong to the specified scale.

    Args:
        scale (str): The scale string, e.g., 'C major', 'D# minor pentatonic'.
        midi_range (tuple): The (min, max) MIDI note numbers to include.
        default_root (str): The root note to use if not found in the scale string (default 'C').

    Returns:
        tuple: MIDI note numbers in the scale within the specified range.


    >>> scale_midi_notes('E')  # doctest: +ELLIPSIS
    (1, 3, 4, 6, 8, 9, 11, 13, 15, 16, ...114, 116, 117, 119, 121, 123, 124, 126)

    If it's suprising that it starts at 1, because you were expecting 'E' (major)
    to start with 4, remember that scale_midi_notes is designed to return all notes in the scale
    within the MIDI range, not just the notes starting from the root note.
    The first note in that range that is in E major is actually a C#, which the
    midi note 1 is. You can control the range through:

    >>> scale_midi_notes('E', midi_range=(4, 30))  # doctest: +ELLIPSIS
    (4, 6, 8, 9, 11, 13, 15, 16, 18, 20, 21, 23, 25, 27, 28, 30)

    You see that if no scale quality is specified, it defaults to 'major'.
    On the other hand, if no root note is specified, it defaults to 'C', or what ever
    you tell `default_root` is should be.

    >>> assert (
    ...     scale_midi_notes('', midi_range=(60, 72))
    ...     == scale_midi_notes('C', midi_range=(60, 72))
    ...     == scale_midi_notes('major', midi_range=(60, 72))
    ...     == scale_midi_notes('C major', midi_range=(60, 72))
    ...     == (60, 62, 64, 65, 67, 69, 71, 72)
    ... )

    >>> scale_midi_notes('Db minor pentatonic', midi_range=(60, 72))
    (61, 64, 66, 68, 71)

    """
    # Parse root and pattern
    root, quality = scale_params(scale)
    if not root:
        root = default_root
    if root not in root_notes:
        raise ValueError(f"Unknown root note: {root}")
    root_midi = root_notes[root]
    pattern = semitone_pattern(quality)
    notes = []
    # Find the first root note in the midi_range
    first_root = root_midi
    while first_root < midi_range[0]:
        first_root += 12
    while first_root > midi_range[0]:
        first_root -= 12
    # Generate all scale notes in the range
    for midi_note in range(first_root, midi_range[1] + 1, 12):
        for interval in pattern:
            n = midi_note + interval
            if midi_range[0] <= n <= midi_range[1]:
                notes.append(n)
    return tuple(sorted(set(notes)))
