import re
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

    # 按国家与地区进行分类
    us_nodes = [n for n in proxy_names if re.search(r"(?i)(美国|🇺🇸|US|United States)", n)]
    sg_nodes = [n for n in proxy_names if re.search(r"(?i)(新加坡|🇸🇬|SG|Singapore|狮城)", n)]
    jp_nodes = [n for n in proxy_names if re.search(r"(?i)(日本|🇯🇵|JP|Japan|东京|大阪)", n)]
    hk_nodes = [n for n in proxy_names if re.search(r"(?i)(香港|🇭🇰|HK|HongKong)", n)]
    tw_nodes = [n for n in proxy_names if re.search(r"(?i)(台湾|🇹🇼|TW|Taiwan|台北)", n)]
    uk_nodes = [n for n in proxy_names if re.search(r"(?i)(英国|🇬🇧|UK|Great Britain|伦敦)", n)]
    
    # Gemini 解锁节点
    gm_nodes = [n for n in proxy_names if re.search(r"(?i)(GM)", n)]

    # 构建策略组
    proxy_groups = []

    # 1. 自动选择组定义列表
    auto_groups = []

    # 全球自动优选
    auto_groups.append({
        "name": "🚀 全球自动优选",
        "type": "url-test",
        "url": "https://www.gstatic.com/generate_204",
        "interval": 60,
        "tolerance": 50,
        "proxies": proxy_names,
    })

    # 各国自动优选组（仅在存在该国节点时加入）
    country_definitions = [
        ("🇺🇸 美国-自动优选", us_nodes),
        ("🇸🇬 新加坡-自动优选", sg_nodes),
        ("🇯🇵 日本-自动优选", jp_nodes),
        ("🇭🇰 香港-自动优选", hk_nodes),
        ("🇹🇼 台湾-自动优选", tw_nodes),
        ("🇬🇧 英国-自动优选", uk_nodes),
    ]

    available_country_group_names = []
    for group_name, nodes in country_definitions:
        if nodes:
            auto_groups.append({
                "name": group_name,
                "type": "url-test",
                "url": "https://www.gstatic.com/generate_204",
                "interval": 60,
                "tolerance": 50,
                "proxies": nodes,
            })
            available_country_group_names.append(group_name)

    # Gemini 专属容灾组（优先走解锁 Gemini 的节点或美区/新加坡优选）
    gemini_proxies = gm_nodes if gm_nodes else (us_nodes if us_nodes else proxy_names)
    gemini_group = {
        "name": "🤖 Gemini-专属专线",
        "type": "fallback",
        "url": "https://www.gstatic.com/generate_204",
        "interval": 60,
        "proxies": [g for g in ["🇺🇸 美国-自动优选", "🇸🇬 新加坡-自动优选", "🇯🇵 日本-自动优选"] if g in available_country_group_names] + gemini_proxies,
    }

    # 顶层主控制组：节点选择
    main_select_proxies = [
        "🚀 全球自动优选",
        *available_country_group_names,
        "🤖 Gemini-专属专线",
        "DIRECT",
        *proxy_names,
    ]

    main_select_group = {
        "name": "节点选择",
        "type": "select",
        "proxies": main_select_proxies,
    }

    proxy_groups = [main_select_group, *auto_groups, gemini_group]

    full_config = {
        "mixed-port": 7890,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "ipv6": False,
        "proxies": proxies,
        "proxy-groups": proxy_groups,
        "rules": [
            "DOMAIN-KEYWORD,antigravity,🤖 Gemini-专属专线",
            "GEOSITE,google-deepmind,🤖 Gemini-专属专线",
            "DOMAIN-SUFFIX,gemini.google.com,🤖 Gemini-专属专线",
            "DOMAIN-SUFFIX,aistudio.google.com,🤖 Gemini-专属专线",
            "DOMAIN-SUFFIX,generativelanguage.googleapis.com,🤖 Gemini-专属专线",
            "DOMAIN-SUFFIX,alkalimakersuite-pa.clients6.google.com,🤖 Gemini-专属专线",
            "GEOIP,lan,DIRECT",
            "GEOIP,CN,DIRECT",
            "MATCH,节点选择",
        ],
    }

    with open("output/clash.yaml", "w", encoding="utf-8") as f:
        yaml.dump(full_config, f, allow_unicode=True, sort_keys=False)
    
    print(f"Successfully generated output/clash.yaml with {len(proxy_names)} nodes!")
    print(f"Countries detected - US: {len(us_nodes)}, SG: {len(sg_nodes)}, JP: {len(jp_nodes)}, HK: {len(hk_nodes)}, TW: {len(tw_nodes)}, UK: {len(uk_nodes)}")

if __name__ == "__main__":
    main()
