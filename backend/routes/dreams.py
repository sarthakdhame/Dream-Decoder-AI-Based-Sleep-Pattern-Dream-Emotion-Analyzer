"""
Dream Decoder - Dream Routes
API endpoints for dream CRUD operations
"""
import os
import re
from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.models.dream import Dream
from backend.models.sleep import SleepRecord
from backend.services.dream_symbols import resolve_keyword_symbol
from backend.services.nlp_engine import analyze_dream
from backend.services.jungian_analyzer import analyze_jungian
from backend.services.sleep_analyzer import SleepAnalyzer
from backend.middleware.auth import require_auth

dreams_bp = Blueprint('dreams', __name__)
sleep_analyzer = SleepAnalyzer()


def _fallback_analysis(content, user_language):
    """
    Return smart basic analysis when ML models are unavailable.
    Extracts important words and detects sentiment from text directly.
    """
    import re
    text_lower = content.lower()
    
    # Extended dream keyword vocabulary
    dream_keywords = [
        'falling', 'flying', 'chased', 'running', 'trapped', 'lost', 'water', 'death',
        'school', 'exam', 'test', 'monster', 'ghost', 'dark', 'house', 'car', 'crash',
        'family', 'friend', 'baby', 'animal', 'fire', 'snake', 'chase', 'fear', 'scared',
        'forest', 'mountain', 'ocean', 'sky', 'city', 'road', 'door', 'room', 'stairs',
        'war', 'battle', 'fight', 'climb', 'swim', 'jump', 'fall', 'sleep', 'wake'
    ]

    # Single keyword extraction pass using weighted candidates.
    stop_words = {'the', 'and', 'was', 'with', 'from', 'were', 'been', 'have', 'that', 'this', 'have', 'what', 'when', 'where', 'which', 'could', 'would', 'should'}
    words = re.findall(r'\b\w+\b', text_lower)
    dream_keyword_set = set(dream_keywords)
    keyword_scores = {}

    for word in words:
        if len(word) >= 4 and word not in stop_words:
            # Prioritize curated dream vocabulary and then frequency.
            keyword_scores[word] = keyword_scores.get(word, 0) + (3 if word in dream_keyword_set else 1)

    ranked_keywords = sorted(keyword_scores.items(), key=lambda x: (-x[1], -len(x[0])))
    final_keywords = [word for word, _ in ranked_keywords[:8]]
    
    # If still empty, use general dream categories
    if not final_keywords:
        final_keywords = ['dream', 'sleep', 'night']
    
    # Comprehensive sentiment detection
    negative_words = {
        'scary': 2, 'afraid': 2, 'terror': 3, 'dangerous': 2, 'death': 2, 'dying': 2, 'monster': 2,
        'ghost': 1, 'fear': 2, 'dark': 1, 'nightmare': 3, 'threat': 2, 'attack': 2, 'hurt': 2,
        'pain': 2, 'sad': 2, 'angry': 2, 'fail': 2, 'lost': 1, 'trapped': 2, 'chase': 1,
        'running': 1, 'falling': 1, 'hurt': 2, 'bad': 1, 'wrong': 1, 'broken': 1
    }
    positive_words = {
        'happy': 2, 'joy': 3, 'love': 2, 'beautiful': 2, 'wonderful': 3, 'amazing': 3, 'flying': 1,
        'light': 1, 'peace': 2, 'calm': 2, 'safe': 2, 'friend': 1, 'success': 2, 'good': 1,
        'great': 1, 'smile': 2, 'laugh': 2, 'win': 2, 'found': 1, 'free': 1, 'easy': 1
    }
    
    neg_score = sum(weight for word, weight in negative_words.items() if word in text_lower)
    pos_score = sum(weight for word, weight in positive_words.items() if word in text_lower)
    
    if neg_score > pos_score:
        sentiment = 'negative'
        if 'fear' in text_lower or 'scary' in text_lower or 'nightmare' in text_lower or 'monster' in text_lower:
            primary_emotion = 'fear'
        elif 'angry' in text_lower or 'fight' in text_lower or 'attack' in text_lower:
            primary_emotion = 'anger'
        else:
            primary_emotion = 'sadness'
        sentiment_score = -0.6 - min(0.3, neg_score / 10)
    elif pos_score > neg_score:
        sentiment = 'positive'
        primary_emotion = 'joy'
        sentiment_score = 0.6 + min(0.3, pos_score / 10)
    else:
        sentiment = 'neutral'
        primary_emotion = 'neutral'
        sentiment_score = 0.0

    # Provide multi-emotion output so UI charts and summaries are never empty.
    if primary_emotion == 'fear':
        emotion_scores = {'fear': 0.72, 'sadness': 0.44, 'surprise': 0.31}
    elif primary_emotion == 'anger':
        emotion_scores = {'anger': 0.69, 'fear': 0.38, 'disgust': 0.33}
    elif primary_emotion == 'sadness':
        emotion_scores = {'sadness': 0.67, 'fear': 0.34, 'neutral': 0.28}
    elif primary_emotion == 'joy':
        emotion_scores = {'joy': 0.71, 'trust': 0.45, 'anticipation': 0.32}
    else:
        emotion_scores = {'neutral': 0.62, 'anticipation': 0.24, 'trust': 0.22}
    
    # Generate numbered elements with symbolic meanings for fallback analysis
    numbered_elements = []
    for idx, keyword in enumerate(final_keywords[:5], 1):
        symbol_match = resolve_keyword_symbol(keyword, user_language)
        if symbol_match:
            numbered_elements.append({
                'number': idx,
                'element': keyword.capitalize(),
                'symbolic_meaning': symbol_match.get('meaning', 'No symbolic meaning available.'),
                'subconscious_insight': symbol_match.get('interpretation', 'No subconscious insight available.'),
                'weight': symbol_match.get('weight', 1),
                'emotion': symbol_match.get('emotion', 'neutral'),
                'symbol_key': symbol_match.get('symbol')
            })
        else:
            numbered_elements.append({
                'number': idx,
                'element': keyword.capitalize(),
                'symbolic_meaning': 'This element represents a focal point of subconscious attention.',
                'subconscious_insight': 'The appearance of this detail suggests that your mind is organizing impressions into a meaningful psychological pattern.',
                'weight': 1,
                'emotion': 'neutral'
            })
    
    return {
        'sentiment': sentiment,
        'sentiment_score': sentiment_score,
        'primary_emotion': primary_emotion,
        'emotion_scores': emotion_scores,
        'keywords': final_keywords,
        'entities': [],
        'themes': ['nightmare' if sentiment == 'negative' else 'peaceful' if sentiment == 'positive' else 'ordinary'],
        'categories': ['nightmare' if 'monster' in final_keywords or 'chase' in final_keywords else 'ordinary'],
        'summary': f'This dream has a {sentiment} tone with themes of {", ".join(final_keywords[:3])}. Key symbols suggest ongoing emotional processing during sleep.',
        'interpretation': {
            'overall_message': 'Analysis based on text pattern recognition. Full ML analysis unavailable.',
            'emotional_pattern': f"Primary emotion appears to be {primary_emotion} with a {sentiment} polarity ({sentiment_score:.2f}).",
            'symbolic_focus': f"Most recurrent symbols: {', '.join(final_keywords[:4])}.",
            'guidance': 'Consider journaling what happened before sleep and any real-life events connected to these symbols.',
            'numbered_elements': numbered_elements
        },
        'emotion_confidence': 0.6,
        'detected_language': user_language,
        'language_confidence': 0.9,
    }


