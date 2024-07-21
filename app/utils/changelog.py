

def get_change_log():
    with open('changelog.md') as f:
        changes = f.read()
    changes = '### Change log:\n' + changes.replace('#', '####')
    return changes


def get_version():
    with open('changelog.md') as f:
        version = f.read().split('\n')[0]
    return version.replace('#', '').strip()
