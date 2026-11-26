#!/usr/bin/env python3
"""
从 GitHub GraphQL API 拉取公开数据，生成与主页同风格的数据卡片 assets/generated/stats.svg

用法：
  GITHUB_TOKEN=xxx python3 scripts/update_stats.py <用户名>
  python3 scripts/update_stats.py --mock         # 用随机假数据本地预览，不访问网络
仅依赖 Python 标准库。
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "assets"))
import generate as g  # noqa: E402

API = "https://api.github.com/graphql"
CST = dt.timezone(dt.timedelta(hours=8))

Q_MAIN = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""

Q_REPOS = """
query($login: String!, $after: String) {
  user(login: $login) {
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      pageInfo { hasNextPage endCursor }
      nodes { stargazerCount }
    }
  }
}"""


def gql(query, variables, token):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats-script"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if res.get("errors"):
        raise RuntimeError(json.dumps(res["errors"], ensure_ascii=False))
    if not res.get("data", {}).get("user"):
        raise RuntimeError("找不到该用户")
    return res["data"]["user"]


def fetch(login, token):
    cc = gql(Q_MAIN, {"login": login}, token)["contributionsCollection"]
    stars, after = 0, None
    while True:
        repos = gql(Q_REPOS, {"login": login, "after": after}, token)["repositories"]
        stars += sum(n["stargazerCount"] for n in repos["nodes"])
        if not repos["pageInfo"]["hasNextPage"]:
            break
        after = repos["pageInfo"]["endCursor"]
    days = [(d["date"], d["contributionCount"])
            for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return {
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "stars": stars,
        "days": days,
    }


def mock():
    random.seed(431)
    start = dt.date.today() - dt.timedelta(days=370)
    days, level = [], 3.0
    for i in range(371):
        level = max(0.0, min(14.0, level + random.uniform(-1.6, 1.8)))
        c = 0 if random.random() < 0.22 else int(random.random() * level)
        days.append(((start + dt.timedelta(days=i)).isoformat(), c))
    total = sum(c for _, c in days[-365:])
    return {"total": total, "commits": int(total * .78), "prs": 46, "issues": 19, "stars": 128, "days": days}


def summarize(raw):
    days = sorted(raw["days"])
    counts = [c for _, c in days]
    # 最长连续
    best = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        best = max(best, run)
    # 当前连续（今天还没提交不算断）
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    cur = 0
    while i >= 0 and counts[i] > 0:
        cur += 1
        i -= 1
    # 按周汇总（最后 52 周，以最后一天为结尾向前每 7 天一组）
    weeks, months, prev_month = [], [], None
    tail = days[-52 * 7:]
    for w in range(len(tail) // 7):
        chunk = tail[w * 7:(w + 1) * 7]
        weeks.append(sum(c for _, c in chunk))
        month = int(chunk[0][0][5:7])
        if prev_month is not None and month != prev_month:
            months.append((w, f"{month}月"))
        prev_month = month
    return {
        "total": raw["total"], "commits": raw["commits"], "prs": raw["prs"],
        "issues": raw["issues"], "stars": raw["stars"],
        "cur_streak": cur, "max_streak": best,
        "active_days": sum(1 for c in counts[-365:] if c > 0),
        "weeks": weeks, "months": months,
        "updated": dt.datetime.now(CST).strftime("%Y-%m-%d"),
    }


def main():
    if "--mock" in sys.argv:
        raw = mock()
    else:
        login = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GITHUB_REPOSITORY_OWNER", "")).strip()
        token = os.environ.get("GITHUB_TOKEN", "").strip()
        if not login or not token:
            sys.exit("需要用户名参数和 GITHUB_TOKEN 环境变量")
        raw = fetch(login, token)
    data = summarize(raw)
    g.stats_card(data)
    print("stats.svg 已更新：", {k: v for k, v in data.items() if k not in ("weeks", "months")})


if __name__ == "__main__":
    main()
