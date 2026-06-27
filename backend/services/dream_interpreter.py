"""
Dream Decoder - Multilingual Dream Interpreter Service
Provides deep psychological and symbolic analysis of dream content in multiple languages.
"""
import re
from backend.services.language_detector import detect_with_fallback
from backend.services.dream_symbols import find_symbols_in_text, resolve_keyword_symbol
from backend.services.translations import get_interpretation_template


# Multilingual interpretation templates
INTERPRETATION_TEMPLATES = {
    'en': {
        'intro': "Your dream weaves together symbols of {symbols} with a strong {emotion} emotional undercurrent.",
        'mid_positive': "The interaction of these elements reflects a positive emotional state in your dream.",
        'mid_negative': "The interaction of these elements reflects an area of emotional challenge in your dream.",
        'mid_neutral': "The interaction of these elements suggests a period of observation and balance.",
        'closing': "Your subconscious highlights these specific details to help you process your experiences.",
        'no_elements': "This dream reflects your current mental state, primarily characterized by a {emotion} tone.",
        'insight_fear': "Your mind is safely processing these anxieties while you sleep. You have the strength to navigate these feelings.",
        'insight_joy': "Your subconscious is capturing a moment of positivity. Carry this energy with you.",
        'insight_sadness': "Allow yourself to process these emotions. This dream is a step toward emotional clarity.",
        'insight_default': "Reflect on these symbols as they appear in your dream. Your inner mind is processing your daily experiences."
    },
    'hi': {
        'intro': "आपका स्वप्न {symbols} के प्रतीकों को एक मजबूत {emotion} भावनात्मक धारा के साथ बुनता है।",
        'mid_positive': "इन तत्वों की परस्पर क्रिया आपके सपने में एक सकारात्मक भावनात्मक स्थिति को दर्शाती है।",
        'mid_negative': "इन तत्वों की परस्पर क्रिया आपके सपने में भावनात्मक चुनौती के क्षेत्र को दर्शाती है।",
        'mid_neutral': "इन तत्वों की परस्पर क्रिया अवलोकन और संतुलन की अवधि का सुझाव देती है।",
        'closing': "आपका अवचेतन आपके अनुभवों को संसाधित करने में मदद करने के लिए इन विशिष्ट विवरणों को उजागर करता है।",
        'no_elements': "यह सपना आपकी वर्तमान मानसिक स्थिति को दर्शाता है, जो मुख्य रूप से {emotion} स्वर द्वारा विशेषता है।",
        'insight_fear': "जब आप सोते हैं तो आपका मन इन चिंताओं को सुरक्षित रूप से संसाधित कर रहा होता है। आपके पास इन भावनाओं को नेविगेट करने की ताकत है।",
        'insight_joy': "आपका अवचेतन सकारात्मकता के क्षण को कैद कर रहा है। इस ऊर्जा को अपने साथ रखें।",
        'insight_sadness': "स्वयं को इन भावनाओं को संसाधित करने दें। यह सपना भावनात्मक स्पष्टता की दिशा में एक कदम है।",
        'insight_default': "इन प्रतीकों पर विचार करें जैसे वे आपके सपने में दिखाई देते हैं। आपका आंतरिक मन आपके दैनिक अनुभवों को संसाधित कर रहा है।"
    },
    'mr': {
        'intro': "तुमचे स्वप्न {symbols} च्या प्रतीकांना एका मजबूत {emotion} भावनिक प्रवाहासह विणते.",
        'mid_positive': "या घटकांचा परस्परसंवाद तुमच्या स्वप्नातील सकारात्मक भावनिक स्थिती दर्शवतो.",
        'mid_negative': "या घटकांचा परस्परसंवाद तुमच्या स्वप्नातील भावनिक आव्हानाचे क्षेत्र दर्शवतो.",
        'mid_neutral': "या घटकांचा परस्परसंवाद निरीक्षण आणि संतुलनाचा काळ सूचित करतो.",
        'closing': "तुमचे अवचेतन तुमचे अनुभव प्रक्रिया करण्यासाठी हे विशिष्ट तपशील हायलाइट करते.",
        'no_elements': "हे स्वप्न तुमच्या सध्याच्या मानसिक स्थितीचे प्रतिबिंब आहे, जे प्रामुख्याने {emotion} स्वराद्वारे वैशिष्ट्यीकृत आहे.",
        'insight_fear': "तुम्ही झोपलेले असताना तुमचे मन या चिंतांवर सुरक्षितपणे प्रक्रिया करत आहे. या भावनांना सामोरे जाण्याची ताकद तुमच्यात आहे.",
        'insight_joy': "तुमचे अवचेतन सकारात्मकतेचा एक क्षण कॅप्चर करत आहे. ही ऊर्जा तुमच्यासोबत ठेवा.",
        'insight_sadness': "स्वत स्वतःला या भावनांवर प्रक्रिया करण्याची परवानगी द्या. हे स्वप्न भावनिक स्पष्टतेच्या दिशेने एक पाऊल आहे.",
        'insight_default': "तुमच्या स्वप्नात दिसणाऱ्या या प्रतीकांवर विचार करा. तुमचे आंतरिक मन तुमच्या दैनंदिन अनुभवांवर प्रक्रिया करत आहे."
    },
    'hinglish': {
        'intro': "Aapka dream {symbols} ke symbols ko ek strong {emotion} emotional undercurrent ke saath weave karta hai.",
        'mid_positive': "In elements ki interaction aapke dream mein ek positive emotional state ko reflect karti hai.",
        'mid_negative': "In elements ki interaction aapke dream mein emotional challenge ke area ko reflect karti hai.",
        'mid_neutral': "In elements ki interaction observation aur balance ka phase suggest karti hai.",
        'closing': "Aapka subconscious aapke experiences ko process karne mein help karne ke liye in specific details ko highlight kar raha hai.",
        'no_elements': "Ye dream aapki current mental state ka reflection hai, jo primarily {emotion} tone se characterized hai.",
        'insight_fear': "Aapka mind sote waqt in anxieties ko safely process kar raha hai. Aapke paas in feelings ko navigate karne ki strength hai.",
        'insight_joy': "Aapka subconscious positivity ke ek moment ko capture kar raha hai. Is energy ko apne saath rakho.",
        'insight_sadness': "Apne aap ko in emotions ko process karne ki ijazat do. Ye dream emotional clarity ki direction mein ek step hai.",
        'insight_default': "In symbols par reflect karo jaise ye aapke dream mein appear hote hain. Aapka inner mind aapke daily experiences ko process kar raha hai."
    }
}


