https://powcoder.com
代写代考加微信 powcoder
Assignment Project Exam Help
Add WeChat powcoder
import os
import ast
import unittest
from inspect import getsource
from random import choice, randint, seed
from string import ascii_lowercase
import sys

import specialtopics as ST

randomSeed = 0  # <------------- modify the random behaviour by changing the seed

scriptDirectory = os.path.dirname(__file__)
allowed_modules = ["csv", "probability", "numpy", "re"]
seed(randomSeed)

#############################################
# Helper functions used in the test.


def assert_no_loops(s, f):
    f_ast = ast.parse(getsource(f))
    for node in ast.walk(f_ast):
        if isinstance(node, ast.For):
            s.fail(f"function {f.__name__} uses a for loop.")
        if isinstance(node, ast.While):
            s.fail(f"function {f.__name__} uses a while loop.")


def randomPart():
    length = randint(1, 5)
    return "".join(choice(ascii_lowercase) for _ in range(length))


def randomMailbox():
    return ".".join(randomPart() for _ in range(randint(1, 3)))


def randomDomain():
    return ".".join(randomPart() for _ in range(randint(1, 3))) + choice(
        [".com", ".org"]
    )


def randomUsername():
    return "@" + randomMailbox() + "@" + randomDomain()


def randomChannel():
    length = randint(1, 8)
    return (
        "#"
        + choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        + "".join(
            choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            for _ in range(length)
        )
    )


def runReChatParser(correctTranscript):
    state = None
    transcript = []
    for message, _ in correctTranscript:
        r, state = ST.reChatParseCommand(message, state)
        transcript.append((message, r))

    return transcript


#############################################
# Tests begin here
#
# The tests are all constructed around a transcript.
# A transcript is a list of pairs like so:
# ( <message>, <expected output> )
# Your function is tested by passing it <message> from each
# pair in the transcript and comparing the result against
# the expected output.
#
# In some cases the transcript includes randomised text.  You can
# change the random seed above to test different values.
#


