from flask import render_template, request, jsonify, Response, stream_with_context
from . import business_bp
from app.utils.scraper import scrape_baidu_generator, scrape_content, scrape_sohu_generator
from flask_login import login_required
from app import db
from app.models import OpinionData
import json

@business_bp.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        source = request.form.get('source', 'baidu') # Default to baidu
        
        try:
            pages = int(request.form.get('pages', 1))
        except:
            pages = 1
            
        try:
            limit = request.form.get('limit')
            if limit:
                limit = int(limit)
            else:
                limit = None
        except:
            limit = None
            
        if not keyword:
            return jsonify({'code': 400, 'msg': '请输入关键字'})
        
        def generate():
            try:
                generator = None
                if source == 'sohu':
                    generator = scrape_sohu_generator(keyword, pages=pages, limit=limit)
                else:
                    generator = scrape_baidu_generator(keyword, pages=pages, limit=limit)
                    
                for item in generator:
                    yield json.dumps(item) + '\n'
            except Exception as e:
                yield json.dumps({'type': 'error', 'msg': str(e)}) + '\n'

        return Response(stream_with_context(generate()), mimetype='application/x-ndjson')
            
    return render_template('business/analysis.html')

@business_bp.route('/deep_crawl', methods=['POST'])
@login_required
def deep_crawl():
    url = request.form.get('url')
    if not url:
        return jsonify({'code': 400, 'msg': 'Missing URL'})
    
    try:
        content = scrape_content(url)
        return jsonify({'code': 0, 'msg': 'success', 'content': content})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})

@business_bp.route('/save_data', methods=['POST'])
@login_required
def save_data():
    try:
        items = request.json.get('items', [])
        if not items:
             return jsonify({'code': 400, 'msg': 'No data to save'})
        
        count = 0
        for item in items:
            # Check duplicate by original_url to prevent double insertion
            exists = OpinionData.query.filter_by(original_url=item.get('original_url')).first()
            if not exists:
                new_opinion = OpinionData(
                    keyword=item.get('keyword'),
                    title=item.get('title'),
                    url=item.get('url'),
                    original_url=item.get('original_url'),
                    source=item.get('source'),
                    cover_url=item.get('cover'),
                    content=item.get('content'),
                    is_deep_crawled=item.get('is_deep_crawled', False)
                )
                db.session.add(new_opinion)
                count += 1
        
        db.session.commit()
        return jsonify({'code': 0, 'msg': f'成功保存 {count} 条数据'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})