# Emotion categories
POSITIVE_EMOTIONS = {'joy', 'love', 'surprise'}
NEGATIVE_EMOTIONS = {'fear', 'sadness', 'anger'}
FEAR_THEMES = {'fear', 'anxiety', 'chase', 'falling', 'flood', 'spider', 'snake', 'darkness', 'exam', 'teeth_falling', 'late'}


PSYCHOLOGICAL_CONTEXT_RULES = [
    {
        'theme': 'career anxiety',
        'emotion': 'pressure',
        'triggers': ['job', 'career', 'office', 'work', 'promotion', 'deadline', 'interview', 'boss', 'performance', 'target', 'project'],
        'conflict': 'pressure to prove yourself professionally',
        'interpretation': 'The dream appears to carry career pressure rather than literal career content.',
    },
    {
        'theme': 'fear of failure',
        'emotion': 'self-doubt',
        'triggers': ['fail', 'failing', 'failed', 'mistake', 'error', 'blank', 'missing answer', 'unable', 'cannot', 'could not', 'test', 'exam'],
        'conflict': 'fear of not meeting your own standards',
        'interpretation': 'A failure-sensitive state is showing up as hesitation, blankness, or blocked recall.',
    },
    {
        'theme': 'fear of disappointing family',
        'emotion': 'approval anxiety',
        'triggers': ['parents', 'parent', 'mother', 'father', 'family', 'relatives', 'home', 'house'],
        'context': ['watching', 'silent', 'silently', 'judging', 'expect', 'expectation', 'disappointed', 'approval'],
        'conflict': 'fear of falling short of family expectations',
        'interpretation': 'Family figures in the dream are likely carrying the emotional weight of expectation, not just their literal presence.',
    },
    {
        'theme': 'responsibility pressure',
        'emotion': 'burden',
        'triggers': ['responsibility', 'duty', 'burden', 'rely', 'depending', 'need to', 'must', 'should', 'care for', 'support', 'provide'],
        'conflict': 'feeling responsible for more than you can comfortably hold',
        'interpretation': 'The dream suggests emotional load and duty are crowding out rest or ease.',
    },
    {
        'theme': 'fear of wasted potential',
        'emotion': 'regret',
        'triggers': ['wasted time', 'too late', 'waste', 'potential', 'missed', 'lost time', 'years', 'clock', 'deadline', 'aging', 'late'],
        'conflict': 'fear that time is slipping away before your potential is used',
        'interpretation': 'Time symbols and urgency cues point to anxiety about what has not yet been achieved.',
    },
    {
        'theme': 'identity conflict',
        'emotion': 'identity strain',
        'triggers': ['former', 'used to', 'old school', 'old college', 'trophy', 'award', 'rank', 'topper', 'high achiever', 'achievement', 'certificate'],
        'context': ['no longer', 'again', 'past', 'remember', 'compare'],
        'conflict': 'tension between your current self and a past high-achieving identity',
        'interpretation': 'Old achievements are being read as a comparison point, not simply as praise.',
    },
    {
        'theme': 'social comparison',
        'emotion': 'comparison anxiety',
        'triggers': ['others', 'everyone', 'classmate', 'peer', 'friends', 'ahead', 'behind', 'moving forward', 'left behind', 'compare', 'comparison'],
        'conflict': 'fear of being measured against people who seem further ahead',
        'interpretation': 'The dream is likely staging comparison pressure through other people moving and the dreamer feeling stuck.',
    },
    {
        'theme': 'analysis paralysis',
        'emotion': 'mental overload',
        'triggers': ['blank screen', 'empty screen', 'blank page', 'missing answer', 'can not decide', 'cannot decide', 'stuck', 'frozen', 'overthinking', 'choice', 'options'],
        'conflict': 'being mentally overloaded until action becomes difficult',
        'interpretation': 'Empty screens or missing answers point to blocked processing rather than lack of intelligence.',
    },
    {
        'theme': 'burnout and emotional exhaustion',
        'emotion': 'exhaustion',
        'triggers': ['exhausted', 'drained', 'tired', 'burnout', 'overwhelmed', 'cannot continue', 'too much', 'sleepy', 'empty', 'no energy'],
        'conflict': 'having too little emotional fuel left to keep up the pace',
        'interpretation': 'The dream reads like depletion, where even ordinary tasks feel heavy or slow.',
    },
    {
        'theme': 'self-doubt despite capability',
        'emotion': 'self-doubt',
        'triggers': ['capable', 'able', 'good at', 'qualified', 'still doubt', 'not good enough', 'imposter', 'insecure', 'can do'],
        'conflict': 'knowing you can do something while still doubting yourself',
        'interpretation': 'Capability exists in the dream, but confidence is not catching up to it.',
    },
    {
        'theme': 'procrastination and avoidance behavior',
        'emotion': 'avoidance',
        'triggers': ['scrolling', 'phone', 'distraction', 'avoid', 'delay', 'later', 'procrastinate', 'ignore', 'distracted'],
        'conflict': 'using distraction to postpone an uncomfortable task or feeling',
        'interpretation': 'Phone use or scrolling in the dream often signals emotional avoidance rather than casual behavior.',
    },
    {
        'theme': 'loss of former high-achiever identity',
        'emotion': 'identity grief',
        'triggers': ['top student', 'first rank', 'topper', 'gold medal', 'award', 'achievement', 'brilliant', 'high achiever'],
        'context': ['used to', 'past', 'former', 'not anymore', 'lost', 'again', 'behind'],
        'conflict': 'grieving the distance between who you were praised as and who you feel like now',
        'interpretation': 'The dream may be mourning a version of the self that once felt effortless and successful.',
    },
    {
        'theme': 'internalized expectations',
        'emotion': 'pressure',
        'triggers': ['should', 'must', 'need to', 'have to', 'expected', 'expectation', 'perfect', 'perfection', 'standard', 'prove'],
        'conflict': 'carrying expectations so deeply that they feel self-imposed',
        'interpretation': 'The pressure may be coming from an internal voice as much as from other people.',
    },
    {
        'theme': 'introversion-related isolation',
        'emotion': 'isolation',
        'triggers': ['alone', 'isolated', 'silent', 'quiet', 'cannot speak', 'invisible', 'left out', 'separated', 'crowd'],
        'context': ['while others', 'everyone else', 'surrounded'],
        'conflict': 'feeling emotionally present but socially disconnected',
        'interpretation': 'The dream suggests quiet distance from others rather than simple loneliness.',
    },
]


