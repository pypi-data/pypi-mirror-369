from abstract_utilities import *
def capitalize(string):
    if not string:
        return string
    if len(string)>1:
        return f"{string[0].upper()}{string[1:].lower()}"
    return string.upper()
def capitalize_underlines(strings):
    strings = strings.split('_')
    for i,string in enumerate(strings):
        string = string.lower()
        if i >0:
            string = capitalize(string)
        strings[i] = string
    return ''.join(strings)
texts = """def download_video(url): return video_mgr.download_video(url)
def extract_video_audio(url): return video_mgr.extract_audio(url)
def get_video_whisper_result(url): return video_mgr.get_whisper(url)
def get_video_whisper_text(url): return get_video_whisper_result(url).get('text')
def get_video_whisper_segments(url): return get_video_whisper_result(url).get('segments')
def get_video_metadata(url): return video_mgr.get_metadata(url)
def get_video_captions(url): return video_mgr.get_captions(url)
def get_video_info(url): return video_mgr.get_data(url).get('info')
def get_video_directory(url): return video_mgr.get_data(url).get('directory')
def get_video_path(url): return video_mgr.get_data(url).get('video_path')
def get_video_audio_path(url): return video_mgr.get_data(url).get('audio_path')
def get_video_srt_path(url): return video_mgr.get_data(url).get('srt_path')
def get_video_metadata_path(url): return video_mgr.get_data(url).get('metadata_path')
"""
function_string ="""
from abstract_flask import *
from abstract_utilities import *
video_url_bp,logger = get_bp('video_url_bp')
abs_file_path = os.path.abspath(__file__)
def get_json_response(value,status_code,function_call=None,data=None):
    dict_obj = {{}}
    if status_code ==200:
        dict_obj["success"]=True
        dict_obj["result"]=value
        initialize_call_log(function_call,data,message="success")
    else:
        dict_obj["success"]=False
        dict_obj["error"]=value
        initialize_call_log(function_call,data,message=f"ERROR: {value}")
    return jsonify(dict_obj),status_code
def initialize_call_log(function_call,data,message=None):
    message = message or "initializing "
    message = f'''{message}
{function_call}
path:{abs_file_path}
data:{data}'''
    logger.info(message)
abs_file_path = os.path.abspath(__file__)
def get_json_response(value,status_code,function_call=None,data=None):
    dict_obj = {}
    if status_code ==200:
        dict_obj["success"]=True
        dict_obj["result"]=value
        initialize_call_log(function_call,data,message="success")
    else:
        dict_obj["success"]=False
        dict_obj["error"]=value
        initialize_call_log(function_call,data,message=f"ERROR: {value}")
    return jsonify(dict_obj),status_code
def initialize_call_log(function_call,data,message=None):
    message = message or "initializing "
    message = f'''{message}\n{function_call}\npath:{abs_file_path}\ndata:{data}'''
    logger.info(message)
"""
function_strings = [function_string]
api_function_strings = [function_string]
for text in texts.split('\n'):
    if not text:
        continue
    function = text.split(' ')[1].split(':')[0]
    function_call = function.split('(')[0]
    function_name = capitalize_underlines(function_call)
    api_function_string = f'''
@modules_bp.route("/api/{function_call}", methods=["POST","GET"])
def {function_name}():
    function_call = "{function_call}"
    try:        
        result = get_from_local_host(function_call,request)
        return get_json_response(value=result,status_code=200,function_call=function_call)
    except Exception as e:
        message = f"{{e}}"
        return get_json_response(value=message,status_code=500,function_call=function_call)'''
    api_function_strings.append(api_function_string)
    function_string = f'''
@video_url_bp.route("/{function_call}", methods=["POST","GET"])
def {function_name}():
    function_call = {function_call}
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {{data}}",status_code=400,function_call=function_call,data=data)
        result = {function_call}(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {{data}}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{{e}}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)'''
    function_strings.append(function_string)
write_to_file(contents='\n'.join(function_strings),file_path='moduile_api_calls.py')
print('\n'.join(api_function_strings))
