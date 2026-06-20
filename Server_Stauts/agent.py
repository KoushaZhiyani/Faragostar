#agent.py


from flask import Flask, jsonify, request
import psutil

app = Flask(__name__)

@app.route('/cpu')
def get_cpu():
    """درصد استفاده از CPU (کل)"""
    return jsonify({'cpu_percent': psutil.cpu_percent(interval=1)})

@app.route('/memory')
def get_memory():
    """اطلاعات رم (درصد و مقادیر)"""
    mem = psutil.virtual_memory()
    return jsonify({
        'total_gb': round(mem.total / (1024**3), 2),
        'used_gb': round(mem.used / (1024**3), 2),
        'percent': mem.percent
    })

@app.route('/disk')
def get_disk():
    """اطلاعات دیسک بر اساس درایو (پیش‌فرض D)"""
    drive = request.args.get('drive', 'D:')
    try:
        usage = psutil.disk_usage(drive)
        return jsonify({
            'drive': drive,
            'total_gb': round(usage.total / (1024**3), 2),
            'used_gb': round(usage.used / (1024**3), 2),
            'free_gb': round(usage.free / (1024**3), 2),
            'percent': usage.percent
        })
    except FileNotFoundError:
        return jsonify({'error': f'درایو {drive} یافت نشد'}), 404

    # در محیط واقعی بهتر است host='0.0.0.0' باشد تا از بیرون قابل دسترسی باشد
app.run(host='0.0.0.0', port=5000)