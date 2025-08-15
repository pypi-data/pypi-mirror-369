import asyncio
import json
import platform
import socket
import subprocess
import time
from typing import List, Tuple

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("network-tester")


async def _tcp_connect_once(host: str, port: int, timeout_seconds: float) -> Tuple[bool, float, str]:
	start = time.perf_counter()
	try:
		reader, writer = await asyncio.wait_for(
			asyncio.open_connection(host=host, port=port), timeout=timeout_seconds
		)
		latency_ms = (time.perf_counter() - start) * 1000.0
		writer.close()
		await writer.wait_closed()
		return True, latency_ms, "ok"
	except Exception as exc:  # noqa: BLE001
		latency_ms = (time.perf_counter() - start) * 1000.0
		return False, latency_ms, f"{type(exc).__name__}: {exc}"


@mcp.tool("tcp_check")
async def tcp_check(host: str, port: int, timeout_seconds: float = 2.0) -> str:
	"""检查 TCP 端口连通性（单次连接）。

	参数:
	- host: 目标主机名或 IP
	- port: 目标端口
	- timeout_seconds: 连接超时秒数，默认 2.0

	返回: JSON 字符串，包含 {reachable, latency_ms, error}
	"""
	success, latency_ms, error_message = await _tcp_connect_once(host, port, timeout_seconds)
	result = {
		"host": host,
		"port": port,
		"reachable": success,
		"latency_ms": round(latency_ms, 2),
		"error": None if success else error_message,
	}
	return json.dumps(result, ensure_ascii=False)


@mcp.tool("tcp_ping")
async def tcp_ping(
	host: str,
	port: int,
	count: int = 4,
	interval_seconds: float = 0.2,
	timeout_seconds: float = 2.0,
) -> str:
	"""多次 TCP 连接探测，统计成功率与时延。

	参数:
	- host: 目标主机名或 IP
	- port: 目标端口
	- count: 探测次数，默认 4
	- interval_seconds: 每次探测间隔秒数，默认 0.2
	- timeout_seconds: 单次连接超时秒数，默认 2.0

	返回: JSON 字符串，包含汇总统计与每次结果明细
	"""
	attempt_results = []
	for attempt_index in range(1, max(1, int(count)) + 1):
		success, latency_ms, error_message = await _tcp_connect_once(host, port, timeout_seconds)
		attempt_results.append({
			"attempt": attempt_index,
			"reachable": success,
			"latency_ms": round(latency_ms, 2),
			"error": None if success else error_message,
		})
		if attempt_index < count:
			await asyncio.sleep(max(0.0, float(interval_seconds)))

	latencies = [r["latency_ms"] for r in attempt_results if r["reachable"]]
	summary = {
		"host": host,
		"port": port,
		"count": count,
		"success": sum(1 for r in attempt_results if r["reachable"]),
		"failure": sum(1 for r in attempt_results if not r["reachable"]),
		"min_ms": round(min(latencies), 2) if latencies else None,
		"avg_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
		"max_ms": round(max(latencies), 2) if latencies else None,
		"results": attempt_results,
	}
	return json.dumps(summary, ensure_ascii=False)


@mcp.tool("dns_resolve")
async def dns_resolve(host: str) -> str:
	"""解析主机名的 A/AAAA 记录，返回所有可用地址。

	参数:
	- host: 需要解析的主机名

	返回: JSON 字符串，包含地址列表与族别
	"""
	addresses: List[dict] = []
	try:
		infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
		for family, _, _, _, sockaddr in infos:
			ip = sockaddr[0]
			version = "IPv6" if family == socket.AF_INET6 else "IPv4" if family == socket.AF_INET else str(family)
			addresses.append({"ip": ip, "family": version})
		# 去重并保持顺序
		seen = set()
		unique_addresses = []
		for addr in addresses:
			key = (addr["ip"], addr["family"])
			if key not in seen:
				seen.add(key)
				unique_addresses.append(addr)
		return json.dumps({"host": host, "addresses": unique_addresses}, ensure_ascii=False)
	except Exception as exc:  # noqa: BLE001
		return json.dumps({"host": host, "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False)


@mcp.tool("system_ping")
async def system_ping(target: str, count: int = 4, timeout_seconds: float = 2.0, size: int = 32) -> str:
	"""调用系统 ping 命令进行 ICMP 探测（可能需要权限）。

	参数:
	- target: 目标主机名或 IP
	- count: 次数，默认 4
	- timeout_seconds: 超时秒数，默认 2.0
	- size: 数据包大小，默认 32（Windows）

	返回: 文本输出或错误 JSON
	"""
	system_name = platform.system().lower()
	try:
		if "windows" in system_name:
			cmd = [
				"ping",
				"-n", str(int(count)),
				"-w", str(int(timeout_seconds * 1000)),
				"-l", str(int(size)),
				target,
			]
		else:
			cmd = [
				"ping",
				"-c", str(int(count)),
				"-W", str(int(timeout_seconds)),
				target,
			]

		proc = await asyncio.create_subprocess_exec(
			*cmd,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE,
		)
		stdout_bytes, stderr_bytes = await proc.communicate()
		stdout_text = stdout_bytes.decode(errors="ignore")
		stderr_text = stderr_bytes.decode(errors="ignore")
		if proc.returncode == 0:
			return stdout_text.strip()
		return json.dumps({
			"target": target,
			"error": stderr_text.strip() or stdout_text.strip() or f"exit={proc.returncode}",
		}, ensure_ascii=False)
	except FileNotFoundError:
		return json.dumps({"error": "系统未找到 ping 命令"}, ensure_ascii=False)
	except Exception as exc:  # noqa: BLE001
		return json.dumps({"error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False)


def main() -> None:
	mcp.run()


if __name__ == "__main__":
	main()
