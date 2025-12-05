from flask import render_template, request, jsonify
from flask_login import login_required
from app import db
from app.models.ai_engine import AIEngine
from . import business_bp

@business_bp.route('/ai_engines')
@login_required
def ai_engines():
    """
    Render the AI Engine Management page.
    """
    return render_template('business/ai_engine.html')

@business_bp.route('/ai_engines/list', methods=['GET'])
@login_required
def list_ai_engines():
    """
    Get list of AI engines for the frontend grid/table.
    """
    try:
        engines = AIEngine.query.order_by(AIEngine.created_at.desc()).all()
        data = [engine.to_dict() for engine in engines]
        return jsonify({'code': 0, 'msg': '', 'count': len(data), 'data': data})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/ai_engines/add', methods=['POST'])
@login_required
def add_ai_engine():
    """
    Add a new AI engine.
    """
    try:
        data = request.json
        new_engine = AIEngine(
            provider=data.get('provider'),
            api_url=data.get('api_url'),
            api_key=data.get('api_key'),
            model_name=data.get('model_name'),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_engine)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/ai_engines/update', methods=['POST'])
@login_required
def update_ai_engine():
    """
    Update an existing AI engine.
    """
    try:
        data = request.json
        engine_id = data.get('id')
        engine = AIEngine.query.get(engine_id)
        if not engine:
            return jsonify({'code': 404, 'msg': 'Engine not found'})
            
        engine.provider = data.get('provider')
        engine.api_url = data.get('api_url')
        engine.api_key = data.get('api_key')
        engine.model_name = data.get('model_name')
        engine.is_active = data.get('is_active', True)
        
        db.session.commit()
        return jsonify({'code': 0, 'msg': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/ai_engines/delete', methods=['POST'])
@login_required
def delete_ai_engine():
    """
    Delete an AI engine.
    """
    try:
        data = request.json
        engine_id = data.get('id')
        engine = AIEngine.query.get(engine_id)
        if not engine:
            return jsonify({'code': 404, 'msg': 'Engine not found'})
            
        db.session.delete(engine)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})
