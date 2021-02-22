from app import app, load_config

if __name__ == '__main__':
    print('Starting SDX Deliver')
    app.run(debug=True, host='0.0.0.0', port=5000)
    load_config()
