"""Launcher lifecycle contract without automating the user's Windows desktop."""
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import dashboard_entry

class LauncherTests(unittest.TestCase):
    def test_ready_opens_once_and_stop_terminates_owned_process(self):
        callbacks = []
        buttons = {}
        window = MagicMock()
        window.after.side_effect = lambda delay, callback: callbacks.append(callback)
        def button(parent, **kwargs):
            state = dict(kwargs)
            widget = MagicMock()
            widget.configure.side_effect = lambda **updates: state.update(updates)
            widget.__getitem__.side_effect = lambda key: state[key]
            buttons[kwargs['text']] = (state, widget)
            return widget
        def mainloop():
            callbacks.pop(0)()  # ready -> browser
            callbacks.pop(0)()  # already ready -> no second browser
            buttons['Zakończ program'][0]['command']()
        window.mainloop.side_effect = mainloop
        child = MagicMock()
        child.poll.return_value = None
        response = MagicMock()
        response.__enter__.return_value.status = 200
        response.__enter__.return_value.read.return_value = b'ok'
        with tempfile.TemporaryDirectory() as folder, \
             patch.dict('os.environ', {'LOCALAPPDATA': folder}), \
             patch('sys.argv', ['dashboard_entry.py']), \
             patch('tkinter.Tk', return_value=window), \
             patch('tkinter.StringVar'), patch('tkinter.ttk.Label'), \
             patch('tkinter.ttk.Button', side_effect=button), \
             patch('subprocess.Popen', return_value=child) as popen, \
             patch('urllib.request.urlopen', return_value=response), \
             patch('webbrowser.open', return_value=True) as browser:
            dashboard_entry.main()
        self.assertEqual(browser.call_count, 1)
        child.terminate.assert_called_once()
        child.wait.assert_called_once()
        window.destroy.assert_called_once()
        self.assertIn('--serve', popen.call_args.args[0])
        self.assertIn('--log', popen.call_args.args[0])
        self.assertTrue(browser.call_args.args[0].startswith('http://127.0.0.1:'))