PSYCHOLOGICAL_TEMPLATES = {
    'en': {
        'intro': 'This dream is better read as an emotional pressure pattern than as a literal story.',
        'bridge': 'The strongest signals point to {themes}.',
        'family': 'Neutral or positive details such as family, school, work, or achievement are carrying the stress meaning in context.',
        'conflict': 'Core conflict: {conflict}.',
    },
    'hi': {
        'intro': 'यह सपना शाब्दिक कहानी से अधिक एक भावनात्मक दबाव-पैटर्न की तरह पढ़ा जाना चाहिए।',
        'bridge': 'सबसे मजबूत संकेत {themes} की ओर इशारा करते हैं।',
        'family': 'परिवार, स्कूल, काम या उपलब्धि जैसे तटस्थ/सकारात्मक विवरण संदर्भ में तनाव का अर्थ ले रहे हैं।',
        'conflict': 'मुख्य संघर्ष: {conflict}.',
    },
    'mr': {
        'intro': 'हे स्वप्न शब्दशः कथेपेक्षा भावनिक दडपणाच्या नमुन्यासारखे वाचावे.',
        'bridge': 'सर्वात मजबूत संकेत {themes} कडे निर्देश करतात.',
        'family': 'कुटुंब, शाळा, काम किंवा यश यांसारखे तटस्थ/सकारात्मक तपशील संदर्भात ताणाचा अर्थ धारण करत आहेत.',
        'conflict': 'मुख्य संघर्ष: {conflict}.',
    },
    'hinglish': {
        'intro': 'Ye dream literal story se zyada emotional pressure pattern ki tarah read hona chahiye.',
        'bridge': 'Strongest signals {themes} ki taraf point karte hain.',
        'family': 'Family, school, work, ya achievement jaise neutral/positive details context mein stress ka meaning carry kar rahe hain.',
        'conflict': 'Core conflict: {conflict}.',
    },
}

