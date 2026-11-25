import ipaddress
import re
import sys
import yaml

# Cloudflare / Anycast 任播网段（GitHub 美区测速会显示为美国，但国内直连会就近分配到新加坡/香港/日本）
ANYCAST_CIDRS = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22", "8.6.112.0/24",
    "8.34.208.0/20",
]
ANYCAST_NETWORKS = [ipaddress.ip_network(cidr) for cidr in ANYCAST_CIDRS]
ANYCAST_KEYWORDS = ("pages.dev", "workers.dev", "cloudflare.com", "speedtest.net", "visa.com", "csgo.com")

def is_anycast_node(proxy: dict) -> bool:
    """判断节点是否属于 Cloudflare / WARP 等 Anycast 任播节点（出口地区随访问者位置漂移）"""
    if proxy.get("type") == "wireguard":
        return True

    server = str(proxy.get("server", "")).lower()
    sni = str(proxy.get("sni") or proxy.get("servername") or "").lower()
    host = ""
    ws_opts = proxy.get("ws-opts")
    if isinstance(ws_opts, dict) and isinstance(ws_opts.get("headers"), dict):
        host = str(ws_opts["headers"].get("Host", "")).lower()

    for kw in ANYCAST_KEYWORDS:
        if kw in server or kw in sni or kw in host:
            return True

    try:
        ip = ipaddress.ip_address(server)
        return any(ip in net for net in ANYCAST_NETWORKS)
    except ValueError:
        return False

def is_clean_string(s: str) -> bool:
    """检查字符串是否含有 C0/C1 控制字符或非法字符（Go YAML 严格禁止）"""
    for ch in s:
        code = ord(ch)
        # 0x00-0x1F (除 \t \n \r 外) 以及 0x7F-0x9F 为 Unicode 控制字符
        if (code < 32 and ch not in "\t\n\r") or (0x7F <= code <= 0x9F):
            return False
    return True

def sanitize_proxy(proxy: dict) -> dict | None:
    """过滤并深度清洗单个代理节点中的非法字符，同时剔除不支持 UDP 的纯 HTTP 代理"""
    if str(proxy.get("type", "")).lower() == "http":
        # 纯 HTTP 代理不支持 UDP，在 TUN 模式下会导致 QUIC/UDP 流量直接回退为 DIRECT 暴露真实 IP
        return None
    clean_p = {}
    for k, v in proxy.items():
        if isinstance(v, str):
            if not is_clean_string(v):
                # 如果是节点关键字段（如 sni、name、server）包含不可修复的控制字符，则直接丢弃该节点
                return None
            clean_p[k] = v
        elif isinstance(v, dict):
            # 嵌套对象（如 reality-opts, ws-opts）
            nested = {}
            for nk, nv in v.items():
                if isinstance(nv, str):
                    if not is_clean_string(nv):
                        return None
                    nested[nk] = nv
                else:
                    nested[nk] = nv
            clean_p[k] = nested
        else:
            clean_p[k] = v
    return clean_p

