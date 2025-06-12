import webbrowser
import uvicorn
from api.api import app
from utils.env_loader import get_env

def run_api_server():
    """
    Menjalankan server API dengan konfigurasi dari environment variables
    """
    api_host = get_env("API_HOST", "127.0.0.1")
    api_port = int(get_env("API_PORT", "8000"))
    api_docs_url = get_env("API_DOCS_URL", "http://localhost:8000/docs")

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
