set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

import 'scripts/just/fleet.just'

# === Fleet-standard ===
    powershell.exe -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 --version } else { try { & 'C:\Python3.11\python.exe' -c 'import rclpy; print(\"rclpy available\")' 2>&1 } catch { Write-Host 'ROS 2 not available' } }"
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
    powershell.exe -NoProfile -File ./web_sota/start.ps1

clean:
    powershell.exe -NoProfile -c "Remove-Item -Recurse -Force -Path dist,.venv,__pycache__ -ErrorAction SilentlyContinue"

# === Repo-specific ===
check-ros:
    powershell.exe -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 --version } else { Write-Host 'ROS 2 not installed' }"

topics:
    powershell.exe -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 topic list } else { Write-Host 'ROS 2 not running' }"

nodes:
    powershell.exe -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 node list } else { Write-Host 'ROS 2 not running' }"

ros-version:
    powershell.exe -NoProfile -c "if (Get-Command ros2 -ErrorAction SilentlyContinue) { ros2 --version } else { try { & 'C:\Python3.11\python.exe' -c 'import rclpy; print(\"rclpy available\")' 2>&1 } catch { Write-Host 'ROS 2 not available' } }"
