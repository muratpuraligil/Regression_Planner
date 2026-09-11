import os
import urllib.request
import urllib.error
import json
import argparse
import ssl

# Config
DIFY_API = "https://api.dify.ai/v1"

def load_env_file(filepath):
    envs = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                key, value = line.split(':', 1)
                envs[key.strip()] = value.strip()
    return envs

def main():
    parser = argparse.ArgumentParser(description="Inject environments into Dify DApp")
    parser.add_argument('--app-id', required=True, help="Dify App ID")
    parser.add_argument('--token', required=True, help="Dify Admin/API Token")
    parser.add_argument('--file', default='jiraEnvVariables', help="File containing variables")
    args = parser.parse_args()

    envs = load_env_file(args.file)
    print(f"📦 Bulunan Degiskenler: {list(envs.keys())}")

    headers = {
        "Authorization": f"Bearer {args.token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"🚀 {args.app_id} icin env yuklemesi baslatiliyor...")
    success_count = 0
    
    # SSL Sertifika dogrulamasi atlamak icin context kalibi (Mac icin kritik)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for name, value in envs.items():
        payload = {
            "name": name,
            "value": value,
            "value_type": "string"
        }
        url = f"{DIFY_API}/apps/{args.app_id}/environment-variables"
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                status_code = response.getcode()
                if status_code in [200, 201]:
                    print(f"✅ Basarili: {name}")
                    success_count += 1
                else:
                    print(f"❌ Hata ({name}): {status_code}")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"❌ Hata ({name}): {e.code} - {error_body}")
        except Exception as e:
            print(f"❌ Istek Hatasi ({name}): {e}")

    print(f"\n🎉 Islem Tamamlandi. ({success_count}/{len(envs)} basarili)")

if __name__ == '__main__':
    main()
