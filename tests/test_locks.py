import os
import tempfile
import time
import unittest
from pathlib import Path

from automation_hub.locks import JobAlreadyRunningError, JobExecutionLock


class LockTests(unittest.TestCase):
    def test_prevents_duplicate_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = JobExecutionLock('job-1', root=root)
            second = JobExecutionLock('job-1', root=root)
            first.acquire()
            try:
                with self.assertRaises(JobAlreadyRunningError):
                    second.acquire()
            finally:
                first.release()
            second.acquire()
            second.release()

    def test_stale_lock_is_recovered(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            lock_path = root / 'job-1.lock'
            root.mkdir(parents=True, exist_ok=True)
            lock_path.write_text('stale', encoding='utf-8')
            old = time.time() - 120
            os.utime(lock_path, (old, old))
            lock = JobExecutionLock('job-1', root=root, stale_seconds=60)
            lock.acquire()
            self.assertTrue(lock.acquired)
            lock.release()


if __name__ == '__main__':
    unittest.main()
