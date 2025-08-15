from flask import Flask, request, send_from_directory, render_template, redirect, url_for, jsonify
import os
import argparse
import stat
import time
import sys
import json

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# The default directory is the current directory when the command is started.
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.dirname(__file__))

app.config['TEMPLATES_AUTO_RELOAD'] = True

# 增加最大文件大小限制
app.config['MAX_CONTENT_LENGTH'] = 2000 * 1024 * 1024  # 2000MB

def get_file_owner(filepath):
    if sys.platform == "win32":
        return ""
    else:
        import pwd
        stat_info = os.stat(filepath)
        return pwd.getpwuid(stat_info.st_uid).pw_name

def get_filemode(st_mode):
    is_dir = 'd' if stat.S_ISDIR(st_mode) else '-'
    perm = ''
    for who in 'USR', 'GRP', 'OTH':
        for what in 'R', 'W', 'X':
            perm += what.lower() if st_mode & getattr(stat, 'S_I' + what + who) else '-'
    return is_dir + perm

def list_files(directory):
    try:
        return [{'name': f, 'is_dir': os.path.isdir(os.path.join(directory, f))} for f in os.listdir(directory)]
    except OSError:
        return []

def list_directory_contents(req_path, directory):
    entries = os.listdir(directory)
    directories = []
    files = []
    data = []

    for entry in entries:
        if entry.startswith('.'):
            continue
        path = os.path.join(directory, entry)
        stat_info = os.stat(path)
        permissions = get_filemode(stat_info.st_mode)
        owner = get_file_owner(path)
        group = stat_info.st_gid
        try:
            if sys.platform != "win32":
                group = ""
            else:
                import grp
                group = grp.getgrgid(stat_info.st_gid).gr_name
        except:
            print("Failed to get group name for gid: " + str(stat_info.st_gid))
        size = stat_info.st_size
        if size > 1024 * 1024 * 1024: 
            size = "%.2f GB" % (size/1024.0/1024.0/1024.0)
        elif size > 1024 * 1024:
            size = "%.2f MB" % (size/1024.0/1024.0)
        elif size > 1024:
            size = "%.2f KB" % (size/1024.0)
        else:
            size = "%.2f B" % (size)
        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_mtime))
        
        href = ""
        file_type = "dir" if os.path.isdir(path) else "file"
        if file_type == "dir":
            directories.append((permissions, owner, group, size, mtime, entry, href))
            href = "/"+req_path+entry+"/"
        else:
            files.append((permissions, owner, group, size, mtime, entry, href))
            file_ext = entry.split('.')[-1].lower()
            if file_ext in ['html', 'txt', 'sh', 'scala', 'py', 'js', 'css', 'json', 'md', 'yml', 'yaml', 'ini','conf']:
                action = "edit"
            elif file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', 'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma']:
                action = "view"
            else:
                action = "download"
            href = "/"+action+"/"+req_path+entry
        
        data.append({
            'permissions': permissions,
            'owner': owner,
            'group': group,
            'size': size,
            'mtime': mtime,
            'name': entry,
            'href': href,
            'type': file_type
        })
    data.sort(key=lambda x: (x['type'] != 'dir', x['name']))
    return data

@app.route('/edit/<path:filename>', methods=['GET', 'POST'])
def edit_file(filename):
    abs_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if request.method == 'POST':
        # save file
        new_content = request.form['content']
        with open(abs_path, 'w') as file:
            file.write(new_content)
        return redirect(url_for('dir_listing', req_path=os.path.dirname(filename)))
    
    # read file
    with open(abs_path, 'r') as file:
        content = file.read()
    
    return render_template('edit_file.html', filename=filename, content=content, parent_path="/"+os.path.dirname(filename))

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    parent_path = "/"+os.path.dirname(req_path)
    
    if req_path and not req_path.endswith('/'):
        req_path += '/'

    abs_path = os.path.join(app.config['UPLOAD_FOLDER'], req_path)

    if not os.path.exists(abs_path):
        return 'Path not found'

    data = list_directory_contents(req_path, abs_path)
    dir1 = app.config['UPLOAD_FOLDER']
    the_path = dir1 +"/"+ req_path
    the_path = the_path.replace("//", "/")
    print("the_path: %s, req_path: %s, parent_path: %s" % (the_path, req_path, parent_path))
    
    return render_template('index.html', data=data, the_path=the_path, req_path=req_path, parent_path=parent_path)

@app.route('/download/<path:req_path>')
def download_file(req_path):
    abs_parent_path = os.path.abspath(app.config['UPLOAD_FOLDER'])
    return send_from_directory(abs_parent_path, req_path, as_attachment=True)

@app.route('/view/<path:req_path>')
def view_file(req_path):
    abs_parent_path = os.path.abspath(app.config['UPLOAD_FOLDER'])
    return send_from_directory(abs_parent_path, req_path, as_attachment=False)

@app.route('/upload', methods=['POST'])
def upload_file():
    req_path = request.args.get('path', '')
    abs_path = os.path.join(app.config['UPLOAD_FOLDER'], req_path)

    if not os.path.exists(abs_path):
        os.makedirs(abs_path)

    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = file.filename
        file.save(os.path.join(abs_path, filename))
        return 'File uploaded successfully to: {}'.format(os.path.join(abs_path, filename))

@app.route('/upload_ajax', methods=['POST'])
def upload_file_ajax():
    """处理AJAX上传请求，支持进度反馈"""
    try:
        req_path = request.args.get('path', '')
        abs_path = os.path.join(app.config['UPLOAD_FOLDER'], req_path)

        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if file:
            filename = file.filename
            # 确保文件名安全
            filename = os.path.basename(filename)
            file_path = os.path.join(abs_path, filename)
            file.save(file_path)
            
            response_data = {
                'success': True, 
                'message': f'文件上传成功: {filename}',
                'file_path': file_path,
                'file_size': os.path.getsize(file_path)
            }
            return app.response_class(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json'
            )
    
    except Exception as e:
        error_data = {'success': False, 'message': f'上传失败: {str(e)}'}
        return app.response_class(
            response=json.dumps(error_data),
            status=500,
            mimetype='application/json'
        )

@app.errorhandler(413)
def too_large(e):
    """处理文件过大的错误"""
    error_data = {
        'success': False, 
        'message': f'文件过大，最大支持2000MB。当前文件可能超过了限制。'
    }
    return app.response_class(
        response=json.dumps(error_data),
        status=413,
        mimetype='application/json'
    )


def main():
    parser = argparse.ArgumentParser(description="Simple HTTP Server")
    parser.add_argument("--port", type=int, default=25000, help="Port to serve on")
    default_dir = os.getcwd()

    parser.add_argument("--dir", type=str, default=default_dir, help="Directory to serve")
    parser.add_argument("--debug", type=bool, default=True, help="Debug mode")
    args = parser.parse_args()
    app.config['UPLOAD_FOLDER'] = args.dir
    print("default start command: ")
    print("whttpserver --port 25000  --dir %s --debug True " % args.dir)
    app.run(host='0.0.0.0', port=args.port,debug=args.debug)
    
if __name__ == '__main__':
    main()
 
