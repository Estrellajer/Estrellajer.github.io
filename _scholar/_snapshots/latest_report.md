# Scholar Monitor Report

**Run:** 2026-06-25 04:20 UTC  |  **Total:** 57  |  Events 3  |  RSS 0  |  CHG 1  |  FIRST 0  |  OK 55  |  ERR 1

---
## Activity Feed (3)

- **K.I.S.S** [Kimi]: dnsmasq 的默认上游是静态配置，并不是在所有网络环境中都能直接用 114 了事，尤其是在一些需要认证的环境中 需要改系统的 DNS 配置，同时每次系统更新之后又要重新改一遍 直到昨天我才知道 BSD 系支持一个按域名设置 resolv
- **K.I.S.S** [Kimi]: 之前我一直使用 dnsmasq 实现按域名切换解析，这样的话有几个问题：
- **K.I.S.S** [Kimi]: 在工作用的电脑上，为了访问公司内网，需要让内网域名走公司的 DNS 服务器，而其他域名走公共 DNS 服务器。

---
## Needs Attention (1)

- [苏剑林 - 科学空间](https://kexue.fm/): `Fetch/extract failed: HTTPSConnectionPool(host='kexue.fm', port=443): Max retries exceeded with url: / (Caused by ConnectTimeoutError(<HTTPSConnection(host='kexue.fm', port=443) at 0x7fab41b4c090>, 'Connection to kexue.fm timed out. (connect timeout=30)'))`