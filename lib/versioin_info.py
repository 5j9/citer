import subprocess
from pathlib import Path

from app import ALLOW_ALL_ORIGINS, BytesTuple, StartResponse, logger


def get_git_info() -> tuple[str, str, str]:
    """Retrieves the latest commit hash and date using git."""
    # Determine the directory of the current script
    repo_dir = Path(__file__).parent

    commit_hash = 'N/A'
    commit_date = 'N/A'
    commit_subject = 'N/A'

    try:
        # Get hash (%H), committer date (%ci), and subject (%s)
        command = ['git', 'log', '-1', '--format=%H%n%ci%n%s']
        result = subprocess.run(
            command,
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 3:
                commit_hash = lines[0].strip()
                commit_date = lines[1].strip()
                commit_subject = lines[2].strip()
            elif len(lines) == 2:
                commit_hash = lines[0].strip()
                commit_date = lines[1].strip()
            elif len(lines) == 1:
                commit_hash = lines[0].strip()

    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        TimeoutError,
        Exception,
    ) as e:
        commit_hash = 'ERROR'
        commit_date = f'{type(e).__name__}'
        commit_subject = (
            'Check if git is installed and if this is a repository.'
        )
        logger.error(f'Git info retrieval failed: {e}')

    return commit_hash, commit_date, commit_subject


def version_info(start_response: StartResponse, environ: dict) -> BytesTuple:
    """
    Handles the /version path, displaying git commit information.
    """
    commit_hash, commit_date, commit_subject = get_git_info()

    status = '200 OK'
    # Use simple HTML headers for this endpoint
    headers = [
        ('Content-Type', 'text/html; charset=UTF-8'),
        ALLOW_ALL_ORIGINS,
    ]

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Application Version</title>
        <style>
            body {{
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
                margin: 20px;
                background-color: #f0f4f8;
                color: #1e293b;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                background: #ffffff;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #0f172a;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 10px;
                margin-top: 0;
            }}
            p {{
                margin: 10px 0;
                line-height: 1.6;
            }}
            .label {{
                font-weight: bold;
                color: #475569;
                display: inline-block;
                width: 130px;
            }}
            .value {{
                color: #0f172a;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Application Version Info</h1>
            <p><span class="label">Latest Commit:</span> <span class="value">{commit_hash}</span></p>
            <p><span class="label">Commit Date:</span> <span class="value">{commit_date}</span></p>
            <p><span class="label">Commit Subject:</span> <span class="value">{commit_subject}</span></p>
            <p><span class="label">Source Path:</span> <span class="value">{Path(__file__).parent.resolve()}</span></p>
            <p style="margin-top: 20px; font-size: 0.85em; color: #64748b;">
                Served by: {environ.get('SERVER_SOFTWARE', 'Unknown WSGI Server')}
            </p>
        </div>
    </body>
    </html>
    """
    response_body = html_content.encode('utf-8')

    start_response(status, headers)
    return (response_body,)
