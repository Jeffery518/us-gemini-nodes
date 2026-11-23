import re
import sys
import yaml

def get_node_region(name: str) -> str:
    # 关键修复：只取第一段前缀，排除尾部 |GM-US 导致加拿大、德国、墨西哥等节点被误判为美国
    head = name.split("|")[0].strip()
    if re.search(r"^(🇺🇸|US_)|美国", head):
        return "US"
    if re.search(r"^(🇸🇬|SG_)|新加坡|狮城", head):
        return "SG"
    if re.search(r"^(🇯🇵|JP_)|日本|东京|大阪", head):
        return "JP"
    if re.search(r"^(🇭🇰|HK_)|香港", head):
        return "HK"
    if re.search(r"^(🇹🇼|TW_)|台湾", head):
        return "TW"
    if re.search(r"^(🇬🇧|GB_|UK_)|英国|伦敦", head):
        return "UK"
    if re.search(r"^(🇰🇷|KR_)|韩国|首尔", head):
        return "KR"
    return "OTHER"

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

    # 精准按国家前缀分类，严防尾部 GM-US 标签串味
    us_nodes = [n for n in proxy_names if get_node_region(n) == "US"]
    sg_nodes = [n for n in proxy_names if get_node_region(n) == "SG"]
    jp_nodes = [n for n in proxy_names if get_node_region(n) == "JP"]
    hk_nodes = [n for n in proxy_names if get_node_region(n) == "HK"]
    tw_nodes = [n for n in proxy_names if get_node_region(n) == "TW"]
    uk_nodes = [n for n in proxy_names if get_node_region(n) == "UK"]
    kr_nodes = [n for n in proxy_names if get_node_region(n) == "KR"]

    # Gemini 专属节点：100% 纯美国且通过 Gemini 解锁认证的节点
    gemini_us_nodes = [n for n in us_nodes if "GM" in n]
    gemini_final_nodes = gemini_us_nodes if gemini_us_nodes else us_nodes

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

    # 各国自动优选组（100% 纯净该国节点）
    country_definitions = [
        ("🇺🇸 美国-自动优选", us_nodes),
        ("🇸🇬 新加坡-自动优选", sg_nodes),
        ("🇯🇵 日本-自动优选", jp_nodes),
        ("🇭🇰 香港-自动优选", hk_nodes),
        ("🇹🇼 台湾-自动优选", tw_nodes),
        ("🇬🇧 英国-自动优选", uk_nodes),
        ("🇰🇷 韩国-自动优选", kr_nodes),
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

    # Gemini 专属专线：100% 纯美区 Gemini 解锁节点
    gemini_group = {
        "name": "🤖 Gemini-专属专线",
        "type": "fallback",
        "url": "https://www.gstatic.com/generate_204",
        "interval": 60,
        "proxies": ["🇺🇸 美国-自动优选"] + gemini_final_nodes,
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
    print(f"Pure US: {len(us_nodes)} (Gemini Unlocked: {len(gemini_us_nodes)}), SG: {len(sg_nodes)}, JP: {len(jp_nodes)}, HK: {len(hk_nodes)}, TW: {len(tw_nodes)}, UK: {len(uk_nodes)}, KR: {len(kr_nodes)}")

if __name__ == "__main__":
    main()
