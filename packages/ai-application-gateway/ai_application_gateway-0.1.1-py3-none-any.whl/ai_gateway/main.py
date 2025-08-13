import uvicorn
import argparse

from config import config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=config.listen_host, help="Host to listen on")
    parser.add_argument(
        "--port", type=int, default=config.listen_port, help="Port to listen on"
    )
    parser.add_argument(
        "--debug", type=bool, default=config.debug, help="Enable or disable debug mode"
    )
    parser.add_argument(
        "--is_reload", type=bool, default=config.is_reload, help="Enable or disable reload mode"
    )
    args = parser.parse_args()

    uvicorn.run(
        "ai_gateway.core.init_app:app",
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info",
        reload=args.is_reload,
        lifespan="on",
        loop="asyncio",
        workers=config.workers,
    )

if __name__ == "__main__":
    main()