def _generate_local_jungian_report(content, analysis):
    """Create a structured Jungian-style report when external AI is unavailable."""
    keywords = analysis.get('keywords', [])[:5]
    primary_emotion = analysis.get('primary_emotion', 'neutral')
    sentiment = analysis.get('sentiment', 'neutral')

    symbol_text = ', '.join(keywords) if keywords else 'journey, self, transition'
    archetypes = []
    lowered = content.lower()

    if any(token in lowered for token in ('monster', 'shadow', 'dark', 'chase', 'fear')):
        archetypes.append('Shadow')
    if any(token in lowered for token in ('friend', 'mother', 'father', 'family', 'guide')):
        archetypes.append('Persona/Relational Self')
    if any(token in lowered for token in ('house', 'room', 'door', 'road', 'forest', 'mountain')):
        archetypes.append('Self (inner landscape)')
    if not archetypes:
        archetypes = ['Self', 'Shadow']

    emotional_insight = (
        f"The dream carries a {sentiment} tone with {primary_emotion} as the dominant affect. "
        "This usually reflects unresolved emotional material surfacing during sleep for integration."
    )

    growth_message = (
        "Track repeating symbols across 3-5 dreams and connect them to recent waking-life stressors, "
        "relationships, and decisions. Repeated symbols often indicate a psychological theme ready for conscious work."
    )

    return (
        "Title: Jungian Interpretation\n\n"
        f"1. Symbols Meaning: The recurring symbols ({symbol_text}) suggest a movement between safety and uncertainty, "
        "often representing internal conflict, adaptation, and identity processing.\n\n"
        f"2. Archetypes Identified: {', '.join(archetypes)}. These archetypes indicate active dialogue between conscious choices "
        "and unconscious fears/desires.\n\n"
        f"3. Emotional Insight: {emotional_insight}\n\n"
        f"4. Personal Growth Message: {growth_message}"
    )


