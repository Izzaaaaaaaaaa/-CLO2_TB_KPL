import threading
import webbrowser
import uvicorn
from cli.api import app
from env_loader import get_env
from cli.config_loader import get_config

def run_api_server():
    """
    Menjalankan server API dengan konfigurasi dari environment variables
    """
    api_host = get_config("API_HOST")
    api_port = int(get_config("API_PORT"))
    api_docs_url = get_config("API_DOCS_URL")

    print(f"\n🚀 Memulai server API di http://{api_host}:{api_port}")
    webbrowser.open(api_docs_url)
    uvicorn.run(app, host=api_host, port=api_port)

def run_api():
    """
    Fungsi yang dipanggil dari menu untuk menjalankan API server
    """
    try:
        print("\n⏳ Mempersiapkan server API...")
        run_api_server()
    except Exception as e:
        print(f"❌ Error ketika menjalankan API: {e}")
