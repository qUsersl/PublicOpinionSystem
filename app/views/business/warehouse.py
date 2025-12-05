from flask import render_template, request, jsonify, current_app
from . import business_bp
from app import db
from app.models import OpinionData, ScrapingRule, OpinionDetail
from flask_login import login_required
from datetime import datetime
from app.utils.scraper import deep_crawl_content

@business_bp.route('/warehouse')
@login_required
def warehouse():
    return render_template('business/warehouse.html')

@business_bp.route('/warehouse/data')
@login_required
def warehouse_data():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    keyword = request.args.get('keyword', '')
    
    query = OpinionData.query
    
    if keyword:
        query = query.filter(OpinionData.title.contains(keyword) | OpinionData.content.contains(keyword))
        
    pagination = query.order_by(OpinionData.created_at.desc()).paginate(
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

@business_bp.route('/warehouse/delete', methods=['POST'])
@login_required
def delete_data():
    try:
        ids = request.json.get('ids', [])
        if not ids:
            return jsonify({'code': 400, 'msg': 'No data selected'})
            
        OpinionData.query.filter(OpinionData.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'code': 0, 'msg': 'Deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/warehouse/update', methods=['POST'])
@login_required
def update_data():
    try:
        data = request.json
        id = data.get('id')
        if not id:
            return jsonify({'code': 400, 'msg': 'Missing ID'})
            
        item = OpinionData.query.get(id)
        if not item:
            return jsonify({'code': 404, 'msg': 'Data not found'})
            
        if 'title' in data:
            item.title = data['title']
        if 'content' in data:
            item.content = data['content']
        if 'source' in data:
            item.source = data['source']
            
        db.session.commit()
        return jsonify({'code': 0, 'msg': 'Updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/warehouse/analyze', methods=['POST'])
@login_required
def analyze_data():
    # Placeholder for AI analysis
    try:
        id = request.json.get('id')
        if not id:
            return jsonify({'code': 400, 'msg': 'Missing ID'})
            
        # TODO: Implement AI analysis logic here
        # For now, just return a success message
        
        return jsonify({'code': 0, 'msg': 'AI analysis request submitted (Placeholder)'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/warehouse/deep-crawl', methods=['POST'])
@login_required
def deep_crawl_data():
    try:
        ids = request.json.get('ids', [])
        if not ids:
            return jsonify({'code': 400, 'msg': 'No data selected'})
        
        items = OpinionData.query.filter(OpinionData.id.in_(ids)).all()
        success_count = 0
        
        for item in items:
            # Find matching rule
            # source format might be "Source Name Date" or just "Source Name"
            source_name = item.source.split(' ')[0] if item.source else ''
            
            rule = ScrapingRule.query.filter(ScrapingRule.site_name == source_name).first()
            
            if not rule and item.source:
                 # Try exact match
                 rule = ScrapingRule.query.filter(ScrapingRule.site_name == item.source).first()
            
            rule_config = rule.to_dict() if rule else None
            
            # Crawl
            target_url = item.url or item.original_url
            title, content, new_rule_config = deep_crawl_content(target_url, rule_config)
            
            if title or content:
                # Save to OpinionDetail
                detail = OpinionDetail.query.filter_by(opinion_id=item.id).first()
                if not detail:
                    detail = OpinionDetail(opinion_id=item.id)
                    db.session.add(detail)
                
                if title:
                    detail.title = title
                    # Do NOT update item.title with detailed title, keep original title for list view
                    # item.title = title 
                if content:
                    detail.content = content
                    # Ensure item.content is NOT updated
                    # item.content = content 
                
                # Update is_deep_crawled status in OpinionData
                item.is_deep_crawled = True
                success_count += 1
                
                # Update rule if changed and we have a rule object
                if rule and new_rule_config:
                    if 'content_xpath' in new_rule_config and new_rule_config['content_xpath'] != rule.content_xpath:
                        rule.content_xpath = new_rule_config['content_xpath']
                        rule.updated_at = datetime.now()

        db.session.commit()
        return jsonify({'code': 0, 'msg': f'详细内容采集完成，成功 {success_count} 条'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/warehouse/preview/<int:id>')
@login_required
def preview_data(id):
    item = OpinionData.query.get_or_404(id)
    detail = OpinionDetail.query.filter_by(opinion_id=id).first()
    
    if not detail:
        return render_template('business/preview.html', item=item, detail=None, msg="尚未进行深度采集或采集失败")
    
    return render_template('business/preview.html', item=item, detail=detail)


