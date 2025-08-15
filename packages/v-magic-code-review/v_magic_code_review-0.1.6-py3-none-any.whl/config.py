import os

from util import get_cookie_from_browser


class GitlabConfig:
    PROJECT_ID = 311
    HOST = os.environ['GITLAB_HOST']
    TOKEN = os.environ['GITLAB_TOKEN']
    DIFF_EXCLUDE_EXT = {'.ttf', '.woff', '.woff2', '.eot', '.otf', '.svg', '.png', '.jpg', '.jpeg', '.gif'}
    DIFF_EXCLUDE_PATH = {'thirdparty'}


class JiraConfig:
    HOST = os.environ['JIRA_HOST']
    TOKEN = os.environ['JIRA_TOKEN']


class JiraField:
    SUMMARY = 'summary'
    AC = 'customfield_13530'
    DESCRIPTION = 'description'
    COMMENT = 'comment'


class ConfluenceConfig:
    HOST = os.environ['CONFLUENCE_HOST']
    TOKEN = os.environ['CONFLUENCE_TOKEN']


class GeminiConfig:
    browser_name = os.environ.get('BROWSER_NAME') or 'chrome'
    secure_1psid, secure_1psidts = get_cookie_from_browser(browser_name)
    COOKIE_SECURE_1PSID = secure_1psid if secure_1psid else os.environ['GEMINI_COOKIE_SECURE_1PSID']
    COOKIE_SECURE_1PSIDTS = secure_1psidts if secure_1psidts else os.environ['GEMINI_COOKIE_SECURE_1PSIDTS']
