from app import create_app
from flask_script import Manager, Server


app = create_app()
manager = Manager(app)
manager.add_command('runserver', Server(host='127.0.0.1', port=app.config['SERVER_PORT'], use_debugger=True, use_reloader=True))

def main():
    manager.run()

if __name__ == '__main__':
    # app.run(debug=app.config['DEBUG'])
    try:
        import sys
        sys.exit(main())
    except Exception as e:
        import traceback
        traceback.print_exc()



