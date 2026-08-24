import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from web_app import run_web_app
    print("Web app yukleniyor...")
    run_web_app()
except Exception as e:
    print(f"HATA: {e}")
    import traceback
    traceback.print_exc()
