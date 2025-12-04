from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.user import User, Role, SystemSetting
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_id = request.form.get('role_id')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return redirect(url_for('admin.create_user'))
            
        user = User(username=username, email=email, role_id=role_id)
        user.password = password
        db.session.add(user)
        db.session.commit()
        flash('用户创建成功', 'success')
        return redirect(url_for('admin.user_list'))
        
    roles = Role.query.all()
    return render_template('admin/user_form.html', roles=roles, user=None)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        role_id = request.form.get('role_id')
        user.role_id = role_id
        
        password = request.form.get('password')
        if password:
            user.password = password
            
        db.session.commit()
        flash('用户更新成功', 'success')
        return redirect(url_for('admin.user_list'))
        
    roles = Role.query.all()
    return render_template('admin/user_form.html', roles=roles, user=user)

@admin_bp.route('/users/<int:user_id>/delete')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin': # Prevent deleting the main admin
         flash('无法删除主管理员用户', 'error')
         return redirect(url_for('admin.user_list'))

    db.session.delete(user)
    db.session.commit()
    flash('用户删除成功', 'success')
    return redirect(url_for('admin.user_list'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    if request.method == 'POST':
        app_name_val = request.form.get('app_name')
        logo_url_val = request.form.get('logo_url')
        
        # Update App Name
        app_name = SystemSetting.query.filter_by(key='app_name').first()
        if not app_name:
            app_name = SystemSetting(key='app_name')
            db.session.add(app_name)
        app_name.value = app_name_val
        
        # Update Logo URL
        logo_url = SystemSetting.query.filter_by(key='logo_url').first()
        if not logo_url:
            logo_url = SystemSetting(key='logo_url')
            db.session.add(logo_url)
        logo_url.value = logo_url_val
        
        db.session.commit()
        flash('设置更新成功', 'success')
        return redirect(url_for('admin.settings'))
        
    settings_list = SystemSetting.query.all()
    settings_dict = {s.key: s.value for s in settings_list}
    return render_template('admin/settings.html', settings=settings_dict)