def interpret_dream(text, nlp_analysis, user_language='en'):
    """
    Generate a structured psychological interpretation with consistency checks.
    """
    # Detect language with fallback to user preference
    detected_lang, lang_conf, used_fallback = detect_with_fallback(text, user_language)
    interpretation_lang = detected_lang
    
    # Find symbols in the dream text
    found_symbols = find_symbols_in_text(text, interpretation_lang)
    
    # 0. Consistency & Polarity Reinforcement
    emo_data = nlp_analysis.get('emotion', {})
    primary_emotion = emo_data.get('primary_emotion', 'neutral')
    emo_confidence = emo_data.get('confidence', 0)
    
    sentiment_data = nlp_analysis.get('sentiment', {})
    sentiment_label = sentiment_data.get('sentiment')
    sent_confidence = sentiment_data.get('score', 0)
    
    # Calculate symbol-based counts and polarity
    symbol_score = 0
    symbol_emotions = {}
    for s in found_symbols:
        symbol_score += s.get('polarity', 0) * s.get('weight', 1)
        s_emo = s.get('emotion', 'neutral')
        symbol_emotions[s_emo] = symbol_emotions.get(s_emo, 0) + s.get('weight', 1)

    # HOUSE GUARD: Protection for literal dreams
    is_house_mention = any(h in text.lower() for h in ['home', 'house', 'ghar', '\u0918\u0930'])
    is_lone_house = is_house_mention and symbol_score < 0.5
    
    # EMOTION REINFORCEMENT
    final_emotion = primary_emotion
    if emo_confidence < 0.4 or primary_emotion == 'neutral' or (symbol_emotions.get(primary_emotion, 0) == 0 and symbol_emotions):
        if symbol_emotions and not is_lone_house:
            best_symbol_emo = max(symbol_emotions.items(), key=lambda x: x[1])[0]
            if best_symbol_emo != 'neutral' and symbol_emotions[best_symbol_emo] >= 2:
                final_emotion = best_symbol_emo

    # SENTIMENT REINFORCEMENT (The "Voting" System)
    final_sentiment = sentiment_label
    
    if not is_lone_house:
        # Rule 1: Joy/Love are powerful indicators. Force positive unless model is 98%+ sure of negative.
        if final_emotion in POSITIVE_EMOTIONS and final_sentiment != 'positive':
            if symbol_score >= -1 or sent_confidence < 0.98:
                final_sentiment = 'positive'

        # Rule 2: Symbols represent the core subconscious content. 
        # Strong positive symbols override Model's negative/neutral findings.
        if symbol_score >= 1.5 and final_sentiment != 'positive':
            if sent_confidence < 0.95:
                final_sentiment = 'positive'
        
        # Rule 3: Scary/Negative symbols are critical warnings. 
        # Override positive/neutral if any strong negative symbols are present.
        if symbol_score <= -1.5 and final_sentiment != 'negative':
            if sent_confidence < 0.95:
                final_sentiment = 'negative'
    
    # Rule 4: Handle "Neutral" correctly
    # If the transformer is low/mid confidence and primary emotion is neutral, force neutral
    if final_emotion == 'neutral' and final_sentiment != 'neutral':
        if sent_confidence < 0.85 and abs(symbol_score) < 1.0:
            final_sentiment = 'neutral'
            
    # Lone House Final Force
    if is_lone_house and abs(symbol_score) < 0.5:
        final_emotion = 'neutral'
        final_sentiment = 'neutral'
    
    # IMPORTANT: Update nlp_analysis in-place so nlp_engine returns reinforced labels
    emo_data['primary_emotion'] = final_emotion
    nlp_analysis['emotion'] = emo_data
    sentiment_data['sentiment'] = final_sentiment
    nlp_analysis['sentiment'] = sentiment_data
            
    # STRICT SYMBOL VERIFICATION (STRICT MODE)
    # Remove any symbol that is not explicitly found as a keyword (substring) in the original text
    original_text_lower = text.lower()
    verified_symbols = []
    for s in found_symbols:
        keyword = s['keyword'].lower()
        # Verify if the literal keyword or its lemma exists in the text
        if keyword in original_text_lower:
            verified_symbols.append(s)
    
    found_symbols = verified_symbols
    
    # Sort by weight
    found_symbols.sort(key=lambda x: (x.get('weight', 1), len(x['keyword'])), reverse=True)
    
    # Extract elements from NLP analysis
    keywords = nlp_analysis.get('keywords', [])
    
    # Build numbered elements from the extracted dream keywords.
    # If a keyword matches the dream symbol database, use that symbol's meaning and interpretation.
    numbered_elements = []
    seen_elements = set()
    for keyword in keywords:
        if len(numbered_elements) >= 5:
            break

        normalized_keyword = keyword.lower().strip()
        if not normalized_keyword or normalized_keyword in seen_elements:
            continue

        if normalized_keyword not in original_text_lower:
            continue

        seen_elements.add(normalized_keyword)
        symbol_match = resolve_keyword_symbol(keyword, interpretation_lang)

        if symbol_match:
            numbered_elements.append({
                'number': len(numbered_elements) + 1,
                'element': keyword.capitalize(),
                'symbolic_meaning': symbol_match['meaning'],
                'subconscious_insight': symbol_match['interpretation'],
                'weight': symbol_match.get('weight', 1),
                'emotion': symbol_match.get('emotion', 'neutral'),
                'symbol_key': symbol_match.get('symbol')
            })
        else:
            numbered_elements.append({
                'number': len(numbered_elements) + 1,
                'element': keyword.capitalize(),
                'symbolic_meaning': _get_generic_meaning(interpretation_lang),
                'subconscious_insight': _get_generic_insight(interpretation_lang),
                'weight': 1,
                'emotion': 'neutral'
            })

    # If keywords were empty or no usable matches were found, fall back to verified symbols.
    if not numbered_elements:
        for symbol_data in found_symbols[:5]:
            numbered_elements.append({
                'number': len(numbered_elements) + 1,
                'element': symbol_data['keyword'].capitalize(),
                'symbolic_meaning': symbol_data['meaning'],
                'subconscious_insight': symbol_data['interpretation'],
                'weight': symbol_data.get('weight', 1),
                'emotion': symbol_data.get('emotion', 'neutral'),
                'symbol_key': symbol_data.get('symbol')
            })
    
    overall_interpretation = _generate_overall_interpretation(
        numbered_elements, final_emotion, final_sentiment, keywords, interpretation_lang
    )

    psychological_context = _generate_psychological_context(
        text,
        keywords,
        numbered_elements,
        final_emotion,
        final_sentiment,
        interpretation_lang,
    )
    
    # Generate final insight
    final_insight = _generate_final_insight(final_emotion, interpretation_lang)
    
    return {
        'numbered_elements': numbered_elements,
        'overall_interpretation': overall_interpretation,
        'psychological_emotions': psychological_context['psychological_emotions'],
        'psychological_themes': psychological_context['psychological_themes'],
        'core_conflict': psychological_context['core_conflict'],
        'psychological_interpretation': psychological_context['psychological_interpretation'],
        'final_insight': final_insight,
        'detected_language': detected_lang,
        'language_confidence': lang_conf,
        'interpretation_language': interpretation_lang
    }


