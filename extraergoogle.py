import requests
from supabase import create_client, Client

# --- Configuración Supabase ---
SUPABASE_URL = "https://xfylujdfpmajnbmuiebv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmeWx1amRmcG1ham5ibXVpZWJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTc5NzMxMSwiZXhwIjoyMDg3MzczMzExfQ.Q1FtXUdASDH423nwOvs1vzJgS5hHvhK2j5DXs1scwYs"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Configuración Google (SerpApi) ---
SERPAPI_KEY = "f9437f98fcf2a804a5d1659ee078a95ddd70c5b9b0c73a4d9be70cbca50472bc"
PLACE_ID = "ChIJu6XIIFaipBIRPy9jHrQ5oSY" 

def importar():
    print("Sincronizando con Google Maps...")
    url = f"https://serpapi.com/search.json?engine=google_maps_reviews&place_id={PLACE_ID}&api_key={SERPAPI_KEY}&hl=es&sort_by=newest_first"
    
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status() # Verifica que no haya error de conexión con SerpApi
        data = respuesta.json()
    except Exception as e:
        print(f"❌ Error al conectar con SerpApi: {e}")
        return

    if "reviews" in data:
        # Tomamos solo las últimas 5 reseñas
        for r in data["reviews"][:5]:
            
            # MAGIA AQUÍ: Aseguramos que si no hay texto, ponga "Sin comentario" en lugar de dar error (None)
            comentario_texto = r.get("snippet") or r.get("text") or "Sin comentario"
            
            payload = {
                "valoracion": int(r.get("rating", 5)),
                "comentario": comentario_texto.strip(),
                "restaurant_slug": "el-buen-bocado",
                "origen": "Google"
            }
            
            try:
                # Insertamos en la tabla 'resenas' (en minúsculas)
                supabase.table("resenas").insert(payload).execute()
                print(f"✅ Éxito guardando: {payload['valoracion']}⭐ - {payload['comentario'][:30]}...")
            except Exception as e:
                # Si sigue saliendo 42501, imprimirá este error
                print(f"❌ Error de base de datos: {e}")
    else:
        print("No se encontraron reseñas nuevas en Google.")

if __name__ == "__main__":
    importar()