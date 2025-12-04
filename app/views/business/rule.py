from flask import render_template, request, jsonify
from . import business_bp
from app import db
from app.models.rule import ScrapingRule
from flask_login import login_required
import json

def process_headers(headers_input):
    """
    Convert raw headers text (Key\nValue\n...) or JSON string to valid JSON string.
    """
    if not headers_input:
        return None
    
    # If it's already a dict, dump it
    if isinstance(headers_input, dict):
        return json.dumps(headers_input, ensure_ascii=False)
        
    # Try to parse as JSON first
    try:
        parsed = json.loads(headers_input)
        if isinstance(parsed, dict):
             return json.dumps(parsed, ensure_ascii=False)
    except:
        pass
        
    # If not JSON, assume raw key-value pairs separated by newlines
    lines = [line.strip() for line in headers_input.split('\n') if line.strip()]
    headers_dict = {}
    
    # Iterate in pairs
    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            key = lines[i]
            value = lines[i+1]
            headers_dict[key] = value
            
    return json.dumps(headers_dict, ensure_ascii=False)

@business_bp.route('/rules')
@login_required
def rules():
    return render_template('business/rule_list.html')

@business_bp.route('/rules/data')
@login_required
def rules_data():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    keyword = request.args.get('keyword', '')
    
    query = ScrapingRule.query
    
    if keyword:
        query = query.filter(ScrapingRule.site_name.contains(keyword) | ScrapingRule.domain.contains(keyword))
        
    pagination = query.order_by(ScrapingRule.created_at.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    data = []
    for item in pagination.items:
        data.append(item.to_dict())
        
    return jsonify({
        'code': 0,
        'msg': '',
        'count': pagination.total,
        'data': data
    })

@business_bp.route('/rules/create', methods=['POST'])
@login_required
def create_rule():
    try:
        data = request.json
        if not data.get('site_name'):
            return jsonify({'code': 400, 'msg': '站点名称不能为空'})
            
        rule = ScrapingRule(
            site_name=data.get('site_name'),
            domain=data.get('domain'),
            title_xpath=data.get('title_xpath'),
            content_xpath=data.get('content_xpath'),
            headers=process_headers(data.get('headers')),
            description=data.get('description')
        )
        db.session.add(rule)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/rules/update', methods=['POST'])
@login_required
def update_rule():
    try:
        data = request.json
        id = data.get('id')
        if not id:
            return jsonify({'code': 400, 'msg': 'ID不能为空'})
            
        rule = ScrapingRule.query.get(id)
        if not rule:
            return jsonify({'code': 404, 'msg': '规则不存在'})
            
        if 'site_name' in data:
            rule.site_name = data['site_name']
        if 'domain' in data:
            rule.domain = data['domain']
        if 'title_xpath' in data:
            rule.title_xpath = data['title_xpath']
        if 'content_xpath' in data:
            rule.content_xpath = data['content_xpath']
        if 'headers' in data:
            rule.headers = process_headers(data['headers'])
        if 'description' in data:
            rule.description = data['description']
            
        db.session.commit()
        return jsonify({'code': 0, 'msg': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/rules/delete', methods=['POST'])
@login_required
def delete_rule():
    try:
        ids = request.json.get('ids', [])
        if not ids:
            return jsonify({'code': 400, 'msg': '请选择要删除的数据'})
            
        ScrapingRule.query.filter(ScrapingRule.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})
