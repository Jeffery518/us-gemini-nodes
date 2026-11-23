import sys
import yaml

def main():
    try:
        with open("output/all.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Failed to read output/all.yaml: {e}")
        sys.exit(0)

    proxies = data.get("proxies", []) if data else []
    if not proxies:
        print("No proxies found in output/all.yaml")
        sys.exit(0)

    proxy_names = [p["name"] for p in proxies if isinstance(p, dict) and "name" in p]

    full_config = {
        "mixed-port": 7890,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "ipv6": False,
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": "节点选择",
                "type": "select",
                "proxies": ["自动优选", "Gemini专线", "DIRECT"] + proxy_names,
            },
            {
                "name": "自动优选",
                "type": "url-test",
                "url": "https://www.gstatic.com/generate_204",
                "interval": 60,
                "tolerance": 50,
                "proxies": proxy_names,
            },
            {
                "name": "Gemini专线",
                "type": "fallback",
                "url": "https://www.gstatic.com/generate_204",
                "interval": 60,
                "proxies": proxy_names,
            },
        ],
        "rules": [
            "DOMAIN-KEYWORD,antigravity,Gemini专线",
            "GEOSITE,google-deepmind,Gemini专线",
            "DOMAIN-SUFFIX,gemini.google.com,Gemini专线",
            "DOMAIN-SUFFIX,aistudio.google.com,Gemini专线",
            "DOMAIN-SUFFIX,generativelanguage.googleapis.com,Gemini专线",
            "DOMAIN-SUFFIX,alkalimakersuite-pa.clients6.google.com,Gemini专线",
            "GEOIP,lan,DIRECT",
            "GEOIP,CN,DIRECT",
            "MATCH,节点选择",
        ],
    }

    with open("output/clash.yaml", "w", encoding="utf-8") as f:
        yaml.dump(full_config, f, allow_unicode=True, sort_keys=False)
    print(f"Successfully generated output/clash.yaml with {len(proxy_names)} nodes!")

if __name__ == "__main__":
    main()
