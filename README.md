# 全球高可用节点自动测速与分流订阅池 (Multi-Country Gemini Auto-Nodes)

<div align="center">

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/Jeffery518/us-gemini-nodes/update.yml?branch=main&label=%E4%BA%91%E7%AB%AF%E6%B5%8B%E9%80%9F%E7%8A%B6%E6%80%81&style=flat-square)
![更新频率](https://img.shields.io/badge/%E6%9B%B4%E6%96%B0%E9%A2%91%E7%8E%87-%E6%AF%8F%202%20%E5%B0%8F%E6%97%B6-blue?style=flat-square)
[![订阅访问人次](https://komarev.com/ghpvc/?username=Jeffery518-us-gemini-nodes&label=%E8%AE%A2%E9%98%85%E8%AE%BF%E9%97%AE%E4%BA%BA%E6%AC%A1&color=007ec6&style=flat-square)](https://github.com/Jeffery518/us-gemini-nodes)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FJeffery518%2Fus-gemini-nodes&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=%E8%AE%A2%E9%98%85%E6%80%BB%E4%BA%BA%E6%AC%A1&edge_flat=false)](https://hits.seeyoufarm.com)
![开源协议](https://img.shields.io/badge/License-MIT-green?style=flat-square)

<p>基于 <b>GitHub Actions</b> + <b>subs-check</b> 云端全自动化构建的高可用节点订阅池。<br>每 2 小时自动抓取全球数百个上游公开源、高并发测速清洗、淘汰拥塞与死节点，专为 <b>Google Gemini、Antigravity</b> 与日常网络加速打造。</p>

</div>

---

### ✨ 核心特性

* ⚡ **超高新鲜度**：云端定时器每 **2 小时** 自动抓取并重测，彻底解决公开节点易死、失效堆积的问题。
* 🌍 **按国家专属自动优选**：内置分类引擎，支持 **「🇺🇸 美国-自动优选」**、**「🇸🇬 新加坡-自动优选」**、**「🇯🇵 日本-自动优选」**、**「🇭🇰 香港-自动优选」**、**「🇹🇼 台湾-自动优选」** 等独立测速组。
* 🤖 **Gemini / AI 专属专线**：对所有节点进行 IP 风险与 Gemini 解锁检测，并在分流规则中将 Antigravity、Gemini 域名精准导流至解锁节点。
* 🛡️ **60s 故障无感漂移**：策略组健康检测设为 60 秒。使用任意「自动优选」组时，一旦某个节点暴毙，客户端内核在 60 秒内静默切换到下一个最快可用节点，完全无感知。
* 📱 **全平台开箱即用**：自动生成手机端与电脑端适用的标准完整配置（包含策略组与分流规则），导入即用。

---

### 🔗 订阅链接获取

#### 1. 完整客户端配置（推荐：手机端 / 电脑端直接导入）
> 包含端口设置、全套按国自动优选策略组、Gemini 专线分流规则，导入后直接可用。

* **CDN 加速直链（国内网络强烈推荐，免翻直连）**：
  ```text
  https://ghfast.top/https://raw.githubusercontent.com/Jeffery518/us-gemini-nodes/main/output/clash.yaml
  ```
* **GitHub 原始直链**：
  ```text
  https://raw.githubusercontent.com/Jeffery518/us-gemini-nodes/main/output/clash.yaml
  ```

#### 2. 纯节点池（用于挂载为 Proxy Provider 或通过覆写脚本合并进主力订阅）
* **CDN 加速直链**：
  ```text
  https://ghfast.top/https://raw.githubusercontent.com/Jeffery518/us-gemini-nodes/main/output/all.yaml
  ```
* **GitHub 原始直链**：
  ```text
  https://raw.githubusercontent.com/Jeffery518/us-gemini-nodes/main/output/all.yaml
  ```

---

### 🚀 客户端使用教程

#### 一、手机端（Clash for Android / Clash Meta / FlClash）

1. 复制上方的 **完整客户端配置（CDN 加速直链）**。
2. 打开手机 **Clash** 客户端，点击 **「配置」**（Profiles）→ 点击右上角 **「+」**（新建配置）。
3. 选择 **「URL」** 方式导入。
4. **名称** 填写 `全球节点优选池`，**URL** 粘贴复制的链接。
5. **自动更新间隔** 设置为 `120` 分钟（与云端 2 小时清洗保持同步）。
6. 点击右上角 **保存并下载**。
7. 返回主界面勾选此配置，进入 **「代理」** 页面即可看到：
   * `🚀 全球自动优选`
   * `🇺🇸 美国-自动优选`
   * `🇸🇬 新加坡-自动优选`
   * `🇯🇵 日本-自动优选` 等独立分组。

---

#### 二、电脑端 Clash Party (Mihomo Party)

**方式 A：直接作为独立订阅导入（最简单）**
1. 打开 **Clash Party**，点击左侧菜单栏的 **「订阅」**（Profiles）图标。
2. 在顶部的「输入订阅 URL」输入框中，粘贴 **完整客户端配置 CDN 直链**。
3. 点击右侧 **「导入」/「下载」**。
4. 选中该卡片设为当前配置，并在主界面开启 **「系统代理」** 或 **「TUN 模式」** 即可。

**方式 B：通过 JS 覆写无缝嵌入现有主力订阅**
如果你电脑上已有主力机场，希望平时上网走自己的节点，仅让 Gemini / AI 流量走该免费池：
1. 打开 **Clash Party**，点击左侧 **「覆写」**（Overrides）。
2. 点击右上角 **「新建」**，类型选择 **JavaScript**，名称填 `Gemini全球多国节点池`。
3. 粘贴以下脚本并保存：

```javascript
function main(config) {
  if (!config['proxy-providers']) config['proxy-providers'] = {};
  config['proxy-providers']['gemini_nodes'] = {
    type: 'http',
    url: 'https://ghfast.top/https://raw.githubusercontent.com/Jeffery518/us-gemini-nodes/main/output/all.yaml',
    path: './providers/gemini_nodes.yaml',
    interval: 3600,
    'health-check': {
      enable: true,
      url: 'https://www.gstatic.com/generate_204',
      interval: 60,
    },
  };

  if (!Array.isArray(config['proxy-groups'])) config['proxy-groups'] = [];
  config['proxy-groups'].unshift({
    name: 'Gemini-专属优选',
    type: 'url-test',
    use: ['gemini_nodes'],
    url: 'https://www.gstatic.com/generate_204',
    interval: 60,
    tolerance: 50,
  });

  if (!Array.isArray(config['rules'])) config['rules'] = [];
  const geminiRules = [
    'DOMAIN-KEYWORD,antigravity,Gemini-专属优选',
    'GEOSITE,google-deepmind,Gemini-专属优选',
    'DOMAIN-SUFFIX,gemini.google.com,Gemini-专属优选',
    'DOMAIN-SUFFIX,aistudio.google.com,Gemini-专属优选',
    'DOMAIN-SUFFIX,generativelanguage.googleapis.com,Gemini-专属优选',
  ];
  config['rules'] = [...geminiRules, ...config['rules']];
  return config;
}
```
4. 保存后将卡片右下角的 **「全局启用」开关打开（变蓝）**，刷新主配置即可。

---

### 💡 核心使用技巧（防止节点失效与断网）

1. **务必选择「自动优选」分组，不要手动单选具体节点**：
   * 公开节点的寿命波动较大，如果手动锁定某一个固定节点，该节点一旦被运营商断流，网络就会卡死。
   * 选择 **「🚀 全球自动优选」** 或 **「🇺🇸 美国-自动优选」** 等自动组，客户端底层内核会在 60 秒内自动探活并漂移至当前最快的活着节点，实现 100% 无感换线。
2. **觉得网络卡顿或节点变灰时**：
   * 在订阅卡片上**手动点击一次刷新图标**，即可立即拉取云端最新生成的节点名单。

---

### 📊 访问量与使用统计

本项目订阅链接自带实时访问统计，徽章数据由第三方计数服务动态统计：
* **当前总使用/访问人次**：可在上方页面顶部实时查看 `订阅访问人次` 徽章。
* 统计数据每次客户端拉取订阅或网页访问均会自动自增计次。

---

### ⚖️ 免责声明
* 本项目抓取的所有节点均来源于互联网公开订阅池，本项目不对节点的安全性、可用性及数据完整性作任何担保。
* 请遵守当地法律法规，严禁利用本项目进行任何非法活动。
