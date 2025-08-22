# Rules

This style guide includes the following Vale rules based on the [Elastic Style Guide](https://docs.elastic.dev/tech-writing-guidelines/):

## Grammar and spelling rules

- `Accessibility.yml`: Flags language that defines people by their disability (for example, "disabled person" instead of "person with a disability").
- `BritishSpellings.yml`: Enforces American English spellings over British English (such as "organize" not "organise").
- `Conjunctions.yml`: Ensures correct article usage with acronyms based on pronunciation (such as "an HTML" not "a HTML").
- `Contractions.yml`: Suggests using contractions for more conversational tone (such as "aren't" instead of "are not").
- `FutureTense.yml`: Flags future tense constructions, encouraging present tense to describe current product state.
- `Numbers.yml`: Requires spelling out numbers one through nine as words instead of numerals.
- `OxfordComma.yml`: Enforces the use of Oxford/serial commas in lists.
- `Passive.yml`: Identifies passive voice constructions and suggests active voice alternatives.
- `Semicolons.yml`: Flags semicolon usage with a reminder to use them judiciously.
- `SubjunctiveMood.yml`: Discourages subjunctive mood words like "should", "would", "could".

## Formatting and punctuation rules

- `Capitalization.yml`: Enforces sentence-style capitalization in headings with exceptions for proper nouns.
- `Decimals.yml`: Requires leading zeros in decimal numbers (such as "0.5" not ".5").
- `Dimensions.yml`: Enforces proper dimension formatting without spaces (such as "1920x1080" not "1920 X 1080").
- `Ellipses.yml`: Discourages the use of ellipses in technical writing.
- `EmDashes.yml`: Flags improper spacing around em dashes.
- `EndPunctuation.yml`: Removes punctuation at the end of headings.
- `Exclamation.yml`: Suggests removing exclamation points for more professional tone.
- `HeadingColons.yml`: Ensures proper capitalization after colons in headings.
- `Parentheses.yml`: Checks for proper parentheses usage.
- `QuotesPunctuation.yml`: Enforces punctuation placement outside quotation marks.
- `SentenceSpacing.yml`: Ensures single spaces between sentences.
- `SmartQuotes.yml`: Flags smart/curly quotes and suggests straight quotes.
- `Spacing.yml`: Identifies improper spacing between words and after punctuation.

## Content and style rules

- `Acronyms.yml`: Flags undefined acronyms that need to be spelled out on first use.
- `DirectionalLanguage.yml`: Discourages spatial references like "above", "below", "left", "right".
- `DontUse.yml`: Flags prohibited words and phrases (such as "easy", "simply", "just").
- `FirstPerson.yml`: Flags first-person pronouns to maintain objective tone.
- `Gender.yml`: Flags problematic gendered language like "he/she".
- `GenderBias.yml`: Suggests gender-neutral alternatives for job titles and roles.
- `Latinisms.yml`: Flags Latin terms and suggests plain English alternatives (such as "for example" instead of "e.g.").
- `MeaningfulCTAs.yml`: Ensures link text is meaningful (flags "click here" type links).
- `Negations.yml`: Identifies negative constructions and suggests positive alternatives.
- `Repetition.yml`: Flags repeated words or phrases.
- `Violent.yml`: Flags violent, offensive, or ableist terminology.
- `WordChoice.yml`: Suggests preferred terminology and word choices.
- `Wordiness.yml`: Identifies wordy phrases and suggests concise alternatives.

## Technical and accessibility rules

- `ConflictMarkers.yml`: Prevents committing Git merge conflict markers.
- `DeviceAgnosticism.yml`: Ensures content works across different devices and interfaces.
- `PluralAbbreviations.yml`: Prevents incorrect apostrophe usage in plural abbreviations.
- `Readability.yml`: Checks Flesch-Kincaid reading level (target: grade nine or below).
- `TooComplex.yml`: Flags sentences with too many conjunctions that need to be split.

Each rule includes appropriate error levels (error, warning, suggestion) and links to relevant sections of the Elastic Style Guide for more context.
