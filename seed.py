from app import create_app, db
from app.models.user import Role, User, SystemSetting

app = create_app()

def seed():
    with app.app_context():
        # Create Roles
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', permissions=0xff) # Full permissions
            db.session.add(admin_role)
            print("Created Admin role.")
        
        user_role = Role.query.filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User', default=True, permissions=0x01) # Basic permissions
            db.session.add(user_role)
            print("Created User role.")
            
        db.session.commit()
        
        # Create Admin User
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', role=admin_role)
            admin_user.password = 'admin123'
            db.session.add(admin_user)
            print("Created Admin user (admin/admin123).")
        
        db.session.commit()
        
        # Create Default System Settings
        app_name = SystemSetting.query.filter_by(key='app_name').first()
        if not app_name:
            app_name = SystemSetting(key='app_name', value='政企智能舆情分析报告生成智能体应用系统')
            db.session.add(app_name)
            print("Created default app_name setting.")
            
        db.session.commit()

if __name__ == '__main__':
    seed()
