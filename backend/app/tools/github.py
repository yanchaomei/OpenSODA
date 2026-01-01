"""
GitHub API 工具封装
提供 GitHub 仓库的基本信息和数据获取能力
"""
import httpx
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
from app.core.config import settings


class GitHubTool:
    """
    GitHub API 工具类
    
    使用 GitHub REST API 获取仓库信息
    文档: https://docs.github.com/en/rest
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenSource-Copilot"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=30.0
        )
    
    async def get_repo_info(self, repo: str) -> Optional[Dict[str, Any]]:
        """
        获取仓库基本信息
        
        Args:
            repo: 仓库路径，如 "apache/dubbo"
            
        Returns:
            仓库信息字典
        """
        url = f"{self.BASE_URL}/repos/{repo}"
        
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name"),
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "language": data.get("language"),
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "open_issues": data.get("open_issues_count", 0),
                    "watchers": data.get("watchers_count", 0),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "pushed_at": data.get("pushed_at"),
                    "homepage": data.get("homepage"),
                    "license": data.get("license", {}).get("name") if data.get("license") else None,
                    "topics": data.get("topics", []),
                    "default_branch": data.get("default_branch"),
                    "archived": data.get("archived", False),
                }
            elif response.status_code == 404:
                return None
            else:
                print(f"GitHub API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching repo info: {e}")
            return None
    
    async def get_contributors(self, repo: str, per_page: int = 30) -> List[Dict[str, Any]]:
        """
        获取仓库贡献者列表
        
        Args:
            repo: 仓库路径
            per_page: 每页数量
            
        Returns:
            贡献者列表
        """
        url = f"{self.BASE_URL}/repos/{repo}/contributors"
        params = {"per_page": per_page}
        
        try:
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                return [
                    {
                        "login": c.get("login"),
                        "contributions": c.get("contributions"),
                        "avatar_url": c.get("avatar_url"),
                    }
                    for c in response.json()
                ]
            return []
        except Exception as e:
            print(f"Error fetching contributors: {e}")
            return []
    
    async def get_recent_issues(self, repo: str, state: str = "all", per_page: int = 20) -> List[Dict[str, Any]]:
        """
        获取最近的 Issues
        
        Args:
            repo: 仓库路径
            state: Issue 状态 (open, closed, all)
            per_page: 每页数量
            
        Returns:
            Issue 列表
        """
        url = f"{self.BASE_URL}/repos/{repo}/issues"
        params = {
            "state": state,
            "per_page": per_page,
            "sort": "updated",
            "direction": "desc"
        }
        
        try:
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                return [
                    {
                        "number": i.get("number"),
                        "title": i.get("title"),
                        "state": i.get("state"),
                        "created_at": i.get("created_at"),
                        "updated_at": i.get("updated_at"),
                        "labels": [l.get("name") for l in i.get("labels", [])],
                        "is_pr": "pull_request" in i,
                    }
                    for i in response.json()
                ]
            return []
        except Exception as e:
            print(f"Error fetching issues: {e}")
            return []
    
    async def get_recent_prs(self, repo: str, state: str = "all", per_page: int = 20) -> List[Dict[str, Any]]:
        """
        获取最近的 Pull Requests
        
        Args:
            repo: 仓库路径
            state: PR 状态 (open, closed, all)
            per_page: 每页数量
            
        Returns:
            PR 列表
        """
        url = f"{self.BASE_URL}/repos/{repo}/pulls"
        params = {
            "state": state,
            "per_page": per_page,
            "sort": "updated",
            "direction": "desc"
        }
        
        try:
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                return [
                    {
                        "number": pr.get("number"),
                        "title": pr.get("title"),
                        "state": pr.get("state"),
                        "created_at": pr.get("created_at"),
                        "merged_at": pr.get("merged_at"),
                        "user": pr.get("user", {}).get("login"),
                    }
                    for pr in response.json()
                ]
            return []
        except Exception as e:
            print(f"Error fetching PRs: {e}")
            return []
    
    async def get_commit_activity(self, repo: str) -> List[Dict[str, Any]]:
        """
        获取提交活动统计（最近一年，按周统计）
        
        Args:
            repo: 仓库路径
            
        Returns:
            每周提交统计
        """
        url = f"{self.BASE_URL}/repos/{repo}/stats/commit_activity"
        
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching commit activity: {e}")
            return []
    
    async def get_languages(self, repo: str) -> Dict[str, int]:
        """
        获取仓库使用的编程语言统计
        
        Args:
            repo: 仓库路径
            
        Returns:
            语言: 字节数 的字典
        """
        url = f"{self.BASE_URL}/repos/{repo}/languages"
        
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error fetching languages: {e}")
            return {}
    
    async def search_good_first_issues(self, repo: str) -> List[Dict[str, Any]]:
        """
        搜索适合新手的 Issues (good first issue)
        
        Args:
            repo: 仓库路径
            
        Returns:
            适合新手的 Issue 列表
        """
        url = f"{self.BASE_URL}/search/issues"
        params = {
            "q": f"repo:{repo} is:issue is:open label:\"good first issue\"",
            "per_page": 20
        }
        
        try:
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                items = response.json().get("items", [])
                return [
                    {
                        "number": i.get("number"),
                        "title": i.get("title"),
                        "html_url": i.get("html_url"),
                        "created_at": i.get("created_at"),
                        "labels": [l.get("name") for l in i.get("labels", [])],
                    }
                    for i in items
                ]
            return []
        except Exception as e:
            print(f"Error searching good first issues: {e}")
            return []
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


# LangChain Tool 装饰器版本
@tool
async def get_github_repo_info(repo: str) -> str:
    """
    获取 GitHub 仓库的基本信息，包括 Star 数、Fork 数、描述等。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"，例如 "apache/dubbo"
        
    Returns:
        仓库的基本信息
    """
    tool_instance = GitHubTool()
    try:
        info = await tool_instance.get_repo_info(repo)
        
        if info is None:
            return f"未找到仓库 {repo}，请检查仓库路径是否正确。"
        
        result = f"""仓库 {info['full_name']} 的基本信息：
