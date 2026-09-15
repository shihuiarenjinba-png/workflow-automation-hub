import unittest

from automation_hub.blogger_automation import insert_link_once, run_link_job
from automation_hub.models import BloggerLinkJob


class FakeConnector:
    def __init__(self, posts):
        self.posts = posts
        self.patched = []

    def list_posts(self, blog_id, status="LIVE", max_posts=50):
        return self.posts[:max_posts]

    def patch_post_content(self, blog_id, post_id, content):
        self.patched.append((blog_id, post_id, content))
        return {"id": post_id}


class NullAudit:
    def write(self, event, **fields):
        pass


class BloggerAutomationTests(unittest.TestCase):
    def test_inserts_first_visible_match(self):
        result = insert_link_once('<p>Hello target world</p>', 'target', 'https://example.com/a', 'Read')
        self.assertTrue(result.changed)
        self.assertIn('<a href="https://example.com/a">Read</a>', result.html)

    def test_skips_if_url_already_present(self):
        html = '<p><a href="https://example.com/a">Existing</a> target</p>'
        result = insert_link_once(html, 'target', 'https://example.com/a', 'Read')
        self.assertFalse(result.changed)
        self.assertEqual(result.reason, 'link_already_present')

    def test_does_not_replace_inside_existing_link(self):
        html = '<p><a href="https://other.example/">target</a></p>'
        result = insert_link_once(html, 'target', 'https://example.com/a', 'Read')
        self.assertFalse(result.changed)
        self.assertEqual(result.reason, 'target_not_found')

    def test_dry_run_never_patches(self):
        connector = FakeConnector([{"id": "1", "content": "<p>target</p>"}])
        job = BloggerLinkJob(id="j1", name="test", blog_id="b1", target_text="target", link_url="https://example.com", anchor_text="target")
        result = run_link_job(connector, job, dry_run=True, audit=NullAudit())
        self.assertEqual(result.changed, 1)
        self.assertEqual(connector.patched, [])


if __name__ == '__main__':
    unittest.main()
