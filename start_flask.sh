#!/bin/bash
echo "Starting Flask (without reloader to avoid routing issues)..."
python3 -c "from app import app; app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)"