- 描述: {info.get('description') or '无'}
- 主要语言: {info.get('language') or '未知'}
- Star 数: {info['stars']:,}
- Fork 数: {info['forks']:,}
- 开放 Issue 数: {info['open_issues']:,}
- 许可证: {info.get('license') or '未知'}
- 最后更新: {info.get('updated_at', '未知')}
- 是否归档: {'是' if info.get('archived') else '否'}"""
        
        if info.get('topics'):
            result += f"\n- 标签: {', '.join(info['topics'][:10])}"
        
        return result
    finally:
        await tool_instance.close()


@tool
async def get_github_contributors(repo: str) -> str:
    """
    获取 GitHub 仓库的主要贡献者列表。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"
        
    Returns:
        贡献者列表及其贡献数量
    """
    tool_instance = GitHubTool()
    try:
        contributors = await tool_instance.get_contributors(repo, per_page=10)
        
        if not contributors:
            return f"未能获取仓库 {repo} 的贡献者信息。"
        
        result = f"仓库 {repo} 的 Top 10 贡献者：\n"
        for i, c in enumerate(contributors, 1):
            result += f"{i}. {c['login']} - {c['contributions']} 次贡献\n"
        
        return result
    finally:
        await tool_instance.close()


@tool
async def find_good_first_issues(repo: str) -> str:
    """
    查找仓库中适合新手贡献的 Issues（标记为 good first issue）。
    
    Args:
        repo: 仓库路径，格式为 "owner/repo"
        
    Returns:
        适合新手的 Issue 列表
    """
    tool_instance = GitHubTool()
    try:
        issues = await tool_instance.search_good_first_issues(repo)
        
        if not issues:
            return f"仓库 {repo} 目前没有标记为 'good first issue' 的开放 Issue。"
        
        result = f"仓库 {repo} 中适合新手的 Issues：\n"
        for issue in issues[:10]:
            result += f"- #{issue['number']}: {issue['title']}\n"
            result += f"  链接: {issue['html_url']}\n"
        
        return result
    finally:
        await tool_instance.close()

