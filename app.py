from flask import Flask, redirect
from flask_cors import CORS
from config.settings import MAX_CONTENT_LENGTH
from blueprints.health import health_bp
from blueprints.upload import upload_bp
from blueprints.predict import predict_bp

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

CORS(app, resources={r"/*": {"origins": "*"}})

# 注册蓝图
app.register_blueprint(health_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(predict_bp)


# 根路径跳转到 /health
@app.route('/')
def root_redirect():
    return redirect('/health')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