def get_node_region(name: str) -> str:
    # 严格只取第一段前缀，排除尾部 |GM-US 导致加拿大、德国、墨西哥等节点被误判为美国
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

    raw_proxies = data.get("proxies", []) if data else []
    if not raw_proxies:
        print("No proxies found in output/all.yaml")
        sys.exit(0)

    # 1. 深度清洗并剔除所有包含 C0/C1 控制字符的破损脏节点（彻底消除 yaml: control characters are not allowed）
    proxies = []
    discarded_count = 0
    for p in raw_proxies:
        if not isinstance(p, dict) or "name" not in p:
            continue
        cleaned = sanitize_proxy(p)
        if cleaned is not None:
            proxies.append(cleaned)
        else:
            discarded_count += 1

    print(f"Sanitization complete: kept {len(proxies)} clean proxies, discarded {discarded_count} corrupted proxies.")

    # 同步把清洗干净的纯净节点写回 output/all.yaml，保证作为 Provider 时同样不报错
    with open("output/all.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"proxies": proxies}, f, allow_unicode=True, sort_keys=False)

    proxy_names = [p["name"] for p in proxies]

    # 识别并标记 Anycast 任播节点（用于兜底，防止优先选中导致地区漂移）
    anycast_names = {p["name"] for p in proxies if is_anycast_node(p)}
    fixed_proxy_names = [n for n in proxy_names if n not in anycast_names]

    # 美国节点分为两层：1) 固定美国原生 IP（首选）；2) 美区标签的 Anycast 任播节点（兜底）
    fixed_us_nodes = [n for n in fixed_proxy_names if get_node_region(n) == "US"]
    anycast_us_nodes = [n for n in proxy_names if n in anycast_names and get_node_region(n) == "US"]

    # 其他国家/地区仅使用固定出口 IP 的节点
    sg_nodes = [n for n in fixed_proxy_names if get_node_region(n) == "SG"]
    jp_nodes = [n for n in fixed_proxy_names if get_node_region(n) == "JP"]
    hk_nodes = [n for n in fixed_proxy_names if get_node_region(n) == "HK"]
    tw_nodes = [n for n in fixed_proxy_names if get_node_region(n) == "TW"]
    uk_nodes = [n for n in fixed_proxy_names if get_node_region(n) == "UK"]
    kr_nodes = [n for n in fixed_proxy_names if get_node_region(n) == "KR"]

    # Gemini 专属节点：同样遵循“美区原生 GM 优先，无可用时才用美区任播 GM 兜底”
    fixed_gemini_nodes = [n for n in fixed_us_nodes if "GM" in n] or list(fixed_us_nodes)
    anycast_gemini_nodes = [n for n in anycast_us_nodes if "GM" in n] or list(anycast_us_nodes)

    auto_groups = []

    # 全球自动优选（传入独立浅拷贝，避免 PyYAML 输出 &id001 别名导致第三方解析器报错）
    auto_groups.append({
        "name": "🚀 全球自动优选",
        "type": "url-test",
        "url": "https://www.gstatic.com/generate_204",
        "interval": 60,
        "tolerance": 50,
        "proxies": list(proxy_names),
    })

    # 美国分层优选：原生固定 IP 优先 -> 任播兜底
    us_tier_groups = []
    if fixed_us_nodes:
        auto_groups.append({
            "name": "🇺🇸 美国-原生优选",
            "type": "url-test",
            "url": "https://www.gstatic.com/generate_204",
            "interval": 60,
            "tolerance": 50,
            "proxies": list(fixed_us_nodes),
        })
        us_tier_groups.append("🇺🇸 美国-原生优选")

    if anycast_us_nodes:
        auto_groups.append({
            "name": "🇺🇸 美国-任播兜底",
            "type": "url-test",
            "url": "https://www.gstatic.com/generate_204",
            "interval": 60,
            "tolerance": 50,
            "proxies": list(anycast_us_nodes),
        })
        us_tier_groups.append("🇺🇸 美国-任播兜底")

    available_country_group_names = []
    if us_tier_groups:
        auto_groups.append({
            "name": "🇺🇸 美国-自动优选",
            "type": "fallback",
            "url": "https://www.gstatic.com/generate_204",
            "interval": 60,
            "proxies": us_tier_groups,
        })
        available_country_group_names.append("🇺🇸 美国-自动优选")

    # 其他国家自动优选组（100% 纯净固定 IP 该国节点）
    country_definitions = [
        ("🇸🇬 新加坡-自动优选", sg_nodes),
        ("🇯🇵 日本-自动优选", jp_nodes),
        ("🇭🇰 香港-自动优选", hk_nodes),
        ("🇹🇼 台湾-自动优选", tw_nodes),
        ("🇬🇧 英国-自动优选", uk_nodes),
        ("🇰🇷 韩国-自动优选", kr_nodes),
    ]

    for group_name, nodes in country_definitions:
        if nodes:
            auto_groups.append({
                "name": group_name,
                "type": "url-test",
                "url": "https://www.gstatic.com/generate_204",
                "interval": 60,
                "tolerance": 50,
                "proxies": list(nodes),
            })
            available_country_group_names.append(group_name)

    # Gemini 分层优选：美区原生 Gemini 优先 -> 美区任播 Gemini 兜底
    gemini_tier_groups = []
    if fixed_gemini_nodes:
        auto_groups.append({
            "name": "🤖 Gemini-原生优选",
            "type": "url-test",
            "url": "https://www.gstatic.com/generate_204",
            "interval": 60,
            "tolerance": 50,
            "proxies": list(fixed_gemini_nodes),
        })
        gemini_tier_groups.append("🤖 Gemini-原生优选")

    if anycast_gemini_nodes:
        auto_groups.append({
            "name": "🤖 Gemini-任播兜底",
            "type": "url-test",
            "url": "https://www.gstatic.com/generate_204",
            "interval": 60,
            "tolerance": 50,
            "proxies": list(anycast_gemini_nodes),
        })
        gemini_tier_groups.append("🤖 Gemini-任播兜底")

    gemini_group = {
        "name": "🤖 Gemini-专属专线",
        "type": "fallback",
        "url": "https://www.gstatic.com/generate_204",
        "interval": 60,
        "proxies": gemini_tier_groups if gemini_tier_groups else list(proxy_names),
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
            "AND,((NETWORK,UDP),(DST-PORT,443)),REJECT",
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

    print(f"Successfully generated output/clash.yaml with {len(proxy_names)} clean nodes!")
    print(f"US Fixed: {len(fixed_us_nodes)} + Anycast Fallback: {len(anycast_us_nodes)} | Gemini Fixed: {len(fixed_gemini_nodes)} + Anycast Fallback: {len(anycast_gemini_nodes)} | SG: {len(sg_nodes)}, JP: {len(jp_nodes)}, HK: {len(hk_nodes)}, TW: {len(tw_nodes)}, UK: {len(uk_nodes)}, KR: {len(kr_nodes)}")

if __name__ == "__main__":
    main()
