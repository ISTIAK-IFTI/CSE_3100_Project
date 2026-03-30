#!/usr/bin/env python
import sys
sys.path.insert(0, 'e:\\RUET\\3_1 Materials\\CSE_3100_Project\\backend')

try:
    from app import app
    print('✅ app.py imported successfully')
    
    # Check if routes exist
    route_count = len([r for r in app.url_map.iter_rules()])
    print(f'✅ Flask app has {route_count} routes')
    
    # List some important routes
    print('\nImportant routes:')
    for rule in app.url_map.iter_rules():
        if 'login' in rule.rule or 'hall/allocations' in rule.rule:
            print(f'  {rule.rule} [{", ".join(rule.methods - {"HEAD", "OPTIONS"})}]')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
