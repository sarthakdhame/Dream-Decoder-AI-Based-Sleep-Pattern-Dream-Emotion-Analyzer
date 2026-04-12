"""
Dream Decoder - Dream Routes
API endpoints for dream CRUD operations
"""
import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.models.dream import Dream
from backend.models.sleep import SleepRecord
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
    
    # Find exact dream keywords in text
    found_keywords = [kw for kw in dream_keywords if kw in text_lower]
    
    # Extract important words by length (4+ chars) and frequency, excluding common stop words
    stop_words = {'the', 'and', 'was', 'with', 'from', 'were', 'been', 'have', 'that', 'this', 'have', 'what', 'when', 'where', 'which', 'could', 'would', 'should'}
    words = re.findall(r'\b\w+\b', text_lower)
    word_freq = {}
    for word in words:
        if len(word) >= 4 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top words that aren't already in found_keywords
    extracted = sorted(word_freq.items(), key=lambda x: (-x[1], -len(x[0])))
    extra_keywords = [w[0] for w in extracted if w[0] not in found_keywords and w[1] >= 2]
    
    # Combine: prioritize dream keywords, then add frequent extracted words
    all_keywords = found_keywords + extra_keywords
    final_keywords = list(dict.fromkeys(all_keywords))[:8]  # Remove duplicates, keep top 8
    
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
    
    return {
        'sentiment': sentiment,
        'sentiment_score': sentiment_score,
        'primary_emotion': primary_emotion,
        'emotion_scores': {primary_emotion: 0.7} if primary_emotion != 'neutral' else {},
        'keywords': final_keywords,
        'entities': [],
        'themes': ['nightmare' if sentiment == 'negative' else 'peaceful' if sentiment == 'positive' else 'ordinary'],
        'categories': ['nightmare' if 'monster' in final_keywords or 'chase' in final_keywords else 'ordinary'],
        'summary': f'This dream has a {sentiment} tone with themes of {", ".join(final_keywords[:3])}.',
        'interpretation': {
            'overall_message': 'Analysis based on text pattern recognition. Full ML analysis unavailable.'
        },
        'emotion_confidence': 0.6,
        'detected_language': user_language,
        'language_confidence': 0.9,
    }


def _compute_duration_hours(sleep_time, wake_time):
    """Compute duration in hours, handling overnight sleep windows."""
    if not sleep_time or not wake_time:
        return None

    sleep_dt = datetime.strptime(sleep_time, "%H:%M")
    wake_dt = datetime.strptime(wake_time, "%H:%M")
    if wake_dt <= sleep_dt:
        wake_dt = wake_dt.replace(day=wake_dt.day + 1)
    return (wake_dt - sleep_dt).total_seconds() / 3600.0


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
                jungian_report = {
                    'analysis': jungian_result['error'],
                    'provider': 'Unavailable',
                    'status': 'error',
                    'generated_at': datetime.utcnow().isoformat()
                }
            else:
                jungian_report = {
                    'analysis': jungian_result.get('analysis', ''),
                    'provider': jungian_result.get('provider', 'Google Gemini'),
                    'status': 'ready',
                    'generated_at': datetime.utcnow().isoformat()
                }
        except Exception as jungian_err:
            print(f"WARNING: Jungian analysis skipped due to error: {jungian_err}")
            jungian_report = {
                'analysis': 'Jungian report could not be generated for this dream.',
                'provider': 'Unavailable',
                'status': 'error',
                'generated_at': datetime.utcnow().isoformat()
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
    user = request.current_user
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Validation
    if limit < 1 or limit > 100:
        limit = 50
    if offset < 0:
        offset = 0
        
    dreams = Dream.get_all(user.id, limit=limit, offset=offset)
    total = Dream.count(user.id)
    
    return jsonify({
        'dreams': [d.to_dict() for d in dreams],
        'total': total,
        'limit': limit,
        'offset': offset
    })


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