def _get_generic_meaning(lang_code):
    """Get professional generic meaning for non-symbol keywords."""
    meanings = {
        'en': "This element represents a focal point of your subconscious attention, acting as a bridge between your internal thoughts and outward reality.",
        'hi': "यह तत्व आपके अवचेतन ध्यान के एक केंद्र बिंदु का प्रतिनिधित्व करता है, जो आपके आंतरिक विचारों और बाहरी वास्तविकता के बीच एक सेतु के रूप में कार्य करता है।",
        'mr': "हा घटक तुमच्या सुप्त मनाच्या एका केंद्रबिंदूचे प्रतिनिधित्व करतो, जो तुमच्या अंतर्गत विचारांना आणि बाह्य वास्तवाला जोडणारा दुवा म्हणून काम करतो.",
        'hinglish': "Ye element aapke subconscious dhyan ka ek focal point represent karta hai, jo aapke internal thoughts aur reality ke beech ek bridge ki tarah kaam karta hai."
    }
    return meanings.get(lang_code, meanings['en'])


def _get_generic_insight(lang_code):
    """Get professional generic insight for non-symbol keywords."""
    insights = {
        'en': "The appearance of this detail suggests that your mind is organizing impressions from your daily life into a meaningful psychological pattern.",
        'hi': "इस विवरण की उपस्थिति बताती है कि आपका मन आपके दैनिक जीवन के प्रभावों को एक सार्थक मनोवैज्ञानिक पैटर्न में व्यवस्थित कर रहा है।",
        'mr': "या तपशीलाचे स्वरूप सूचित करते की तुमचे मन तुमच्या दैनंदिन जीवनातील छापांना एका अर्थपूर्ण मनोवैज्ञानिक नमुन्यात व्यवस्थित करत आहे.",
        'hinglish': "Is detail ka dikhna suggest karta hai ki aapka mind daily life ke impressions ko ek meaningful psychological pattern mein organize kar raha hai."
    }
    return insights.get(lang_code, insights['en'])