def _trim_section_text(text, max_chars=650):
    """Trim section text while preserving sentence boundaries when possible."""
    if not text:
        return ''
    cleaned = ' '.join(str(text).strip().split())
    if len(cleaned) <= max_chars:
        return cleaned

    clipped = cleaned[:max_chars].rstrip()
    # Prefer ending on sentence punctuation rather than hard-cut.
    sentence_end = max(clipped.rfind('. '), clipped.rfind('! '), clipped.rfind('? '))
    if sentence_end >= max_chars // 2:
        return clipped[:sentence_end + 1].strip()
    return clipped + '...'


def _build_essential_jungian_report(raw_text, analysis):
    """Return a consistent 4-point Jungian report so key sections are never missing."""
    keywords = (analysis or {}).get('keywords', [])[:5]
    interpretation = (analysis or {}).get('interpretation') or {}
    interpreted_elements = interpretation.get('numbered_elements') if isinstance(interpretation, dict) else []
    primary_emotion = (analysis or {}).get('primary_emotion', 'neutral')
    sentiment = (analysis or {}).get('sentiment', 'neutral')

    symbol_text = ', '.join(keywords) if keywords else 'journey, self, transition'

    keyword_lines = []
    if isinstance(interpreted_elements, list) and interpreted_elements:
        for element in interpreted_elements[:5]:
            element_name = element.get('element') or element.get('keyword') or 'Unknown'
            symbolic_meaning = element.get('symbolic_meaning') or 'No symbolic meaning available.'
            subconscious_insight = element.get('subconscious_insight') or 'No subconscious insight available.'
            keyword_lines.append(
                f"- {element_name}: Symbolic Meaning: {symbolic_meaning} | Subconscious Insight: {subconscious_insight}"
            )
    else:
        for keyword in keywords[:5]:
            symbol_match = resolve_keyword_symbol(keyword)
            if symbol_match:
                keyword_lines.append(
                    f"- {keyword.capitalize()}: Symbolic Meaning: {symbol_match.get('meaning', 'No symbolic meaning available.')} | Subconscious Insight: {symbol_match.get('interpretation', 'No subconscious insight available.')}"
                )
            else:
                keyword_lines.append(
                    f"- {keyword.capitalize()}: Symbolic Meaning: This element represents a focal point of subconscious attention. | Subconscious Insight: The appearance of this detail suggests that your mind is organizing impressions into a meaningful psychological pattern."
                )

    defaults = {
        1: f"The recurring symbols ({symbol_text}) suggest active subconscious processing around identity, control, and adaptation.",
        2: "Likely active archetypes include the Self, Persona, and Shadow, reflecting tension between social identity and inner emotional truth.",
        3: f"The dream carries a {sentiment} tone with {primary_emotion} as the dominant emotional signal, indicating unresolved emotional material seeking integration.",
        4: "Track repeating symbols across multiple dreams, connect them with current life stressors, and use reflective journaling to convert dream insight into action."
    }

    extracted = {}
    text = (raw_text or '').replace('\r\n', '\n').strip()
    if text:
        for idx in range(1, 5):
            pattern = rf"{idx}\.\s*[^:]*:\s*(.*?)(?=(?:\n\s*[1-4]\.\s*[^:]*:)|\Z)"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                extracted[idx] = _trim_section_text(match.group(1))

    sections = {
        1: extracted.get(1) or defaults[1],
        2: extracted.get(2) or defaults[2],
        3: extracted.get(3) or defaults[3],
        4: extracted.get(4) or defaults[4],
    }

    keyword_section = '\n'.join(keyword_lines) if keyword_lines else '- No keyword-level symbolic matches were identified.'

    return (
        "Title: Jungian Interpretation\n\n"
        f"1. Symbols Meaning: {sections[1]}\n\n"
        f"2. Archetypes Identified: {sections[2]}\n\n"
        f"3. Emotional Insight: {sections[3]}\n\n"
        f"4. Personal Growth Message: {sections[4]}\n\n"
        f"5. Keyword Symbolic Meanings and Subconscious Insights:\n{keyword_section}"
    )


