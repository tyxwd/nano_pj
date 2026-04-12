from flask import Flask, redirect, url_for
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from config.settings import MAX_CONTENT_LENGTH
from blueprints.health import health_bp
from blueprints.upload import upload_bp
from blueprints.predict import predict_bp
from blueprints.model_admin import model_admin_bp

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 让Flask在反向代理后识别真实的host/proto/prefix（如 /npj）。
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1, x_prefix=1)

CORS(app, resources={r"/*": {"origins": "*"}})

# 注册蓝图
app.register_blueprint(health_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(model_admin_bp)


# @app.after_request
# def add_no_cache_headers(response):
#     mimetype = (response.mimetype or "").lower()
#     if mimetype == 'application/json':
#         response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
#         response.headers['Pragma'] = 'no-cache'
#         response.headers['Expires'] = '0'
#     return response


# 根路径跳转到 /health
@app.route('/')
def root_redirect():
    return redirect(url_for('health.health_check'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
