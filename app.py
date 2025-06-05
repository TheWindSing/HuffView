import heapq
from flask import Flask, request, jsonify, render_template
# import threading 
# import webbrowser 
# import time 
# import subprocess 
import os
import sys
import math


# ================================
# Flask 应用初始化
# ================================
# PyInstaller 用launcher.py打包
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后，temp_path 是 PyInstaller 解压文件的临时目录
    base_path = sys._MEIPASS
else:
    # 非打包状态（直接运行 .py 文件）
    base_path = os.path.dirname(os.path.abspath(__file__))

template_path = os.path.join(base_path, 'templates')
app = Flask(__name__, template_folder=template_path) 
# app = Flask(__name__)

# ================================
# Huffman 编码核心功能
# ================================

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1

    heap = [HuffmanNode(char, f) for char, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0], freq

def generate_codes(node, prefix='', code_map=None):
    if code_map is None:
        code_map = {}
    if node.char is not None:
        code_map[node.char] = prefix
    else:
        generate_codes(node.left, prefix + '0', code_map)
        generate_codes(node.right, prefix + '1', code_map)
    return code_map

def encode_text(text, code_map):
    return ''.join(code_map[char] for char in text)

def decode_text(encoded, tree):
    result = ''
    node = tree
    for bit in encoded:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            result += node.char
            node = tree
    return result


def calculate_entropy_and_avg_length(freq, code_map):
    total = sum(freq.values())
    entropy = 0.0
    avg_length = 0.0
    for char in freq:
        p = freq[char] / total
        l = len(code_map[char])
        entropy += -p * math.log2(p)
        avg_length += p * l
    return round(entropy, 4), round(avg_length, 4), round(entropy / avg_length * 100, 2)

# ================================
# Flask 路由
# ================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/huffman', methods=['POST'])
def huffman_api():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': '文本不能为空'}), 400

    tree, freq = build_huffman_tree(text)
    code_map = generate_codes(tree)
    encoded = encode_text(text, code_map)
    decoded = decode_text(encoded, tree)

    # return jsonify({
    #     'frequency': freq,
    #     'codeMap': code_map,
    #     'encoded': encoded,
    #     'decoded': decoded,
    #     'tree': serialize_tree(tree) 
    # })
    
    # ===== 计算编码效率 =====
    original_bits = len(text) * 8                 # 原始比特数 = 文本长度 * 8
    encoded_bits = len(encoded)                    # 编码后比特数 = 二进制串长度
    if original_bits > 0:
        compression_rate = round((original_bits - encoded_bits) / original_bits * 100, 2)
    else:
        compression_rate = 0.0

    entropy, avg_len, efficiency = calculate_entropy_and_avg_length(freq, code_map)

    return jsonify({
        'frequency': freq, 
        'codeMap': code_map,
        'encoded': encoded,
        'decoded': decode_text(encoded, tree),
        'tree': serialize_tree(tree),
        'originalBits': original_bits,
        'encodedBits': encoded_bits,
        'compressionRate': compression_rate,
        'entropy': entropy,
        'averageLength': avg_len,
        'codingEfficiency': efficiency
    })

def serialize_tree(node):
    if node is None:
        return None
    return {
        'char': node.char,
        'freq': node.freq,
        'left': serialize_tree(node.left),
        'right': serialize_tree(node.right)
    }

@app.route('/decode', methods=['POST'])
def decode_api():
    data = request.get_json()
    encoded = data.get('encoded', '')
    tree_data = data.get('tree', {})

    if not encoded or not tree_data:
        return jsonify({'error': '缺少编码数据或树结构'}), 400

    def deserialize_tree(data):
        if data is None:
            return None
        node = HuffmanNode(data['char'], data['freq'])
        node.left = deserialize_tree(data.get('left'))
        node.right = deserialize_tree(data.get('right'))
        return node

    tree = deserialize_tree(tree_data)
    decoded = decode_text(encoded, tree)
    return jsonify({'decoded': decoded})
    
# # 用于关闭服务器
# @app.route('/shutdown', methods=['GET'])
# def shutdown():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()
#     return jsonify({'message': '服务器正在关闭...'}), 200

# # === 浏览器启动函数 ===
# def open_browser():
#     # 稍微等待一下，确保 Flask 服务器有时间启动并监听端口
#     # time.sleep(1) # 2秒通常足够，如果遇到问题可以适当增加

#     app_url = "http://127.0.0.1:5000/"

#     webbrowser.open(app_url)

#     # # 尝试使用您之前配置的 Edge 路径和参数来打开浏览器
#     # edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge_proxy.exe"
#     # edge_args = [
#     #     edge_path,
#     #     app_url
#     # ]
#     # try:
#     #     subprocess.Popen(edge_args) # 使用 subprocess 启动浏览器，防止阻塞
#     # except FileNotFoundError:
#     #     print(f"Error: Edge browser executable not found at {edge_path}. Trying default browser...")
#     #     webbrowser.open(app_url) # 如果特定路径的 Edge 找不到，尝试用默认浏览器打开
#     # except Exception as e:
#     #     print(f"Failed to open Edge browser ({e}). Trying default browser...")
#     #     webbrowser.open(app_url) # 其他错误，尝试用默认浏览器打开


# === 主程序入口 ===
if __name__ == '__main__':
    # # 在一个新的线程中启动浏览器打开函数
    # # 这样主线程就可以继续运行 Flask 服务器，而不会被浏览器启动阻塞
    # browser_thread = threading.Thread(target=open_browser)
    # browser_thread.daemon = True # 设置为守护线程，这样当主程序（Flask）退出时，这个线程也会随之退出
    # browser_thread.start() # 启动线程

    # # 在主线程中运行 Flask 应用
    # # 这是一个阻塞调用，但浏览器已经由另一个线程启动了
    app.run(debug=False, host='127.0.0.1', port=5000)