def _compact_report_for_list(dream_dict, max_report_chars=1800):
    """Reduce payload size for list APIs while preserving preview-ready report content."""
    report = dream_dict.get('jungian_report') or {}
    analysis_text = report.get('analysis') if isinstance(report, dict) else None
    if isinstance(analysis_text, str) and len(analysis_text) > max_report_chars:
        compact = dict(report)
        compact['analysis'] = analysis_text[:max_report_chars] + '...'
        dream_dict['jungian_report'] = compact
    return dream_dict


def _compute_duration_hours(sleep_time, wake_time):
    """Compute duration in hours, handling overnight sleep windows."""
    if not sleep_time or not wake_time:
        return None

    sleep_dt = datetime.strptime(sleep_time, "%H:%M")
    wake_dt = datetime.strptime(wake_time, "%H:%M")
    if wake_dt <= sleep_dt:
        wake_dt = wake_dt.replace(day=wake_dt.day + 1)
    return (wake_dt - sleep_dt).total_seconds() / 3600.0


def _should_use_fallback_only():
    """Use fallback-only mode on Render unless explicitly disabled."""
    heavy_nlp_enabled = os.getenv('ENABLE_HEAVY_NLP', '').strip().lower() in ('1', 'true', 'yes', 'on')
    running_on_render = bool(os.getenv('RENDER'))
    return running_on_render and not heavy_nlp_enabled