def _generate_overall_interpretation(elements, emotion, sentiment, keywords, lang_code):
    """Combine analysis into a specific context-aware narrative."""
    templates = INTERPRETATION_TEMPLATES.get(lang_code, INTERPRETATION_TEMPLATES['en'])
    
    keywords_set = set([k.lower() for k in keywords])
    
    if not elements:
        return templates['no_elements'].format(emotion=emotion)
    
    # Get symbol names for intro
    primary_symbols = ", ".join([e['element'].lower() for e in elements[:2]])
    intro = templates['intro'].format(symbols=primary_symbols, emotion=emotion)
    
    # conflict context detection
    has_fear_context = any(kw in FEAR_THEMES for kw in keywords_set) or \
                      any(e.get('emotion') == 'fear' for e in elements)
    
    # Core Logic for section selection
    if emotion in POSITIVE_EMOTIONS and not has_fear_context:
        mid = templates['mid_positive']
    elif emotion in NEGATIVE_EMOTIONS or has_fear_context:
        mid = templates['mid_negative']
    elif sentiment == 'positive':
        mid = templates['mid_positive']
    elif sentiment == 'negative':
        mid = templates['mid_negative']
    else:
        mid = templates['mid_neutral']
    
    # Ensure interpretation is never empty or "weak"
    narrative = f"{intro} {mid} {templates['closing']}"
    if len(narrative) < 100: # Extra padding for completeness
         narrative += f" {templates['intro'].split('{symbols}')[0].strip()} elements often surface during times of mental processing."
         
    return narrative


