#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A rule-based tokeniser designed for micro-blog (Twitter, at current stage) processing, considering both effectiveness and efficiency.

Features:
1. Twitter specific symbols like hashtags, URLs, mentions are reserved.
2. Emoticons are kept together by grouping all non-word characters together e.g., :), \,,/, More in //http://en.wikipedia.org/wiki/List_of_emoticons
3. Abbreviations like "e.g." are included.
4. Date are included e.g., 2011/11/11.
5. Email address are included e.g., a@b.c
6. Dollar and percentage are included. e.g., 20$, 76%.

Update: 
    2011.08.18: 1) Fix incorrect tokenisation when non-letter chars mingled with @ and #, (@JackieChan) -> ( @JackieChan )
                2) Fix incorrect 'I'm' tokenisation
    
Known Issues:
1. Dot disambiguation in Sep. vs Sep are NOT included, because many calendar month name in Twitter are also at the end of a sentence and there is no robust sentence breaker available.
2. Some ambiguities are hard to resolve, e.g., ":)" is recognised as emoticon in "(He said:)", because there is no available emoticon recogniser available.  

This rule-based method refers to several state-of-the-art tokenisers for Twitter.
1. Ritter, Alan and Clark, Sam and Mausam and Etzioni, Oren, Named Entity Recognition in Tweets: An Experimental Study.
In EMNLP 2011. https://github.com/aritter/twitter_nlp/tarball/master
2. Han, Bo and Baldwin, Timothy. Lexical Normalisation of Short Text Messages: Makn Sens a #twitter. 
In ACL 2011. http://www.aclweb.org/supplementals/P/P11/P11-1038.Software.tar.bz2

@author Bo HAN
@author_email hanb@student.unimelb.edu.au

