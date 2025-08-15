import logging
from flask import request, jsonify, send_file, current_app, redirect
from flask import Blueprint, jsonify
import os
import subprocess
import pathlib
from sense_table.utils.local_fs import LocalFileSystem
from sense_table.utils.s3_fs import S3FileSystem
import time
from botocore.exceptions import ClientError
logger = logging.getLogger(__name__)
fs_bp = Blueprint('fs', __name__)



@fs_bp.get('/ls')
def get_ls():
    path = request.args.get('path')
    limit = int(request.args.get('limit', 100))
    show_hidden = request.args.get('show_hidden', 'false').lower() == 'true'

    try:
        if path.startswith('s3://'):
            s3_client = current_app.config['S3_CLIENT']
            items = S3FileSystem(s3_client).list_one_level(path, limit)
        else:
            items = LocalFileSystem.list_one_level(path, limit, show_hidden)
        return jsonify([item.model_dump() for item in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@fs_bp.get('/get-file')
def get_file():
    path = request.args.get('path')
    ext = os.path.splitext(path)[1]
    mime_type = {
        '.json': 'application/json',
        '.txt': 'text/plain',
    }
    if path.startswith('s3://'):
        logger.info(f"Generating signed URL for {path}")
        s3_client = current_app.config['S3_CLIENT']
        signed_url = S3FileSystem(s3_client).sign_get_url(path)
        return redirect(signed_url)
    else:
        if path.startswith('~'):
            path = os.path.expanduser(path)
        if not os.path.exists(path):
            return jsonify({"error": f"Path {path} does not exist"}), 404
        logger.info(f"Sending file {path}")
        return send_file(path, mimetype=mime_type.get(ext, 'application/octet-stream'))

@fs_bp.post('/upload')
def upload_file():
    path = request.args.get('path')
    content = request.json['content']
    if path.startswith('s3://'):
        s3_client = current_app.config['S3_CLIENT']
        try:
            S3FileSystem(s3_client).put_file(path, content)
            return jsonify({"status": "success"})
        except ClientError as e:
            msg = str(e)
            if 'AccessDenied' in msg:
                return jsonify({"status": "error", "error": msg}), 403
            else:
                return jsonify({"status": "error", "error": msg}), 400
    else:
        if path.startswith('~'):
            path = os.path.expanduser(path)
        pathlib.Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
    return jsonify({"status": "success"})

@fs_bp.post('/bash')
def run_bash():
    command = request.json['command']
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return jsonify({
        'status': 'success',
        'output': result.stdout,
        'error': result.stderr,
    })
