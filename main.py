import uvicorn
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the API Server with optional port")
    parser.add_argument("--port", type=int, default=18889, help="Port to run the server on (default: 18889)")
    
    args, unknown_args = parser.parse_known_args()

    sys.argv = ['main.py'] + unknown_args

    uvicorn.run("api_module:app", host="0.0.0.0", port=args.port, reload=False)