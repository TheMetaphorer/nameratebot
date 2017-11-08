# -*- coding: utf-8 -*-

import praw
import json
import time
import sys
import re

from os import stat
from datetime import datetime



class NameRateBot(praw.Reddit):
    _rating_keywords = {
        'cool': 3,
        'nice': 4,
        'good': 5,
        'great': 7,
        'awesome': 9,
        'bad': -3,
        'terrible': -5,
        'horrible': -6,
        'shit': -7,
        'garbage': -8,
    }
    stats_dictionary = {}
    pres = [
        'what a',
        'you have a',
        'such a',
        'quite the',
    ]
    qualifiers = []
    for keyword in _rating_keywords.keys():
        for pre in pres:
            qualifiers.append('{0} {1} username'.format(pre, keyword))
            qualifiers.append('{0} {1} name'.format(pre, keyword))
            qualifiers.append('{0} username'.format(keyword))
            qualifiers.append('{0} name'.format(keyword))

    def _generate_log_string(self, type, msg):
        current_time = datetime.now()
        return "[{0} {1}: {2}]".format(current_time, type, msg)

    def _update_stats(self, user, score_delta):
        """

        :param user:
        :param score_delta:
        :param json_file:
        :return:


        """
        if user.name not in self.stats_dictionary.keys():
            self.stats_dictionary[user.name] = 64.0
            score_delta = score_delta * ((100 - self.stats_dictionary[user.name]) / 100)
            self.stats_dictionary[user.name] += score_delta
        else:
            score_delta = score_delta * ((100 - self.stats_dictionary[user.name]) / 100)
            self.stats_dictionary[user.name] += score_delta

        print self._generate_log_string('INFO', '{0} points earned for u/{1}'.format(score_delta, user.name))

    def run(self, subreddit, json_file):
        try:
            if not stat(json_file).st_size == 0:
                tmp = open(json_file, 'r')
                self.stats_dictionary = json.loads(tmp.read())
                tmp.close()
            sub = self.subreddit(subreddit)
            print self._generate_log_string('INFO', 'Scanning subreddit r/{}'.format(sub))
            while True:
                comments_processed = 0
                for comment in sub.stream.comments():
                    comments_processed += 1
                    if comments_processed % 500 == 0:
                        print self._generate_log_string('INFO', '{0} comments processed.'.format(comments_processed))
                    comment_as_string = re.sub(r'[^\w\s]+', '', comment.body)
                    for qualifier in self.qualifiers:
                        if comment_as_string == qualifier:
                            for keyword in self._rating_keywords.keys():
                                if keyword in comment_as_string:
                                    self._update_stats(comment.parent().author, self._rating_keywords[keyword])
                            print self._generate_log_string('INFO',
                                                            'Comment meeting requirements found. Statistics updated.')
                            print self._generate_log_string('INFO', '{0}'.format(comment.body))
                            comment.reply("""You have rated u/{0}'s name! They currently have a score of {1:.2f} out of 100.
                            (This bot is only testing names within the scope of r/{2}) 
                            ^^^bleep ^^^bloop ^^^im ^^^a ^^^bot.""".format(
                                comment.parent().author.name, self.stats_dictionary[comment.parent().author.name],
                                sub))
                            print self._generate_log_string('INFO', 'Reply to u/{0} generated.'.format(comment.author.name))
                            break

        except KeyboardInterrupt:
            print self._generate_log_string('INFO', 'Ctrl-C caught. Program suspended.')
            print self._generate_log_string('INFO', '{0} comments processed.'.format(comments_processed))
            try:
                print self._generate_log_string('INFO', 'Sleeping for 10 seconds. Ctrl-C again to continue, press nothing to terminate.')
                time.sleep(10)
                print self._generate_log_string('INFO', 'Exiting with 0 status.')
                f=open(json_file, 'w+')
                f.write(json.dumps(self.stats_dictionary))
                f.close()
                sys.exit(0)
            except KeyboardInterrupt:
                self.run(subreddit, json_file)

        except UnicodeEncodeError as e:
            print self._generate_log_string('WARNING', 'Unicode encode error: {0}'.format(str(e)))
            print self._generate_log_string('WARNING', 'Trying again...')
            self.run(subreddit, json_file)

        except Exception as e:
            print self._generate_log_string('FATAL', 'An exception has been caught. {0}'.format(str(e)))
            print self._generate_log_string('WARNING', 'Exiting program with -1 status.')
            sys.exit(-1)
