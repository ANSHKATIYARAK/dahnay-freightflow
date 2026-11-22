import re

email_text = """Hi Murali,

Saw DahNAY is scaling ocean freight volumes out of Chennai and Tuticorin, and actively hiring documentation executives to keep up with manual entry.

Re-keying shipper SIs into CargoWise typically eats 20 minutes per file and risks $150 B/L amendment penalties when typos slip through.

We built FreightFlow to automate this: it parses raw Excel/PDF SIs, catches container check-digit typos, audits SOLAS weights, and generates ready-to-import CargoWise Universal XML in under 1 second.

Here is the 60-second live demo: https://dahnay-freightflow.vercel.app

Would you be open to testing this on 5 of your redacted historical files? We process them in a private sandbox with zero data retention.

Best regards,
Ansh Katiyar
Founder, FreightFlow"""

words = re.findall(r'\b\w+\b', email_text)
sentences = [s.strip() for s in re.split(r'[.!?]+', email_text) if s.strip()]
word_count = len(words)
sentence_count = len(sentences)
avg_sentence_len = word_count / max(1, sentence_count)

def count_syllables(w):
    w = w.lower()
    return max(1, len(re.findall(r'[aeiouy]+', w)))

syllables = sum(count_syllables(w) for w in words)
fk_grade = 0.39 * (word_count / max(1, sentence_count)) + 11.8 * (syllables / max(1, word_count)) - 15.59

spam_triggers = ['free', 'guarantee', 'urgent', 'act now', 'make money', 'cash', 'risk-free', 'winner', '100% free']
detected_spam = [s for s in spam_triggers if s in email_text.lower()]

print(f"Word Count: {word_count} words (Target: 75-125 words)")
print(f"Sentence Count: {sentence_count}")
print(f"Average Sentence Length: {avg_sentence_len:.1f} words/sentence")
print(f"Flesch-Kincaid Grade Level: Grade {fk_grade:.1f} (Target: Grade 5-7)")
print(f"Spam Trigger Words: {detected_spam if detected_spam else 'None (100% Clean)'}")