def _generate_final_insight(emotion, lang_code):
    """Create a gentle reflective message in the specified language."""
    templates = INTERPRETATION_TEMPLATES.get(lang_code, INTERPRETATION_TEMPLATES['en'])
    
    if emotion == 'fear':
        return templates['insight_fear']
    elif emotion == 'joy' or emotion == 'love':
        return templates['insight_joy']
    elif emotion == 'sadness':
        return templates['insight_sadness']
    else:
        return templates['insight_default']


def _generate_psychological_context(text, keywords, elements, emotion, sentiment, lang_code):
    """Detect psychologically meaningful dream themes without changing existing analysis outputs."""
    text_lower = text.lower()
    keyword_blob = " ".join((keywords or [])).lower()
    element_blob = " ".join(e.get('element', '') for e in (elements or [])).lower()
    combined_text = f"{text_lower} {keyword_blob} {element_blob}"

    matches = []
    for rule in PSYCHOLOGICAL_CONTEXT_RULES:
        base_hits = sum(1 for trigger in rule.get('triggers', []) if trigger in combined_text)
        if base_hits == 0:
            continue

        score = float(base_hits)
        if any(ctx in combined_text for ctx in rule.get('context', [])):
            score += 1.0

        if rule['theme'] == 'fear of disappointing family' and any(family_term in combined_text for family_term in ['parents', 'parent', 'mother', 'father', 'family']) and any(watching_term in combined_text for watching_term in ['watching', 'silent', 'silently', 'judging', 'expect']):
            score += 1.5

        if rule['theme'] == 'social comparison' and any(move_term in combined_text for move_term in ['ahead', 'behind', 'left behind', 'moving forward', 'everyone else']):
            score += 1.0

        if rule['theme'] == 'analysis paralysis' and any(block_term in combined_text for block_term in ['blank', 'empty', 'missing answer', 'stuck', 'frozen']):
            score += 1.0

        if rule['theme'] == 'burnout and emotional exhaustion' and any(exhaust_term in combined_text for exhaust_term in ['tired', 'drained', 'overwhelmed', 'no energy', 'sleepy']):
            score += 1.0

        matches.append({
            'theme': rule['theme'],
            'emotion': rule['emotion'],
            'conflict': rule['conflict'],
            'interpretation': rule['interpretation'],
            'score': score,
        })

    if not matches:
        default_conflict = {
            'en': 'the mind is processing pressure, uncertainty, or unresolved expectations',
            'hi': 'मन दबाव, अनिश्चितता, या अधूरी अपेक्षाओं को संसाधित कर रहा है',
            'mr': 'मन दडपण, अनिश्चितता किंवा अपूर्ण अपेक्षा प्रक्रिया करत आहे',
            'hinglish': 'mind pressure, uncertainty, ya unresolved expectations process kar raha hai',
        }
        return {
            'psychological_emotions': [emotion] if emotion else [],
            'psychological_themes': [],
            'core_conflict': default_conflict.get(lang_code, default_conflict['en']),
            'psychological_interpretation': _fallback_psychological_interpretation(lang_code, emotion, sentiment),
        }

    matches.sort(key=lambda item: (item['score'], len(item['theme'])), reverse=True)
    top_matches = matches[:4]

    psychological_themes = [item['theme'] for item in top_matches]
    psychological_emotions = []
    for item in top_matches:
        if item['emotion'] not in psychological_emotions:
            psychological_emotions.append(item['emotion'])

    strongest = top_matches[0]
    templates = PSYCHOLOGICAL_TEMPLATES.get(lang_code, PSYCHOLOGICAL_TEMPLATES['en'])
    theme_text = ", ".join(psychological_themes[:3])
    interpretation_parts = [
        templates['intro'],
        templates['bridge'].format(themes=theme_text),
        templates['family'],
        templates['conflict'].format(conflict=strongest['conflict'])
    ]

    return {
        'psychological_emotions': psychological_emotions,
        'psychological_themes': psychological_themes,
        'core_conflict': strongest['conflict'],
        'psychological_interpretation': " ".join(part for part in interpretation_parts if part),
    }


