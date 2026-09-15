import unittest
from unittest.mock import patch

from automation_hub.models import BloggerLinkJob, ScheduleSpec
from automation_hub.scheduler import SchedulerError, build_create_args, task_name, validate_time


class SchedulerTests(unittest.TestCase):
    def test_daily_args_are_fixed_interactive_limited_runner(self):
        job = BloggerLinkJob(id='job-1', name='x', blog_id='b', target_text='x', link_url='https://example.com', anchor_text='x', schedule=ScheduleSpec(kind='daily', time='08:30'))
        with patch('automation_hub.scheduler.sys.executable', r'C:\Python\python.exe'):
            args = build_create_args(job)
        self.assertEqual(args[0], 'schtasks')
        self.assertIn('/RL', args)
        self.assertIn('LIMITED', args)
        self.assertIn('/IT', args)
        command = args[args.index('/TR') + 1]
        self.assertIn('--run-job', command)
        self.assertNotIn('powershell', command.lower())
        self.assertNotIn('cmd.exe', command.lower())

    def test_weekly_requires_day(self):
        job = BloggerLinkJob(id='j', name='x', blog_id='b', target_text='x', link_url='https://example.com', anchor_text='x', schedule=ScheduleSpec(kind='weekly', time='08:00', weekdays=[]))
        with self.assertRaises(SchedulerError):
            build_create_args(job)

    def test_time_validation(self):
        self.assertEqual(validate_time('23:59'), '23:59')
        with self.assertRaises(SchedulerError):
            validate_time('24:00')

    def test_task_name_sanitized(self):
        self.assertEqual(task_name('a b/c'), 'WorkflowAutomationHub_a_b_c')


if __name__ == '__main__':
    unittest.main()
