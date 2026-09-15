from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
from urllib.parse import urlparse

from bs4 import BeautifulSoup, NavigableString

from .audit import AuditLogger
from .models import BloggerLinkJob

if TYPE_CHECKING:
    from .google_blogger import GoogleBloggerConnector


class BloggerAutomationError(RuntimeError):
    pass


@dataclass
class LinkInsertionResult:
    html: str
    changed: bool
    reason: str


@dataclass
class JobRunResult:
    scanned: int = 0
    changed: int = 0
    skipped_existing: int = 0
    skipped_no_match: int = 0


def validate_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise BloggerAutomationError("link_url must be an absolute http/https URL")


def insert_link_once(html: str, target_text: str, link_url: str, anchor_text: str | None = None) -> LinkInsertionResult:
    if not target_text:
        raise BloggerAutomationError("target_text must not be empty")
    validate_http_url(link_url)
    anchor_text = anchor_text or target_text
    soup = BeautifulSoup(html or "", "html.parser")

    for anchor in soup.find_all("a", href=True):
        if str(anchor.get("href", "")) == link_url:
            return LinkInsertionResult(str(soup), False, "link_already_present")

    ignored_parents = {"a", "script", "style", "code", "pre", "textarea"}
    for text_node in soup.find_all(string=True):
        parent = getattr(text_node, "parent", None)
        if parent is None or getattr(parent, "name", None) in ignored_parents:
            continue
        text = str(text_node)
        index = text.find(target_text)
        if index < 0:
            continue

        before = text[:index]
        after = text[index + len(target_text):]
        new_nodes: list[Any] = []
        if before:
            new_nodes.append(NavigableString(before))
        link = soup.new_tag("a", href=link_url)
        link.string = anchor_text
        new_nodes.append(link)
        if after:
            new_nodes.append(NavigableString(after))
        text_node.replace_with(*new_nodes)
        return LinkInsertionResult(str(soup), True, "inserted")

    return LinkInsertionResult(str(soup), False, "target_not_found")


def run_link_job(connector: "GoogleBloggerConnector", job: BloggerLinkJob, *, dry_run: bool, audit: AuditLogger | None = None) -> JobRunResult:
    audit = audit or AuditLogger()
    result = JobRunResult()
    audit.write("blogger_job_start", job_id=job.id, dry_run=dry_run, blog_id=job.blog_id)
    posts = connector.list_posts(job.blog_id, status=job.status, max_posts=job.max_posts)
    for post in posts:
        result.scanned += 1
        post_id = str(post.get("id", ""))
        content = str(post.get("content", ""))
        insertion = insert_link_once(content, job.target_text, job.link_url, job.anchor_text)
        if insertion.reason == "link_already_present":
            result.skipped_existing += 1
            continue
        if not insertion.changed:
            result.skipped_no_match += 1
            continue
        if not dry_run:
            connector.patch_post_content(job.blog_id, post_id, insertion.html)
        result.changed += 1
        audit.write("blogger_post_change", job_id=job.id, post_id=post_id, dry_run=dry_run)
    audit.write("blogger_job_finish", job_id=job.id, dry_run=dry_run, scanned=result.scanned, changed=result.changed, skipped_existing=result.skipped_existing, skipped_no_match=result.skipped_no_match)
    return result