def _fallback_psychological_interpretation(lang_code, emotion, sentiment):
    templates = PSYCHOLOGICAL_TEMPLATES.get(lang_code, PSYCHOLOGICAL_TEMPLATES['en'])
    if emotion in ['fear', 'sadness', 'anger'] or sentiment == 'negative':
        conflict = {
            'en': 'anxiety, pressure, or self-protection needs are driving the dream',
            'hi': 'चिंता, दबाव, या आत्म-सुरक्षा की ज़रूरतें इस सपने को चला रही हैं',
            'mr': 'चिंता, दडपण किंवा आत्म-संरक्षणाची गरज हे स्वप्न चालवत आहेत',
            'hinglish': 'anxiety, pressure, ya self-protection needs is dream ko drive kar rahi hain',
        }
    else:
        conflict = {
            'en': 'the mind is organizing everyday pressure into a symbolic story',
            'hi': 'मन रोज़मर्रा के दबाव को प्रतीकात्मक कहानी में व्यवस्थित कर रहा है',
            'mr': 'मन रोजच्या दडपणाला प्रतीकात्मक कथेत मांडत आहे',
            'hinglish': 'mind everyday pressure ko symbolic story mein organize kar raha hai',
        }
    conflict_text = conflict.get(lang_code, conflict['en'])
    return f"{templates['intro']} {templates['conflict'].format(conflict=conflict_text)}"
