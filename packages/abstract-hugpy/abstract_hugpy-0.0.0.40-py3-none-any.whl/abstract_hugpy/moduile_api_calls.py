
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
    message = f'''{message}
{function_call}
path:{abs_file_path}
data:{data}'''
    logger.info(message)


@video_url_bp.route("/download_video", methods=["POST","GET"])
def downloadVideo():
    function_call = download_video
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = download_video(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/extract_video_audio", methods=["POST","GET"])
def extractVideoAudio():
    function_call = extract_video_audio
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = extract_video_audio(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_whisper_result", methods=["POST","GET"])
def getVideoWhisperResult():
    function_call = get_video_whisper_result
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_whisper_result(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_whisper_text", methods=["POST","GET"])
def getVideoWhisperText():
    function_call = get_video_whisper_text
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_whisper_text(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_whisper_segments", methods=["POST","GET"])
def getVideoWhisperSegments():
    function_call = get_video_whisper_segments
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_whisper_segments(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_metadata", methods=["POST","GET"])
def getVideoMetadata():
    function_call = get_video_metadata
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_metadata(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_captions", methods=["POST","GET"])
def getVideoCaptions():
    function_call = get_video_captions
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_captions(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_info", methods=["POST","GET"])
def getVideoInfo():
    function_call = get_video_info
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_info(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_directory", methods=["POST","GET"])
def getVideoDirectory():
    function_call = get_video_directory
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_directory(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_path", methods=["POST","GET"])
def getVideoPath():
    function_call = get_video_path
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_path(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_audio_path", methods=["POST","GET"])
def getVideoAudioPath():
    function_call = get_video_audio_path
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_audio_path(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_srt_path", methods=["POST","GET"])
def getVideoSrtPath():
    function_call = get_video_srt_path
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_srt_path(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)

@video_url_bp.route("/get_video_metadata_path", methods=["POST","GET"])
def getVideoMetadataPath():
    function_call = get_video_metadata_path
    data = get_request_data(request)
    initialize_call_log(function_call=function_call,data=data,message=None)
    try:        
        
        url = data.get('url')
        if not url:
            return get_json_response(value=f"url in {data}",status_code=400,function_call=function_call,data=data)
        result = get_video_metadata_path(url)
        if not result:
            return get_json_response(function_call=function_call,value=f"no result for {data}",status_code=400,function_call=function_call,data=data)
        return get_json_response(function_call=function_call,value=result,status_code=200,function_call=function_call,data=data)
    except Exception as e:
        message = f"{e}"
        return get_json_response(function_call=function_call,value=message,status_code=500,function_call=function_call,data=data)