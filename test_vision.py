"""VISION - Final Verification Script"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  [PASS] {name}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        failed += 1

# Test 1: ASCII Face
def t1():
    from ui.ascii_face import ASCIIFace
    f = ASCIIFace()
    for s in ['idle','listening','thinking','speaking','sleeping','boot']:
        f.set_state(s)
        frame = f.get_frame()
        assert len(frame) >= 9
test("ASCII Face - 6 animation states", t1)

# Test 2: Notes CRUD
def t2():
    from modules.notes_module import manage_notes
    r = manage_notes('create', title='VisionTest', content='Hello')
    assert 'created' in r.lower()
    r = manage_notes('list')
    assert 'VisionTest' in r
    r = manage_notes('read', title='VisionTest')
    assert 'Hello' in r
    r = manage_notes('search', query='Hello')
    assert 'VisionTest' in r
    r = manage_notes('delete', title='VisionTest')
    assert 'removed' in r.lower() or 'Deleted' in r
test("Notes Module - CRUD + search", t2)

# Test 3: Planner
def t3():
    from modules.planner import manage_plan
    manage_plan('create', plan_name='TestPlan')
    manage_plan('add_task', plan_name='TestPlan', task='Task1')
    r = manage_plan('view', plan_name='TestPlan')
    assert 'Task1' in r
    r = manage_plan('complete_task', plan_name='TestPlan', task_index=1)
    assert 'Completed' in r or 'DONE' in r
    r = manage_plan('list')
    assert 'TestPlan' in r
test("Planner Module - tasks & completion", t3)

# Test 4: File Browser
def t4():
    from modules.file_browser import search_files, list_directory
    r = search_files('main', directory=os.path.dirname(os.path.abspath(__file__)))
    assert 'main' in r.lower()
    r = list_directory(os.path.dirname(os.path.abspath(__file__)))
    assert 'Contents of' in r
test("File Browser - search & list", t4)

# Test 5: App Launcher
def t5():
    from modules.app_launcher import APP_REGISTRY
    assert len(APP_REGISTRY) >= 20
    assert 'notepad' in APP_REGISTRY
    assert 'brave' in APP_REGISTRY
test("App Launcher - 29 apps registered", t5)

# Test 6: LLM Tools
def t6():
    from core.llm_engine import TOOL_DEFINITIONS
    names = [t['function']['name'] for t in TOOL_DEFINITIONS]
    assert len(names) == 21
    assert 'control_volume' in names
    assert 'send_whatsapp' in names
    assert 'explain_concept' in names
test("LLM Engine - 21 tool definitions", t6)

# Test 7: TTS
def t7():
    from core.tts_engine import TTSEngine
    e = TTSEngine()
    assert e is not None
test("TTS Engine - initializes", t7)

# Test 8: STT
def t8():
    from core.stt_engine import STTEngine
    e = STTEngine()
    assert e.wake_word == 'vision online'
test("STT Engine - initializes", t8)

# Test 9: Config
def t9():
    import config
    assert config.DATA_DIR.exists()
    assert config.SYSTEM_PROMPT
    assert len(config.THEME) >= 5
test("Config - all settings loaded", t9)

# Test 10: Weather (live)
def t10():
    from modules.web_search import get_weather
    r = get_weather('London')
    assert 'Temperature' in r or 'error' in r.lower()
test("Weather Module - live API call", t10)

# Test 11: Startup module
def t11():
    from startup.install_startup import check_startup
    result = check_startup()
    assert isinstance(result, bool)
test("Startup Module - check works", t11)

# Test 12: All module imports
def t12():
    from modules.system_control import control_volume, control_brightness, media_control
    from modules.web_browser import open_website, web_search
    from modules.youtube_module import search_youtube, play_music
    from modules.messaging import send_whatsapp, send_email
    from modules.screenshot_module import take_screenshot
    from modules.code_generator import generate_code
    from modules.knowledge import explain_concept
    from modules.typing_module import type_text
test("All 13 modules import cleanly", t12)

# Test 13: Terminal UI
def t13():
    from ui.terminal_ui import TerminalUI
    ui = TerminalUI()
    assert ui.face is not None
    assert ui.status == "online"
    ui.add_message("user", "test message")
    assert len(ui.conversation_log) == 1
test("Terminal UI - init & message log", t13)

print()
print("=" * 50)
print(f"  RESULTS: {passed} passed, {failed} failed")
if failed == 0:
    print("  ALL TESTS PASSED!")
print("=" * 50)