class TestFSA(unittest.TestCase):
    def test_no_loops(self):
        """No loops"""
        assert_no_loops(self, ST.reChatParseCommand)

    def test_simple(self):
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)

    def test_command(self):
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\list users", {"action": "list", "param": "users"}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)

    def test_commands_more(self):
        channel = randomChannel()
        user = randomUsername()
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\list users", {"action": "list", "param": "users"}),
            ("\\join " + channel, {"action": "join", "channel": channel}),
            ("\\leave", {"action": "leaveChannel", "channel": channel}),
            ("\\dm " + user, {"action": "dm", "user": user}),
            ("\\leave", {"action": "leaveDM", "user": user}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)

    def test_channel(self):
        channel = randomChannel()
        channel2 = randomChannel()
        user = randomUsername()
        user2 = randomUsername()
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\join " + channel, {"action": "join", "channel": channel}),
            ("\\read", {"action": "readChannel", "channel": channel}),
            (
                "Hello " + user,
                {
                    "action": "postChannel",
                    "channel": channel,
                    "message": "Hello " + user,
                    "mentions": {user},
                },
            ),
            ("\\leave", {"action": "leaveChannel", "channel": channel}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\join " + channel2, {"action": "join", "channel": channel2}),
            ("\\read", {"action": "readChannel", "channel": channel2}),
            (
                "Hello " + user2,
                {
                    "action": "postChannel",
                    "channel": channel2,
                    "message": "Hello " + user2,
                    "mentions": {user2},
                },
            ),
            ("\\leave", {"action": "leaveChannel", "channel": channel2}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)

    def test_dm(self):
        user = randomUsername()
        user2 = randomUsername()
        user3 = randomUsername()
        user4 = randomUsername()
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\dm " + user, {"action": "dm", "user": user}),
            ("\\read", {"action": "readDM", "user": user}),
            (
                "Hello " + user2,
                {
                    "action": "postDM",
                    "user": user,
                    "message": "Hello " + user2,
                    "mentions": {user2},
                },
            ),
            ("\\leave", {"action": "leaveDM", "user": user}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\dm " + user3, {"action": "dm", "user": user3}),
            ("\\read", {"action": "readDM", "user": user3}),
            (
                "Hello " + user4 + " " + user2,
                {
                    "action": "postDM",
                    "user": user3,
                    "message": "Hello " + user4 + " " + user2,
                    "mentions": {user4, user2},
                },
            ),
            ("\\leave", {"action": "leaveDM", "user": user3}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)

    def test_command_errors(self):
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\list something", {"error": "Invalid command"}),
            ("\\list users", {"action": "list", "param": "users"}),
            ("\\join something", {"error": "Invalid command"}),
            ("\\dm someone", {"error": "Invalid command"}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)

    def test_channel_errors(self):
        channel = randomChannel()
        channel2 = randomChannel()
        user = randomUsername()
        user2 = randomUsername()
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\join " + randomPart(), {"error": "Invalid command"}),
            ("\\join " + channel, {"action": "join", "channel": channel}),
            ("\dm " + randomUsername(), {"error": "Invalid command"}),
            ("\\nothing", {"error": "Invalid command"}),
            ("\\read", {"action": "readChannel", "channel": channel}),
            (
                "Hello " + user,
                {
                    "action": "postChannel",
                    "channel": channel,
                    "message": "Hello " + user,
                    "mentions": {user},
                },
            ),
            ("\\" + randomPart(), {"error": "Invalid command"}),
            ("\\leave", {"action": "leaveChannel", "channel": channel}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\join " + randomPart(), {"error": "Invalid command"}),
            ("\\join " + channel2, {"action": "join", "channel": channel2}),
            ("\\read", {"action": "readChannel", "channel": channel2}),
            (
                "Hello " + user2,
                {
                    "action": "postChannel",
                    "channel": channel2,
                    "message": "Hello " + user2,
                    "mentions": {user2},
                },
            ),
            ("\\leave", {"action": "leaveChannel", "channel": channel2}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)

    def test_dm_errors(self):
        user = randomUsername()
        user2 = randomUsername()
        user3 = randomUsername()
        user4 = randomUsername()
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\join " + randomPart(), {"error": "Invalid command"}),
            ("\\dm " + user, {"action": "dm", "user": user}),
            ("\\join " + randomChannel(), {"error": "Invalid command"}),
            ("\\something", {"error": "Invalid command"}),
            ("\\read", {"action": "readDM", "user": user}),
            (
                "Hello " + user2,
                {
                    "action": "postDM",
                    "user": user,
                    "message": "Hello " + user2,
                    "mentions": {user2},
                },
            ),
            ("\\" + randomPart(), {"error": "Invalid command"}),
            ("\\leave", {"action": "leaveDM", "user": user}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\dm " + user3, {"action": "dm", "user": user3}),
            ("\\" + randomPart(), {"error": "Invalid command"}),
            ("\\read", {"action": "readDM", "user": user3}),
            (
                "Hello " + user4 + " " + user2,
                {
                    "action": "postDM",
                    "user": user3,
                    "message": "Hello " + user4 + " " + user2,
                    "mentions": {user4, user2},
                },
            ),
            ("\\" + randomPart(), {"error": "Invalid command"}),
            ("\\leave", {"action": "leaveDM", "user": user3}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)

    def test_combined_errors(self):
        channel = randomChannel()
        channel2 = randomChannel()
        user = randomUsername()
        user2 = randomUsername()
        user3 = randomUsername()
        user4 = randomUsername()
        correctTranscript = [
            ("", {"action": "greeting"}),
            ("\\dm " + user, {"action": "dm", "user": user}),
            ("\\something", {"error": "Invalid command"}),
            ("\\read", {"action": "readDM", "user": user}),
            (
                "Hello " + user2,
                {
                    "action": "postDM",
                    "user": user,
                    "message": "Hello " + user2,
                    "mentions": {user2},
                },
            ),
            ("\\" + randomPart(), {"error": "Invalid command"}),
            ("\\leave", {"action": "leaveDM", "user": user}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\dm " + user3, {"action": "dm", "user": user3}),
            ("\\" + randomPart(), {"error": "Invalid command"}),
            ("\\read", {"action": "readDM", "user": user3}),
            (
                "Hello " + user4 + " " + user2,
                {
                    "action": "postDM",
                    "user": user3,
                    "message": "Hello " + user4 + " " + user2,
                    "mentions": {user4, user2},
                },
            ),
            ("\\" + randomPart(), {"error": "Invalid command"}),
            ("\\leave", {"action": "leaveDM", "user": user3}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\join " + channel, {"action": "join", "channel": channel}),
            ("\\nothing", {"error": "Invalid command"}),
            ("\\read", {"action": "readChannel", "channel": channel}),
            (
                "Hello " + user,
                {
                    "action": "postChannel",
                    "channel": channel,
                    "message": "Hello " + user,
                    "mentions": {user},
                },
            ),
            ("\\" + randomPart(), {"error": "Invalid command"}),
            ("\\leave", {"action": "leaveChannel", "channel": channel}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\join " + channel2, {"action": "join", "channel": channel2}),
            ("\\read", {"action": "readChannel", "channel": channel2}),
            (
                "Hello " + user2,
                {
                    "action": "postChannel",
                    "channel": channel2,
                    "message": "Hello " + user2,
                    "mentions": {user2},
                },
            ),
            ("\\leave", {"action": "leaveChannel", "channel": channel2}),
            ("\\list channels", {"action": "list", "param": "channels"}),
            ("\\quit", {"action": "quit"}),
        ]
        transcript = runReChatParser(correctTranscript)
        self.assertEqual(correctTranscript, transcript)


# This test does not count for any marks.  It just helps to ensure
# that your code will run on the test system.
class TestImportedModules(unittest.TestCase):
    def test_modules(self):
        with open("specialtopics.py", "r") as f:
            file_raw = f.read()
            player_ast = ast.parse(file_raw)

        def imported_modules():
            for node in ast.walk(player_ast):
                if isinstance(node, ast.Import):
                    yield from (x.name.split(".")[0] for x in node.names)
                if isinstance(node, ast.ImportFrom) and node.level is None:
                    yield node.module.split(".")[0]

        for module in imported_modules():
            if module not in allowed_modules:
                self.fail(f"module {module} imported by submission but not allowed.")


if __name__ == "__main__":
    print(f"Python version {sys.version}")
    unittest.main(argv=["-b"])
