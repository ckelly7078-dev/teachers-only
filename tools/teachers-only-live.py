"""Local, approval-gated development launcher for Teachers Only on Windows."""
import getpass
import os
from pathlib import Path
import subprocess
import sys
import time

HOME = Path.home()
REPO = HOME / 'teachers-only-live'
PRIVATE = HOME / 'teachers-only-private'
BRANCH = 'feature/foundation-knowledge-base'
REMOTE = 'https://github.com/ckelly7078-dev/teachers-only.git'
REF = 'refs/remotes/origin/' + BRANCH
POLL = 15

# Git never receives the API key from this launcher.
GIT_ENV = {k: v for k, v in os.environ.items() if k not in ('OPENAI_API_KEY', 'KB_MODEL_KEY')}


def git(*args, check=True):
    return subprocess.run(['git', '--no-pager', *args], cwd=REPO, env=GIT_ENV,
                          text=True, encoding='utf-8', errors='replace',
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=check, timeout=60)


def value(*args):
    return git(*args).stdout.strip()


def clean():
    return not value('status', '--porcelain', '--untracked-files=normal')


def verify_repo():
    if value('branch', '--show-current') != BRANCH:
        raise RuntimeError('Wrong branch. No updates applied.')
    if value('remote', 'get-url', 'origin') != REMOTE:
        raise RuntimeError('Unexpected origin URL. No updates applied.')
    if not clean():
        raise RuntimeError('Working tree has local changes. No updates applied.')


def stop_server(server):
    if server is not None and server.poll() is None:
        server.terminate()
        try:
            server.wait(timeout=8)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=8)


def start_server(env):
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    server = subprocess.Popen([sys.executable, '-m', 'foundation.server', '--port', '8080'],
                              cwd=REPO, env=env, creationflags=flags)
    time.sleep(1)
    if server.poll() is not None:
        raise RuntimeError('Server exited. Check the error above (port 8080 may already be in use).')
    print('Open http://127.0.0.1:8080/foundation/web/index.html', flush=True)
    return server


def main():
    server = None
    try:
        if not REPO.is_dir() or not (PRIVATE / 'foundation.sqlite').is_file() or not (PRIVATE / 'users.json').is_file():
            raise RuntimeError('Expected cloned repository, database or teacher login file is missing.')
        verify_repo()
        print('Current checked-out commit:')
        print(value('log', '-1', '--format=%h %s'))
        if input('Start this checked-out code with your API key? [y/N] ').strip().lower() != 'y':
            return
        key = getpass.getpass('OpenAI API key (hidden, Enter for local-only mode): ').strip()
        env = dict(GIT_ENV, KB_DB=str(PRIVATE / 'foundation.sqlite'),
                   KB_USERS=str(PRIVATE / 'users.json'), KB_STUDIO_MODEL='gpt-4.1',
                   PYTHONDONTWRITEBYTECODE='1')
        if key:
            env['OPENAI_API_KEY'] = key
        del key
        server = start_server(env)
        print('Checking GitHub every 15 seconds. Ctrl+C stops the launcher.\n'
              'New code is never applied or executed without your approval.', flush=True)
        declined = None
        while True:
            time.sleep(POLL)
            if server.poll() is not None:
                raise RuntimeError('Server stopped. Check the messages above.')
            try:
                verify_repo()
                git('fetch', '--no-tags', 'origin', BRANCH)
                current = value('rev-parse', 'HEAD')
                target = value('rev-parse', REF)
                if target == current or target == declined:
                    continue
                if git('merge-base', '--is-ancestor', current, target, check=False).returncode != 0:
                    print('Update is not a fast-forward. Stopping automatic checks to protect local code.')
                    break
                print('\nGitHub update available:')
                print(value('log', '--oneline', current + '..' + target))
                print(value('diff', '--stat', '--no-ext-diff', '--no-textconv', current, target))
                print('Review: https://github.com/ckelly7078-dev/teachers-only/compare/' + current + '...' + target)
                choice = input('Apply this exact update and restart? [y/N, d=show diff] ').strip().lower()
                if choice == 'd':
                    print(value('diff', '--no-ext-diff', '--no-textconv', current, target))
                    choice = input('Apply this exact update and restart? [y/N] ').strip().lower()
                if choice != 'y':
                    declined = target
                    print('Update skipped. The current website remains running.')
                    continue
                verify_repo()
                if value('rev-parse', 'HEAD') != current:
                    raise RuntimeError('Local commit changed during review. No update applied.')
                stop_server(server)
                server = None
                git('merge', '--ff-only', target)
                print('Approved update applied. Restarting server...', flush=True)
                server = start_server(env)
                print('Refresh Firefox to see the changes.', flush=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                print('Git check/update failed:', getattr(exc, 'stderr', None) or str(exc), flush=True)
                if server is None:
                    raise RuntimeError('Update interrupted after stopping the server. Inspect git status before restarting.') from exc
        # Keep the approved server running when update checks are disabled.
        print('Server still running; Ctrl+C to stop.')
        server.wait()
    except KeyboardInterrupt:
        print('\nStopping local server.')
    except (RuntimeError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print('\nLauncher stopped:', exc, file=sys.stderr)
        return 1
    finally:
        stop_server(server)
    return 0


if __name__ == '__main__':
    sys.exit(main())