"""
__version__ = (0,0,1)

__license__ = """Please contact the author."""

import re

class MicroTokeniser():

    def __init__(self):
        self._SPACE = re.compile(r'\s+', re.UNICODE)
        self._URL = re.compile("(https?://|www.)[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#/%=~_|]", re.UNICODE)
        self._WORD = re.compile("[\w-]+$", re.UNICODE)        
        self._NONWORD = re.compile("[^\w]+$", re.UNICODE)
        self._SYMBOL = re.compile("(^[@#][\w]+|\$[0-9,.]*[0-9]|[0-9.]*[0-9][%$]|^([A-Za-z]+\.){2,})", re.UNICODE)
        self._ABBRDICT = {
                "'ve":3,
                "n't":3,
                "i'm":2,
                "I'm":2,
                "'ll":3,
                "'re":3,
                "'s":2
                }
        self._SUFFS = set(self._ABBRDICT.values())

    def _unicodify(self, raw_tweet, encoding='utf-8'):
        """
        Convert all raw_tweets into unicode in utf-8 format
        """
        if isinstance(raw_tweet, basestring):
            if not isinstance(raw_tweet, unicode):
                try:
                    raw_tweet = unicode(raw_tweet, encoding)
                except:
                    # for malformed word encoding, just reserve ascii code
                    raw_tweet = "".join(c for c in raw_tweet if ord(c) < 128)
                    pass
        return raw_tweet

    def _remove_spaces(self, unicode_tweet):
        """
        Remove redundant spaces
        """
        compact_tweet = self._SPACE.sub(' ', unicode_tweet)
        return compact_tweet
    
    def _analyse_specials(self, special_token):
        """
        Process symbols, punctuation conjuctions
        """
        analysed_tokens = []
        m = self._SYMBOL.match(special_token)
        if m:
            s = m.start()
            e = m.end()
            analysed_tokens.append(special_token[:s])
            analysed_tokens.append(special_token[s:e])
            analysed_tokens.append(special_token[e:])
        else:
            s = 0
            e = len(special_token)
            for i in range(s, e):
                cur_char = special_token[i]
                if cur_char.isalnum() or cur_char == "#" or cur_char == "@":
                    s = i
                    break
            analysed_tokens.append(special_token[:s])
            for i in range(e, s, -1):
                if special_token[i - 1].isalnum():
                    e = i
                    break
            analysed_tokens.append(special_token[s:e])
            analysed_tokens.append(special_token[e:])
        return [token for token in analysed_tokens if token]

    def _post_process(self, coarse_tokens):
        """
        Fix abbreviations, like 've, I'm.
        """
        post_tokens = []
        for coarse_token in coarse_tokens:            
            flag = True
            for suffix in self._SUFFS:
                key = coarse_token[-suffix:]
                if key in self._ABBRDICT:
                    offSet = self._ABBRDICT[key]
                    prefix = coarse_token[:-offSet].strip()
                    if prefix:
                        post_tokens.append(prefix)
                    post_tokens.append(coarse_token[-offSet:])
                    flag = False
                    break
            if flag:
                post_tokens.append(coarse_token)
        return post_tokens

    def _re_tokenise(self, compact_tweet):
        """
        Tokenise tweets by regular expressions
        """
        coarse_tokens = compact_tweet.split(' ')
        tokens = []
        for coarse_token in coarse_tokens:
            if self._WORD.match(coarse_token):
                tokens.append(coarse_token)
            elif self._NONWORD.match(coarse_token):
                tokens.append(coarse_token)
            elif self._URL.match(coarse_token):
                tokens.append(coarse_token)
            else:
                acc_tokens = self._analyse_specials(coarse_token)
                post_tokens = self._post_process(acc_tokens)
                tokens.extend(post_tokens)
        return tokens


    def tokenise(self, raw_tweet):
        """        tokenise tweets as a pipeline        """
        tweet_tokens = None

        unicode_tweet = self._unicodify(raw_tweet)
        compact_tweet = self._remove_spaces(unicode_tweet)
        tweet_tokens = self._re_tokenise(compact_tweet)
        tweet_tokens = [token.encode("utf-8") for token in tweet_tokens]

        return tweet_tokens


    def regression_test(self):
        ts_list = [
                "test i appreciate @jkyunah's relentless committment with love. test",
                "test you've don't he's test",
                "test $100, 100$, 200%, 20% test",
                "test http://sch.mp/alDU http://bit.ly/qKbpuj test",
                "test okay. okay? test",
                "test a@b.c test",
                "Ed Joyce (@EnviroEd) is tweeting live",
                "test Ph.D. ph.d e.g. test",
                "test 2011/11/11 2011.11.11 test",
                "I wouldn't do that",
                "I'm so I'am good-bye #a, #a      http://a.com a@b.c e.g.,  100$ and 2011/11/11 so you think? sokay."
                ]
        re_list = [
                "test i appreciate @jkyunah 's relentless committment with love . test", 
                "test you 've do n't he 's test",
                "test $100 , 100$ , 200% , 20% test",
                "test http://sch.mp/alDU http://bit.ly/qKbpuj test",
                "test okay . okay ? test",
                "test a@b.c test",
                "Ed Joyce ( @EnviroEd ) is tweeting live",
                "test Ph.D. ph.d e.g. test",
                "test 2011/11/11 2011.11.11 test",
                "I would n't do that",
                "I 'm so I'am good-bye #a , #a http://a.com a@b.c e.g. , 100$ and 2011/11/11 so you think ? sokay ."
                ]
        case_num = len(ts_list)
        assert(len(re_list) == case_num)
        failed_num = 0
        for i in range(case_num):
            tokens = self.tokenise(ts_list[i])
            tokend_str = " ".join(tokens)
            if tokend_str != re_list[i]:
                print "Regression test failed"
                print tokend_str
                print re_list[i]
                failed_num += 1
        if failed_num == 0:
            print "All test passed"
        else:
            print "%s test failed" % failed_num

if __name__ == "__main__":
    tTokeniser = MicroTokeniser()
    tTokeniser.regression_test()

