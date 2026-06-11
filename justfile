# === Fleet-standard ===
bootstrap:
    uv sync

serve:
    uv run python -m ros_mcp

lint:
    ruff check src/ web_sota/backend/

fix:
    ruff check --fix src/ web_sota/backend/

test:
    uv run pytest tests/ -q

e2e:
    cd web_sota && npx playwright test

web:
    pwsh -NoProfile -File ./web_sota/start.ps1

mcpb-pack:
    pwsh -NoProfile -File ./mcpb/pack.ps1

clean:
    pwsh -NoProfile -c "Remove-Item -Recurse -Force -Path dist,.venv,__pycache__ -ErrorAction SilentlyContinue"

# === Repo-specific ===
check-ros:
    pwsh -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 --version } else { Write-Host 'ROS 2 not installed' }"

topics:
    pwsh -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 topic list } else { Write-Host 'ROS 2 not running' }"

nodes:
    pwsh -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 node list } else { Write-Host 'ROS 2 not running' }"

ros-version:
    pwsh -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 --version } else { try { & 'C:\Python3.11\python.exe' -c 'import rclpy; print(\"rclpy available\")' 2>&1 } catch { Write-Host 'ROS 2 not available' } }"