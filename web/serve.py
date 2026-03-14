#!/usr/bin/env python3
"""Start the Storywizard web server."""

import uvicorn


def main():
    print("Starting Storywizard web server...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run("web.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
