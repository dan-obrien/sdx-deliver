from app import app, cloud_config

if __name__ == '__main__':
    print('Starting SDX Deliver')
    cloud_config()
    app.run(debug=True, host='0.0.0.0', port=5000)