@dreams_bp.route('/api/dreams', methods=['POST'])
@require_auth
def create_dream():
    """Create a new dream entry with NLP analysis."""
    try:
        user = request.current_user
        data = request.get_json()
        print(f"DEBUG: Received dream data from user {user.username}: {ascii(data)}")
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Dream content is required'}), 400
        
        content = data['content'].strip()
        if not content:
            return jsonify({'error': 'Dream content cannot be empty'}), 400
        
        # Optional metadata for richer journal flow
        dream_date = data.get('dream_date')
        dream_time = data.get('dream_time')
        sleep_data_input = data.get('sleep_data') if isinstance(data.get('sleep_data'), dict) else None

        # Get user's language preference
        user_language = user.language_preference or 'en'
        
        # Perform NLP analysis with language preference
        print(f"DEBUG: Starting NLP analysis in language: {user_language}...")
        if _should_use_fallback_only():
            print("INFO: Render safe mode active. Using fallback analysis.")
            analysis = _fallback_analysis(content, user_language)
        else:
            try:
                analysis = analyze_dream(content, user_language=user_language)
                print("DEBUG: NLP analysis complete.")
            except Exception as nlp_err:
                # Do not fail dream creation if NLP models/services are unavailable.
                print(f"WARNING: NLP analysis failed, using fallback analysis: {nlp_err}")
                analysis = _fallback_analysis(content, user_language)

        # Generate Jungian psychology report for this dream and store it with the dream record.
        jungian_report = {}
        try:
            jungian_result = analyze_jungian(content)
            if 'error' in jungian_result:
                local_report = _generate_local_jungian_report(content, analysis)
                jungian_report = {
                    'analysis': _build_essential_jungian_report(local_report, analysis),
                    'raw_analysis': local_report,
                    'provider': 'Unavailable',
                    'status': 'error',
                    'generated_at': datetime.utcnow().isoformat(),
                    'fallback_reason': jungian_result['error']
                }
            else:
                raw_analysis = jungian_result.get('analysis', '')
                jungian_report = {
                    'analysis': _build_essential_jungian_report(raw_analysis, analysis),
                    'raw_analysis': raw_analysis,
                    'provider': jungian_result.get('provider', 'Google Gemini'),
                    'status': 'ready',
                    'generated_at': datetime.utcnow().isoformat()
                }
        except Exception as jungian_err:
            print(f"WARNING: Jungian analysis skipped due to error: {jungian_err}")
            local_report = _generate_local_jungian_report(content, analysis)
            jungian_report = {
                'analysis': _build_essential_jungian_report(local_report, analysis),
                'raw_analysis': local_report,
                'provider': 'Unavailable',
                'status': 'error',
                'generated_at': datetime.utcnow().isoformat(),
                'fallback_reason': str(jungian_err)
            }
        
        # Create dream object with user_id
        print("DEBUG: Creating Dream object...")
        dream = Dream(
            user_id=user.id,
            content=content,
            sentiment=analysis['sentiment'],
            sentiment_score=analysis['sentiment_score'],
            primary_emotion=analysis['primary_emotion'],
            emotion_scores=analysis['emotion_scores'],
            keywords=analysis['keywords'],
            entities=analysis['entities'],
            interpretation=analysis.get('interpretation', {}),
            jungian_report=jungian_report
        )
        
        # Save to database
        print("DEBUG: Saving to database...")
        dream.save()
        print(f"DEBUG: Saved dream with ID: {dream.id}")
        
        # Return dream with analysis
        response = dream.to_dict()
        response['analysis'] = {
            'themes': analysis['themes'],
            'summary': analysis['summary'],
            'emotion_confidence': analysis.get('emotion_confidence', 0),
            'detected_language': analysis.get('detected_language', user_language),
            'language_confidence': analysis.get('language_confidence', 0)
        }

        if dream_date:
            response['dream_date'] = dream_date
        if dream_time:
            response['dream_time'] = dream_time

        # Optional sleep-based scoring tied to this dream entry
        if sleep_data_input:
            try:
                sleep_time = sleep_data_input.get('sleep_time')
                wake_time = sleep_data_input.get('wake_time')

                duration_hours = sleep_data_input.get('duration_hours')
                if duration_hours in (None, ''):
                    duration_hours = _compute_duration_hours(sleep_time, wake_time)

                if duration_hours is not None:
                    duration_hours = float(duration_hours)

                sleep_payload = {
                    'duration_hours': duration_hours if duration_hours is not None else 7.0,
                    'quality_rating': int(sleep_data_input.get('quality_rating', 5) or 5),
                    'interruptions': int(sleep_data_input.get('interruptions', sleep_data_input.get('wakeups', 0)) or 0),
                    'sleep_time': sleep_time or '23:00',
                    'wake_time': wake_time or '06:30',
                }

                sleep_quality_result = sleep_analyzer.calculate_sleep_quality(sleep_payload)
                disturbance = sleep_analyzer.predict_sleep_disturbance(analysis.get('emotion_scores', {}))

                response['analysis']['sleep'] = {
                    'quality': sleep_quality_result,
                    'disturbance': disturbance,
                }

                # If sufficient fields exist, also persist an associated sleep log entry.
                if sleep_data_input.get('date') and duration_hours is not None:
                    sleep_record = SleepRecord(
                        user_id=user.id,
                        date=sleep_data_input.get('date'),
                        sleep_time=sleep_time,
                        wake_time=wake_time,
                        duration_hours=duration_hours,
                        wakeups=sleep_payload['interruptions'],
                        quality_rating=sleep_payload['quality_rating'],
                        notes=sleep_data_input.get('notes', '')
                    )
                    sleep_record.save()
            except Exception as sleep_err:
                # Sleep scoring should not block dream saving.
                print(f"WARNING: sleep analysis skipped due to error: {sleep_err}")
        
        print("DEBUG: Returning successful response.")
        return jsonify(response), 201
    except Exception as e:
        import traceback
        print(f"ERROR in create_dream: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An internal error occurred during dream analysis'}), 500


@dreams_bp.route('/api/dreams', methods=['GET'])
@require_auth
def get_dreams():
    """Get all dreams for the authenticated user with optional pagination."""
    try:
        user = request.current_user
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        include_compact_report = request.args.get('include_compact_report', '0') in ('1', 'true', 'yes')

        # Validation
        if limit < 1 or limit > 100:
            limit = 50
        if offset < 0:
            offset = 0

        dreams = Dream.get_all(user.id, limit=limit, offset=offset)
        total = Dream.count(user.id)

        dream_items = [d.to_dict() for d in dreams]
        if include_compact_report:
            dream_items = [_compact_report_for_list(item) for item in dream_items]

        return jsonify({
            'dreams': dream_items,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        import traceback
        print(f"ERROR in get_dreams: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch dreams'}), 500


@dreams_bp.route('/api/dreams/reports', methods=['GET'])
@require_auth
def get_jungian_reports():
    """Get compact dream entries that include Jungian reports for journal view."""
    try:
        user = request.current_user
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        if limit < 1 or limit > 100:
            limit = 50
        if offset < 0:
            offset = 0

        dreams = Dream.get_all(user.id, limit=limit, offset=offset)
        items = []
        for dream in dreams:
            d = dream.to_dict()
            report = d.get('jungian_report') or {}
            if isinstance(report, dict) and report.get('analysis'):
                compact = {
                    'id': d.get('id'),
                    'content': d.get('content'),
                    'created_at': d.get('created_at'),
                    'jungian_report': report
                }
                items.append(compact)

        return jsonify({
            'dreams': items,
            'count': len(items),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        import traceback
        print(f"ERROR in get_jungian_reports: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch Jungian reports'}), 500


@dreams_bp.route('/api/dreams/<int:dream_id>', methods=['GET'])
def get_dream(dream_id):
    """Get a specific dream by ID."""
    dream = Dream.get_by_id(dream_id)
    
    if not dream:
        return jsonify({'error': 'Dream not found'}), 404
    
    return jsonify(dream.to_dict())


@dreams_bp.route('/api/dreams/<int:dream_id>', methods=['DELETE'])
@require_auth
def delete_dream(dream_id):
    """Delete a dream by ID for the authenticated user."""
    user = request.current_user
    dream = Dream.get_by_id(dream_id)

    if not dream or dream.user_id != user.id:
        return jsonify({'error': 'Dream not found or unauthorized'}), 404

    deleted = Dream.delete(dream_id)
    
    if not deleted:
        return jsonify({'error': 'Dream not found'}), 404
    
    return jsonify({'message': 'Dream deleted successfully'})


@dreams_bp.route('/api/dreams/<int:dream_id>/jungian-report', methods=['DELETE'])
@require_auth
def delete_jungian_report(dream_id):
    """Delete only the Jungian analysis report for a dream."""
    user = request.current_user
    dream = Dream.get_by_id(dream_id)

    if not dream or dream.user_id != user.id:
        return jsonify({'error': 'Dream not found or unauthorized'}), 404

    deleted = Dream.clear_jungian_report(dream_id, user.id)

    if not deleted:
        return jsonify({'error': 'Failed to delete Jungian analysis'}), 500

    return jsonify({'message': 'Jungian analysis deleted successfully'})


@dreams_bp.route('/api/dreams/recent', methods=['GET'])
@require_auth
def get_recent_dreams():
    """Get dreams from the last N days for the authenticated user."""
    user = request.current_user
    days = request.args.get('days', 7, type=int)
    
    # Validation
    if days < 1 or days > 365:
        return jsonify({'error': 'Days must be between 1 and 365'}), 400
        
    dreams = Dream.get_recent(user.id, days=days)
    
    return jsonify({
        'dreams': [d.to_dict() for d in dreams],
        'count': len(dreams),
        'days': days
    })


@dreams_bp.route('/api/dreams/<int:dream_id>/export', methods=['GET'])
def export_dream_pdf(dream_id):
    """Export a dream as a PDF file."""
    from backend.services.pdf_generator import generate_dream_pdf
    from flask import send_file
    
    dream = Dream.get_by_id(dream_id)
    if not dream:
        return jsonify({'error': 'Dream not found'}), 404
        
    try:
        pdf_buffer = generate_dream_pdf(dream.to_dict())
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({'error': 'Failed to generate PDF report'}), 500
    
    filename = f"dream_export_{dream_id}.pdf"
    if dream.created_at:
        try:
            if isinstance(dream.created_at, str):
                from datetime import datetime
                dt = datetime.fromisoformat(dream.created_at.replace('Z', '+00:00'))
            else:
                dt = dream.created_at
            filename = f"Dream_{dt.strftime('%Y%m%d_%H%M%S')}.pdf"
        except:
            pass
            
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
