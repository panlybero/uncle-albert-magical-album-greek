#!/usr/bin/env python3
"""Post-build patcher for ScummVM's generated scummvm.js (handles both minified and unminified output)."""
import pathlib
import sys

JS_PATH = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "scummvm.js"
s = JS_PATH.read_text()
orig = s

# 0. Preserve pre-set Module["arguments"] in Emscripten pre-js and catch WebMIDI rejection
if 'Module["arguments"]=[];' in s:
    s = s.replace('Module["arguments"]=[];', 'Module["arguments"]=Module["arguments"]||[];', 1)
    print("Patched Module['arguments'] init")
elif "Module['arguments'] = [];" in s:
    s = s.replace("Module['arguments'] = [];", "Module['arguments'] = Module['arguments'] || [];", 1)
    print("Patched Module['arguments'] init")

old_midi = "midiAccess.onstatechange=e=>{midiOutputMap=e.target.outputs}})"
new_midi = "midiAccess.onstatechange=e=>{midiOutputMap=e.target.outputs}}).catch(()=>{})"
if old_midi in s and new_midi not in s:
    s = s.replace(old_midi, new_midi, 1)
    print("Patched requestMIDIAccess .catch()")

# 1. Route locateFile(path, scriptDirectory) through resolveScummUrl
old_locate_min = 'function locateFile(path){if(Module["locateFile"]){return Module["locateFile"](path,scriptDirectory)}return scriptDirectory+path}'
new_locate_min = 'function locateFile(path){if(Module["locateFile"]){return Module["locateFile"](path,scriptDirectory)}var p=scriptDirectory+path;return globalThis["resolveScummUrl"]?globalThis["resolveScummUrl"](p):p}'
old_locate = "function locateFile(path) {\n  if (Module['locateFile']) {\n    return Module['locateFile'](path, scriptDirectory);\n  }\n  return scriptDirectory + path;\n}"
new_locate = "function locateFile(path) {\n  if (Module['locateFile']) {\n    return Module['locateFile'](path, scriptDirectory);\n  }\n  var p = scriptDirectory + path;\n  return globalThis['resolveScummUrl'] ? globalThis['resolveScummUrl'](p) : p;\n}"

if old_locate_min in s:
    s = s.replace(old_locate_min, new_locate_min, 1)
    print("Patched locateFile() (minified)")
elif old_locate in s:
    s = s.replace(old_locate, new_locate, 1)
    print("Patched locateFile()")
elif 'globalThis["resolveScummUrl"]?globalThis["resolveScummUrl"](p):p' in s or "globalThis['resolveScummUrl'] ? globalThis['resolveScummUrl'](p) : p" in s:
    print("locateFile() already patched")
else:
    raise RuntimeError("Could not find locateFile() in scummvm.js")

# 2. Preserve Module['arguments'] instead of resetting arguments_ = []
if "var arguments_=[];" in s:
    s = s.replace("var arguments_=[];", 'var arguments_=Module["arguments"]||[];', 1)
    print("Patched arguments_ (minified)")
elif "var arguments_ = [];" in s:
    s = s.replace("var arguments_ = [];", "var arguments_ = Module['arguments'] || [];", 1)
    print("Patched arguments_")
elif 'var arguments_=Module["arguments"]||[];' in s or "var arguments_ = Module['arguments'] || [];" in s:
    print("arguments_ already patched")
else:
    raise RuntimeError("Could not find var arguments_ = [] in scummvm.js")

# 3. Restrict SDL3's global window key listener to #canvas so typing in the
#    on-screen keyboard input field doesn't double-trigger via window bubbling.
old_key_min = "var registerKeyEventCallback=(target,userData,useCapture,callbackfunc,eventTypeId,eventTypeString,targetThread)=>{"
new_key_min = 'var registerKeyEventCallback=(target,userData,useCapture,callbackfunc,eventTypeId,eventTypeString,targetThread)=>{if(target===2)target="#canvas";'
old_key = "JSEvents.registerKeyEventCallback(target, userData, useCapture, callbackfunc, eventTypeId, eventTypeString, targetThread);"
new_key = "if (target === 2) target = \"#canvas\";\n  JSEvents.registerKeyEventCallback(target, userData, useCapture, callbackfunc, eventTypeId, eventTypeString, targetThread);"

if new_key_min in s or new_key in s:
    print("registerKeyEventCallback already patched")
elif old_key_min in s:
    s = s.replace(old_key_min, new_key_min, 1)
    print("Patched registerKeyEventCallback target -> #canvas (minified)")
elif old_key in s:
    s = s.replace(old_key, new_key, 1)
    print("Patched registerKeyEventCallback target -> #canvas")
else:
    raise RuntimeError("Could not find registerKeyEventCallback in scummvm.js")

# 4. Disable SDL3 raw touch listener so web/index.html's Trackpad / Direct Touch
#    layer is the single authoritative pointer input source on touchscreens.
old_touch_min = "var registerTouchEventCallback=(target,userData,useCapture,callbackfunc,eventTypeId,eventTypeString,targetThread)=>{"
new_touch_min = "var registerTouchEventCallback=(target,userData,useCapture,callbackfunc,eventTypeId,eventTypeString,targetThread)=>{return 0;"
if new_touch_min in s:
    print("registerTouchEventCallback already patched")
elif old_touch_min in s:
    s = s.replace(old_touch_min, new_touch_min, 1)
    print("Patched registerTouchEventCallback -> no-op (minified)")

# 5. Guard JSEvents DOM callbacks while an async HTTP fetch is unwound in Asyncify
old_jsev_min = "eventHandler.eventListenerFunc=function(event){++JSEvents.inEventHandler;"
new_jsev_min = 'eventHandler.eventListenerFunc=function(event){if(globalThis["_scummAsyncFetchActive"]>0||Asyncify.state!==0){if(event&&/^(mousedown|mouseup|keydown|keyup)$/.test(event.type)){setTimeout(()=>eventHandler.eventListenerFunc(event),16)}return}++JSEvents.inEventHandler;'
if new_jsev_min in s:
    print("JSEvents async fetch guard already patched")
elif old_jsev_min in s:
    s = s.replace(old_jsev_min, new_jsev_min, 1)
    print("Patched JSEvents async fetch guard")

# 6. Guard SDL3 WebAudio ScriptProcessorNode callbacks while an async HTTP fetch is unwound
old_audio_min = 'SDL3.audio_playback.scriptProcessorNode["onaudioprocess"]=function(e){'
new_audio_min = 'SDL3.audio_playback.scriptProcessorNode["onaudioprocess"]=function(e){if(globalThis["_scummAsyncFetchActive"]>0||Asyncify.state!==0){if(e&&e["outputBuffer"]){for(var c=0;c<e["outputBuffer"].numberOfChannels;c++)e["outputBuffer"].getChannelData(c).fill(0)}return}'
if new_audio_min in s:
    print("SDL3 onaudioprocess async fetch guard already patched")
elif old_audio_min in s:
    s = s.replace(old_audio_min, new_audio_min, 1)
    print("Patched SDL3 onaudioprocess async fetch guard")

old_silence_min = "var silence_callback=function(){"
new_silence_min = 'var silence_callback=function(){if(globalThis["_scummAsyncFetchActive"]>0||Asyncify.state!==0)return;'
if new_silence_min in s:
    print("SDL3 silence_callback async fetch guard already patched")
elif old_silence_min in s:
    s = s.replace(old_silence_min, new_silence_min)
    print("Patched SDL3 silence_callback async fetch guard")

if s != orig:
    JS_PATH.write_text(s)
    print(f"Saved patched {JS_PATH}")

